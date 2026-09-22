#!/usr/bin/env python3
"""
M10 probe -- which token audience does the /openai/v1/ route accept?

THE TWELFTH CALL SITE. m5_index.build_embedding_client() is the one migration
target that is NOT a swap, for two reasons:

1. It builds a PLAIN `OpenAI` client pointed at f"{endpoint}/openai/v1/", not
   an `AzureOpenAI` client. That shape was chosen deliberately -- the Aug
   11/12 404 forced the v1 GA migration for embeddings specifically (see
   STATUS.md Key Lessons), so reverting to AzureOpenAI to get
   azure_ad_token_provider would undo a fix. The plain class has no
   azure_ad_token_provider parameter.

2. Microsoft's docs name TWO DIFFERENT AUDIENCES and this route is exactly
   where they disagree:
     - classic Azure OpenAI / AI Services: https://cognitiveservices.azure.com/.default
       (verified working 2026-09-22 for Vision Read and the Evaluation SDK)
     - Foundry v1 /openai/v1/ route: "Tokens must be issued with scope
       https://ai.azure.com/.default"
   Neither is safe to assume for THIS client.

This probe tries both audiences against the real embeddings deployment and
reports which the service accepts. It also tests whether a CALLABLE works as
api_key -- openai-python resolves api_key into an Authorization: Bearer
header, and if a callable is not supported then any token here is a fixed
string that expires in ~60-90 minutes, which constrains how long a single
indexing run may be.

Read-only: embeds one short string. Indexes nothing, writes nothing.

Written by Claude 2026-09-22 at Gerard's direction.

Run (from scripts/, venv active):
    python probe_keyless_v1_scope.py
"""

import os

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential

from m3_analyze import get_endpoint  # reuse, don't rewrite

SCOPES = [
    ("cognitiveservices", "https://cognitiveservices.azure.com/.default"),
    ("ai.azure.com",      "https://ai.azure.com/.default"),
]


def main():
    load_dotenv()
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    deployment = os.environ["EMBEDDING_DEPLOYMENT"]
    base_url = f"{get_endpoint(account, rg)}/openai/v1/"
    cred = DefaultAzureCredential()

    print("PROBE: /openai/v1/ token audience for the embeddings route")
    print(f"  base_url    {base_url}")
    print(f"  deployment  {deployment}\n")

    winners = []
    for name, scope in SCOPES:
        try:
            token = cred.get_token(scope).token
        except Exception as exc:  # noqa: BLE001
            print(f"  {name:<20} token NOT ISSUED -- {type(exc).__name__}: {exc}")
            continue
        try:
            client = OpenAI(api_key=token, base_url=base_url)
            resp = client.embeddings.create(model=deployment, input=["keyless probe"])
            dims = len(resp.data[0].embedding)
            print(f"  {name:<20} ACCEPTED  -- {dims}-dim vector returned")
            winners.append((name, scope))
        except Exception as exc:  # noqa: BLE001
            first = str(exc).splitlines()[0][:160]
            print(f"  {name:<20} REJECTED  -- {type(exc).__name__}: {first}")

    # Does a callable work as api_key? Decides whether token refresh is possible
    # on this client shape, which decides how long an indexing run may safely be.
    print()
    if winners:
        _, scope = winners[0]
        try:
            client = OpenAI(api_key=lambda: cred.get_token(scope).token, base_url=base_url)
            client.embeddings.create(model=deployment, input=["callable probe"])
            print("  callable api_key    ACCEPTED -- the client refreshes; no expiry ceiling")
        except Exception as exc:  # noqa: BLE001
            print(f"  callable api_key    REJECTED -- {type(exc).__name__}: {str(exc).splitlines()[0][:120]}")
            print("                      => the token is a fixed string. Fine for a short")
            print("                         indexing run; NOT safe for anything over ~60 min.")

    print()
    if not winners:
        print("  VERDICT: neither audience worked. Do NOT migrate this call site by")
        print("           guesswork -- m5_index.py keeps its key and M10's done-when")
        print("           carries a stated, single-line exception.")
        return 1
    print(f"  VERDICT: use {winners[0][1]}")
    if len(winners) > 1:
        print("           (both audiences work; prefer the classic one for consistency")
        print("            with every other call site, and record that both were tried)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
