#!/usr/bin/env python3
"""
M10 probe -- does Entra ID cover Vision Read on aif-dev-wus-01?

Settles the FIRST HALF of the RBAC model's row 4 VERIFY. Row 4 asks whether
Foundry User covers "Vision Read and the Evaluation SDK"; this probe answers
Vision Read only. probe_keyless_eval.py answers the other half.

WHY IT IS UNTESTED. Before 2026-09-21 the Foundry account had no direct role
assignments at all -- the account key was concealing that. So no prior
successful run of m7_legibility_check.py proves anything about the keyless
path (m10-prep.md, "One thing not to assume").

WHAT A FAILURE MEANS, and it is not alarming. The Image Analysis SDK docs name
`Cognitive Services User` as the Entra prerequisite, NOT Foundry User. A 403
here is a plausible outcome with a known fix -- assign Cognitive Services User
on the account -- not a reason to rethink M10.

Read-only: one analyze call on one fixture. Writes nothing, changes nothing.

Written by Claude 2026-09-22 at Gerard's direction.

Run (from scripts/, venv active):
    python probe_keyless_vision.py
    python probe_keyless_vision.py item1-riverside-hardware.png
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures

from m3_analyze import get_endpoint  # reuse, don't rewrite

FIXTURES_DIR = (Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware").resolve()


def main():
    load_dotenv()
    account = os.environ["AIF_ACCOUNT"]
    rg = os.environ["AIF_RESOURCE_GROUP"]
    endpoint = get_endpoint(account, rg)

    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    fixture = FIXTURES_DIR / names[0] if names else sorted(FIXTURES_DIR.glob("item*.png"))[0]

    print("PROBE: Vision Read via Entra ID (no key)")
    print(f"  account   {account}")
    print(f"  endpoint  {endpoint}")
    print(f"  fixture   {fixture.name}")
    print("  NOTE: the endpoint above is built from customSubDomainName, not the")
    print("        resource name. If it reads aif-dev-... without 'iip', stop and say so.\n")

    # Step 1 -- can the credential mint a token for the Cognitive Services audience?
    # Separated from the call so a credential problem is never mistaken for a
    # role problem. This step succeeding proves nothing about authorization.
    scope = "https://cognitiveservices.azure.com/.default"
    try:
        token = DefaultAzureCredential().get_token(scope)
        print(f"  [1/2] token for {scope}: ACQUIRED (expires {token.expires_on})")
    except ClientAuthenticationError as exc:
        print(f"  [1/2] token FAILED -- this is a sign-in problem, not a role problem:\n        {exc}")
        return 2

    # Step 2 -- the call that actually tests the role assignment.
    client = ImageAnalysisClient(endpoint=endpoint, credential=DefaultAzureCredential())
    try:
        result = client.analyze(image_data=fixture.read_bytes(), visual_features=[VisualFeatures.READ])
    except HttpResponseError as exc:
        code = exc.status_code
        print(f"\n  [2/2] analyze FAILED -- HTTP {code}")
        print(f"        {exc.message.splitlines()[0] if exc.message else exc}")
        if code == 401:
            print("\n  VERDICT: 401 -- the token was rejected outright. Check that the")
            print("           endpoint is the custom-subdomain one and that the account")
            print("           has not had local auth disabled in a way that broke Entra.")
        elif code == 403:
            print("\n  VERDICT: 403 -- token accepted, NOT AUTHORIZED. Foundry User does")
            print("           NOT cover Vision Read. Expected fix: assign Cognitive")
            print("           Services User on aif-dev-wus-01 and re-run. Row 4 of the")
            print("           RBAC model needs amending either way -- record this.")
        else:
            print(f"\n  VERDICT: HTTP {code} is neither 401 nor 403 -- this is not an auth")
            print("           result. Do not record it as settling row 4.")
        return 1

    lines = [ln.text for blk in (result.read.blocks if result.read else []) for ln in blk.lines]
    print(f"\n  [2/2] analyze SUCCEEDED -- {len(lines)} text line(s) recovered")
    for text in lines:
        print(f"        {text!r}")
    print("\n  VERDICT: Foundry User COVERS Vision Read. Row 4's first half closes.")
    print("           m7_legibility_check.py's Group B migration is a code change only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
