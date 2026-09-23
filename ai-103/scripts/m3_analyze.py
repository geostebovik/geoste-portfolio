#!/usr/bin/env python3
"""
M3 -- IIP Document Intelligence: submit-and-poll pipeline for Azure Content Understanding.

Pipeline (mirrors the proven manual commands in iip-cli-runbook.md, Google
Drive > IIP folder, "Submit an analyze call" / "Poll for the analyze result"
sections -- full debugging history behind these lives in MASTER-REFERENCE
Section 4.12):

    endpoint -> Entra ID token -> user-delegation SAS or base64 -> POST :analyze
    -> poll Operation-Location -> save structured result

Design decisions:
  - Config storage: .env (git-ignored) holds NON-secret resource names only
    (account name, resource group, storage account, analyzer id, api version).
  - Auth: KEYLESS since 2026-09-23 (M3's migration, the last piece of M10).
    Both the analyze call and the result poll send an Entra ID bearer token
    for https://cognitiveservices.azure.com/.default -- the scope the
    Content Understanding REST reference (2025-11-01) names, and the one M10
    proved on Vision Read and the Evaluation SDK. Role: Foundry User.
    CORRECTED 2026-09-23: this bullet used to say Entra ID "doesn't apply
    cleanly here because ... there is no managed identity for a laptop". That
    conflated the two. A managed identity is one KIND of Entra ID principal;
    on a laptop, DefaultAzureCredential signs in as the developer through
    `az login`, which is how every other script here already works.
  - --blob uses a USER-DELEGATION SAS (decision (A), Gerard, 2026-09-23):
    the same read-only, 30-minute URL as before, but signed with the caller's
    Entra ID credentials instead of the storage account key. Needs Storage
    Blob Delegator (to get the delegation key) and a blob data role that
    covers read -- Gerard holds both on stiipdevwus01 (RBAC model row 3 and
    the Delegator row). Microsoft recommends user-delegation SAS whenever a
    SAS is used. Content Understanding fetching the blob with the Foundry
    account's own identity was considered and ruled out: no Microsoft
    documentation shows it for this API; every example is a SAS or public URL.
  - get_subscription_key() and get_storage_key() were REMOVED 2026-09-23,
    after both paths were verified live keyless (results 20260923-121256 and
    -121335: all 21 non-generative extracted values identical to the July 27
    key-based run). No function in this repo reads an account key any more.

Request body verified against iip-cli-runbook.md's actual working curl
commands (not reconstructed/guessed): the input is wrapped in an "inputs"
array --
    {"inputs": [{"url": "<sas-url>"}]}
    {"inputs": [{"data": "<base64>", "mimeType": "application/pdf"}]}
"""

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


def run_az(args: list[str]) -> str:
    """Run an Azure CLI command, return stdout stripped. Raises RuntimeError on failure.

    Every value this script needs from Azure is fetched this way, on the spot,
    so there's no cached/stale credential sitting in a file. Requires `az login`
    to already be done in whatever shell/environment runs this script.
    """
    az_cmd = shutil.which("az")
    if az_cmd is None:
        raise RuntimeError("`az` not found on PATH — is Azure CLI installed?")
    result = subprocess.run(
        [az_cmd, *args, "-o", "tsv"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"az {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def get_endpoint(account: str, resource_group: str) -> str:
    """The Foundry account's endpoint: the AIF_ENDPOINT setting if present,
    otherwise a live `az` lookup.

    ADDED 2026-09-23 for M11 (m11-prep.md, "the M7 code assumes a developer's
    laptop"). A Function has no Azure CLI, and m7_evaluator_tool.py calls this
    at MODULE SCOPE -- so without the setting, merely importing the evaluator
    inside a Function would fail while the host loads the code. With it set,
    no subprocess runs at all. Laptop runs without the setting are unchanged.

    The value is the custom-subdomain endpoint (aif-iip-dev-wus-01 -- the
    project's naming exception, pinned in infrastructure/iip/dev.bicepparam).
    Nothing here verifies a configured value against the live account; a
    wrong value surfaces as a DNS or 401 error on the first call.
    """
    configured = os.environ.get("AIF_ENDPOINT", "").strip()
    if configured:
        return configured.rstrip("/")
    # Matches: az cognitiveservices account show --name <account>
    #   --resource-group <rg> --query properties.endpoint -o tsv
    return run_az([
        "cognitiveservices", "account", "show",
        "--name", account,
        "--resource-group", resource_group,
        "--query", "properties.endpoint",
    ]).rstrip("/")


def build_token_provider(scope: str = "https://cognitiveservices.azure.com/.default"):
    """Entra ID bearer-token provider -- the keyless replacement for
    get_subscription_key(), added for M10 (2026-09-22).

    Returns a CALLABLE, not a token. The OpenAI SDK invokes it before each
    request, so expiry and refresh are handled for us. That matters here: a
    token lives ~60-90 minutes and the M7 acceptance test runs ~95, so a
    fetched-once token string would expire mid-run.

    SCOPE. cognitiveservices.azure.com is the classic Azure OpenAI /
    AI Services audience, verified working 2026-09-22 against Vision Read
    and the Evaluation SDK (probe_keyless_vision.py, probe_keyless_eval.py).
    Microsoft's newer Foundry docs name a DIFFERENT audience,
    ai.azure.com/.default, for the /openai/v1/ route -- which is the route
    m5_index.build_embedding_client() uses. Parameterised rather than
    hardcoded for exactly that reason; do not assume one covers the other.

    ROLE. Foundry User carries this. Its dataActions are the wildcard
    Microsoft.CognitiveServices/* (role definition
    53ca6127-db72-4b80-b1b0-d745d6d5456d, read 2026-09-22), which is why it
    covers Vision and the Evaluation SDK as well as chat. Note the same role
    also grants accounts/listkeys/action -- keyless code does not by itself
    make keys unavailable; disableLocalAuth does.

    get_subscription_key() was kept as a fallback until the acceptance test
    passed on this path (2026-09-22), and removed 2026-09-23 in its own
    commit. Removing a fallback at the moment it is most likely to be needed
    is how a migration becomes an outage.
    """
    return get_bearer_token_provider(DefaultAzureCredential(), scope)


def get_sas_url(storage_account: str, container: str, blob: str, minutes: int = 30) -> str:
    """Read-only USER-DELEGATION SAS for one blob -- no account key involved.

    CHANGED 2026-09-23 from an account-key SAS. `--as-user` signs the SAS with a
    user delegation key obtained with the caller's Entra ID credentials, and
    Azure CLI requires `--auth-mode login` with it. A user delegation key is
    valid for at most 7 days, so a longer --expiry would be silently capped;
    30 minutes is far inside that. Revocation: revoking the user's delegation
    keys invalidates every SAS signed with them.
    """
    # Matches iip-cli-runbook.md "Generate a read-only SAS URL for a blob"
    # (keyless version, 2026-09-23).
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%MZ")
    return run_az([
        "storage", "blob", "generate-sas",
        "--account-name", storage_account,
        "--container-name", container,
        "--name", blob,
        "--permissions", "r",
        "--expiry", expiry,
        "--https-only",
        "--full-uri",
        "--as-user",
        "--auth-mode", "login",
    ])


def build_input_from_file(path: Path) -> dict:
    """Base64 path -- for a local file with no blob step. Skips SAS entirely.

    Matches iip-cli-runbook.md's base64 example exactly: {"data": ..., "mimeType": ...}
    -- no "name" field.
    """
    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "application/octet-stream"
    data_b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"data": data_b64, "mimeType": mime_type}


def build_input_from_sas(sas_url: str) -> dict:
    """SAS path -- for a document already sitting in blob storage."""
    return {"url": sas_url}


def _auth_header(token_provider) -> dict:
    # Called per request rather than once: a bearer token lives ~60-90 minutes,
    # and the provider refreshes it when needed. The poll loop is short (300 s
    # cap), but calling per request keeps both functions correct if it grows.
    return {"Authorization": f"Bearer {token_provider()}"}


def submit_analyze(endpoint: str, token_provider, analyzer_id: str, api_version: str, analysis_input: dict) -> str:
    # Matches: POST {endpoint}contentunderstanding/analyzers/{analyzerId}:analyze
    #   ?api-version=2025-11-01
    # Body shape confirmed from iip-cli-runbook.md: the input dict is wrapped
    # in an "inputs" LIST, not sent bare -- {"inputs": [{...}]}.
    url = f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}:analyze"
    resp = requests.post(
        url,
        params={"api-version": api_version},
        headers={
            **_auth_header(token_provider),
            "Content-Type": "application/json",
        },
        json={"inputs": [analysis_input]},
        timeout=60,
    )
    resp.raise_for_status()  # 4xx/5xx -> raises with the real error body
    op_location = resp.headers.get("Operation-Location")
    if not op_location:
        raise RuntimeError(
            f"202 response but no Operation-Location header. "
            f"Status {resp.status_code}, body: {resp.text[:500]}"
        )
    return op_location


def poll_result(op_location: str, token_provider, interval_s: int = 2, timeout_s: int = 300) -> dict:
    # iip-cli-runbook.md: "poll every 1-2 seconds ... copy the real header
    # value" -- GET this exact URL, no extra query params appended.
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        resp = requests.get(
            op_location,
            headers=_auth_header(token_provider),
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        status = body.get("status")
        if status == "Succeeded":
            return body
        if status == "Failed":
            raise RuntimeError(f"Analyze failed:\n{json.dumps(body, indent=2)}")
        time.sleep(interval_s)
    raise TimeoutError(f"Polling timed out after {timeout_s}s (last status unresolved)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Submit a document to Content Understanding, poll, save structured result."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", type=Path, help="Local file path -- base64-encoded, no blob step")
    src.add_argument(
        "--blob", nargs=2, metavar=("CONTAINER", "BLOB_NAME"),
        help="Existing blob container + name -- script generates a fresh SAS",
    )
    parser.add_argument("--out", type=Path, default=Path("results"), help="Output directory (default: ./results)")
    args = parser.parse_args()

    load_dotenv()
    try:
        account = os.environ["AIF_ACCOUNT"]
        resource_group = os.environ["AIF_RESOURCE_GROUP"]
        analyzer_id = os.environ["ANALYZER_ID"]
    except KeyError as e:
        sys.exit(f"Missing required .env value: {e}. Copy .env.example to .env and fill it in.")
    storage_account = os.environ.get("STORAGE_ACCOUNT")
    api_version = os.environ.get("API_VERSION", "2025-11-01")

    if args.blob and not storage_account:
        sys.exit("--blob requires STORAGE_ACCOUNT to be set in .env")

    print(f"[1/5] Resolving endpoint for {account}...")
    endpoint = get_endpoint(account, resource_group)

    print("[2/5] Entra ID token provider (keyless; signs in as the az login user)...")
    token_provider = build_token_provider()

    print("[3/5] Preparing input payload...")
    if args.file:
        analysis_input = build_input_from_file(args.file)
        label = args.file.stem
    else:
        container, blob = args.blob
        sas_url = get_sas_url(storage_account, container, blob)
        analysis_input = build_input_from_sas(sas_url)
        label = Path(blob).stem

    print(f"[4/5] Submitting to analyzer '{analyzer_id}' and polling...")
    op_location = submit_analyze(endpoint, token_provider, analyzer_id, api_version, analysis_input)
    result = poll_result(op_location, token_provider)

    args.out.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = args.out / f"{timestamp}_{label}.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"[5/5] Saved: {out_path}")


if __name__ == "__main__":
    main()
