#!/usr/bin/env python3
"""
M3 -- IIP Document Intelligence: submit-and-poll pipeline for Azure Content Understanding.

Pipeline (mirrors the proven manual commands in iip-cli-runbook.md, Google
Drive > IIP folder, "Submit an analyze call" / "Poll for the analyze result"
sections -- full debugging history behind these lives in MASTER-REFERENCE
Section 4.12):

    endpoint -> key -> SAS or base64 -> POST :analyze -> poll Operation-Location
    -> save structured result

Design decisions:
  - Config storage: .env (git-ignored) holds NON-secret resource names only
    (account name, resource group, storage account, analyzer id, api version).
  - The subscription key is fetched LIVE from Azure CLI every run via
    subprocess and is never written to disk. This is a stricter version of
    "keep secrets out of committed files" -- the key never touches a file
    at all, not even a git-ignored one.
  - Auth: key-based (Ocp-Apim-Subscription-Key), matching the already-proven
    REST calls. Managed identity/Entra ID doesn't apply cleanly here because
    this script runs on YOUR machine, not on an Azure-hosted resource -- there
    is no "managed identity" for a laptop. Revisit if this ever moves to a
    hosted context (Function App, App Service, etc).

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
    # Matches: az cognitiveservices account show --name <account>
    #   --resource-group <rg> --query properties.endpoint -o tsv
    return run_az([
        "cognitiveservices", "account", "show",
        "--name", account,
        "--resource-group", resource_group,
        "--query", "properties.endpoint",
    ]).rstrip("/")


def get_subscription_key(account: str, resource_group: str) -> str:
    # Matches: az cognitiveservices account keys list --name <account>
    #   --resource-group <rg> --query key1 -o tsv
    return run_az([
        "cognitiveservices", "account", "keys", "list",
        "--name", account,
        "--resource-group", resource_group,
        "--query", "key1",
    ])


def get_storage_key(storage_account: str, resource_group: str) -> str:
    # NOTE the different --query shape vs. get_subscription_key above:
    # `cognitiveservices account keys list` returns a flat object with
    # key1/key2. `storage account keys list` returns a LIST of {keyName,
    # value, ...} objects -- index [0] for the first key. Same-sounding
    # command family, different response shape.
    return run_az([
        "storage", "account", "keys", "list",
        "--account-name", storage_account,
        "--resource-group", resource_group,
        "--query", "[0].value",
    ])


def get_sas_url(storage_account: str, storage_key: str, container: str, blob: str, minutes: int = 30) -> str:
    # Matches iip-cli-runbook.md "Generate a read-only SAS URL for a blob":
    # az storage blob generate-sas --account-name <acct>
    #   --account-key "$STORAGE_KEY" --container-name <c> --name <b>
    #   --permissions r --expiry <ISO8601> --https-only --full-uri -o tsv
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%MZ")
    return run_az([
        "storage", "blob", "generate-sas",
        "--account-name", storage_account,
        "--account-key", storage_key,
        "--container-name", container,
        "--name", blob,
        "--permissions", "r",
        "--expiry", expiry,
        "--https-only",
        "--full-uri",
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


def submit_analyze(endpoint: str, key: str, analyzer_id: str, api_version: str, analysis_input: dict) -> str:
    # Matches: POST {endpoint}contentunderstanding/analyzers/{analyzerId}:analyze
    #   ?api-version=2025-11-01
    # Body shape confirmed from iip-cli-runbook.md: the input dict is wrapped
    # in an "inputs" LIST, not sent bare -- {"inputs": [{...}]}.
    url = f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}:analyze"
    resp = requests.post(
        url,
        params={"api-version": api_version},
        headers={
            "Ocp-Apim-Subscription-Key": key,
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


def poll_result(op_location: str, key: str, interval_s: int = 2, timeout_s: int = 300) -> dict:
    # iip-cli-runbook.md: "poll every 1-2 seconds ... copy the real header
    # value" -- GET this exact URL, no extra query params appended.
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        resp = requests.get(
            op_location,
            headers={"Ocp-Apim-Subscription-Key": key},
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

    print("[2/5] Fetching subscription key (live from az, not cached anywhere)...")
    key = get_subscription_key(account, resource_group)

    print("[3/5] Preparing input payload...")
    if args.file:
        analysis_input = build_input_from_file(args.file)
        label = args.file.stem
    else:
        container, blob = args.blob
        storage_key = get_storage_key(storage_account, resource_group)
        sas_url = get_sas_url(storage_account, storage_key, container, blob)
        analysis_input = build_input_from_sas(sas_url)
        label = Path(blob).stem

    print(f"[4/5] Submitting to analyzer '{analyzer_id}' and polling...")
    op_location = submit_analyze(endpoint, key, analyzer_id, api_version, analysis_input)
    result = poll_result(op_location, key)

    args.out.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = args.out / f"{timestamp}_{label}.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"[5/5] Saved: {out_path}")


if __name__ == "__main__":
    main()
