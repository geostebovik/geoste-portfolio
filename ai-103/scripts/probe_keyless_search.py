#!/usr/bin/env python3
"""
M10 probe -- does keyless auth work against srch-iip-dev-wus-01 (FREE tier)?

THE QUESTION. Microsoft Learn contradicts itself on whether the free tier
supports Entra ID client connections. Four pages, three one way:
  - Enable or disable RBAC ............... "any tier, INCLUDING FREE"
  - Quickstart: Connect (Python) ......... "any region OR TIER"
  - Quickstart: Connect (REST) ........... "any region OR TIER"
  - Connect your app using identities .... "must be a BILLABLE TIER"   <- outlier
  - Try Search for free .................. free "doesn't support ... MANAGED
                                            IDENTITIES for Entra ID auth"

The reading that reconciles all of them: free supports INBOUND Entra auth (a
client authenticating TO the service) but not OUTBOUND managed identity (the
service authenticating to storage, for indexers). m5_index.py and
m5_retrieve.py are clients. This probe tests that reading.

*** THIS PROBE IS ONLY DIAGNOSTIC IF A ROLE IS ASSIGNED FIRST. ***
The RBAC model deliberately assigns nothing on Search. Microsoft's own
troubleshooting table:
    403 Forbidden  -> identity lacks the role (up to 10 min to propagate)
    401 Unauthorized -> RBAC not enabled on the service
So an unassigned run returns 403 and reads as "the free tier can't do this" --
which would point M10 at a paid-tier recreate, a one-way door with a recurring
bill, for a missing role assignment. Assign Search Index Data Reader, wait for
propagation, THEN run this.

Read-only: one token request, one query. Creates nothing, indexes nothing.

Written by Claude 2026-09-22 at Gerard's direction.

Run (from scripts/, venv active):
    python probe_keyless_search.py
"""

import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient


def main():
    load_dotenv()
    service = os.environ["SEARCH_SERVICE"]
    index_name = os.environ["SEARCH_INDEX_NAME"]
    endpoint = f"https://{service}.search.windows.net"

    print("PROBE: Azure AI Search via Entra ID (no key), FREE tier")
    print(f"  service   {service}  (tier: free -- cannot be changed after creation)")
    print(f"  index     {index_name}")
    print(f"  endpoint  {endpoint}\n")

    # Step 1 -- token acquisition. Included for completeness, but note what it
    # does NOT prove: Entra mints a token for this audience regardless of the
    # service's tier, its RBAC setting, or your role assignments. A success
    # here is not evidence about the free tier. m10-prep.md's
    # `az account get-access-token` step has the same limitation.
    scope = "https://search.azure.com/.default"
    try:
        token = DefaultAzureCredential().get_token(scope)
        print(f"  [1/3] token for {scope}: ACQUIRED (expires {token.expires_on})")
        print("        (proves sign-in works; proves NOTHING about the tier)")
    except ClientAuthenticationError as exc:
        print(f"  [1/3] token FAILED -- sign-in problem, not a tier problem:\n        {exc}")
        return 2

    # Step 2 -- THE DECISIVE TEST. A plain text query on the existing index.
    # Deliberately NOT a vector query: m5_retrieve.py's vector path needs the
    # embedding deployment too, and a failure there would confound a Search
    # auth result with a Foundry auth result.
    credential = DefaultAzureCredential()
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)
    try:
        results = list(search_client.search(search_text="*", top=1))
    except HttpResponseError as exc:
        code = exc.status_code
        print(f"\n  [2/3] query FAILED -- HTTP {code}")
        print(f"        {exc.message.splitlines()[0] if exc.message else exc}")
        if code == 403:
            print("\n  VERDICT: 403 -- token accepted, NOT AUTHORIZED.")
            print("           Per Microsoft's troubleshooting table this means the role is")
            print("           missing or has not propagated (up to 10 min), NOT that the")
            print("           free tier lacks the capability. Confirm Search Index Data")
            print("           Reader is assigned to YOUR principal at the service scope,")
            print("           wait, re-run. Only a 403 that survives a confirmed, propagated")
            print("           role assignment is evidence about the tier.")
        elif code == 401:
            print("\n  VERDICT: 401 -- RBAC is not enabled for data-plane auth on this")
            print("           service. That contradicts the M8 baseline, which recorded")
            print("           authOptions.aadOrApiKey and disableLocalAuth:false. Re-read")
            print("           the live authOptions before concluding anything about tiers.")
        else:
            print(f"\n  VERDICT: HTTP {code} is neither 401 nor 403 -- not an auth result.")
        return 1

    print(f"\n  [2/3] query SUCCEEDED -- {len(results)} document(s) returned")
    for doc in results:
        keys = sorted(k for k in doc if not k.startswith("@"))
        print(f"        fields: {keys}")

    # Step 3 -- the write/service path, reported SEPARATELY. m5_index.py needs
    # Search Service Contributor + Search Index Data Contributor. With only
    # Reader assigned this is EXPECTED to fail, and that failure says nothing
    # about the tier. Reported so the two paths are never conflated.
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    try:
        index = index_client.get_index(index_name)
        print(f"\n  [3/3] get_index SUCCEEDED -- {len(index.fields)} field(s)")
        print("        (you hold a service-level role too; m5_index.py's path is open)")
    except HttpResponseError as exc:
        print(f"\n  [3/3] get_index failed -- HTTP {exc.status_code}")
        print("        EXPECTED with only Search Index Data Reader assigned. This is a")
        print("        role scope result, not a tier result. m5_index.py additionally")
        print("        needs Search Service Contributor + Search Index Data Contributor.")

    print("\n  VERDICT: keyless query WORKS on the free tier. The 'billable tier'")
    print("           prerequisite is about outbound managed identity, not inbound")
    print("           client auth. Group C is a code change -- no service recreate,")
    print("           no recurring bill. Record this against m10-prep.md's")
    print("           'PROBABLE BLOCKER' framing, which this retires.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
