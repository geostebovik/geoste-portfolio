#!/usr/bin/env python3
"""
M10 probe -- does the Evaluation SDK work keyless, and HOW?

Settles the SECOND HALF of the RBAC model's row 4 VERIFY ("Foundry User covers
Vision Read AND the Evaluation SDK"). probe_keyless_vision.py answers the first.

WHY THIS IS NOT A GROUP A EDIT. m10-prep.md lists m6_evaluate.py and
m7_evaluator_tool.py in Group A, whose prescribed fix is
`api_key=` -> `azure_ad_token_provider=`. But neither builds an AzureOpenAI
client. Both build an `AzureOpenAIModelConfiguration`, which is a TypedDict the
Evaluation SDK consumes -- it has no azure_ad_token_provider parameter. So 2 of
Group A's 9 call sites take a different fix, and Group A is 7 mechanical + 2
unknown, not 9 mechanical. Step 1 below establishes what the installed version
actually accepts rather than assuming.

Pinned version: azure-ai-evaluation==1.18.3 (requirements.txt, pinned 2026-08-05).

Cost: one judge call on one trivial fixture pair. Not the 95-minute acceptance
test -- this is a 2-minute auth probe. Writes nothing.

Written by Claude 2026-09-22 at Gerard's direction.

Run (from scripts/, venv active):
    python probe_keyless_eval.py
"""

import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

from m3_analyze import get_endpoint  # reuse, don't rewrite


def main():
    load_dotenv()
    account = os.environ["AIF_ACCOUNT"]
    rg = os.environ["AIF_RESOURCE_GROUP"]
    deployment = os.environ.get("JUDGE_DEPLOYMENT", "gpt-5-4")
    api_version = os.environ["CHAT_API_VERSION"]
    endpoint = get_endpoint(account, rg)

    print("PROBE: azure-ai-evaluation via Entra ID (no key)")
    print(f"  account     {account}")
    print(f"  endpoint    {endpoint}")
    print(f"  deployment  {deployment}")
    print(f"  api_version {api_version}\n")

    # Step 1 -- INTROSPECTION. What does the installed version actually accept?
    # Done before any call, because the answer decides what the migration looks
    # like for m6_evaluate.py and m7_evaluator_tool.py.
    import azure.ai.evaluation as evaluation
    from azure.ai.evaluation import AzureOpenAIModelConfiguration, GroundednessEvaluator

    version = getattr(evaluation, "__version__", "unknown")
    annotations = getattr(AzureOpenAIModelConfiguration, "__annotations__", {})
    required = getattr(AzureOpenAIModelConfiguration, "__required_keys__", frozenset())
    optional = getattr(AzureOpenAIModelConfiguration, "__optional_keys__", frozenset())

    print(f"  [1/2] azure-ai-evaluation version: {version}")
    print(f"        AzureOpenAIModelConfiguration accepts: {sorted(annotations)}")
    print(f"        required: {sorted(required)}")
    print(f"        optional: {sorted(optional)}")
    if "azure_ad_token_provider" in annotations:
        print("        NOTE: it DOES accept azure_ad_token_provider -- m10-prep.md's")
        print("              Group A prescription happens to work here after all.")
    elif "api_key" in optional:
        print("        api_key is OPTIONAL -> omitting it should fall back to a")
        print("        credential chain. That is the fix for these two scripts.")
    else:
        print("        api_key appears REQUIRED -> omitting it may raise. Read the")
        print("        error in step 2 carefully before designing the migration.")

    scope = "https://cognitiveservices.azure.com/.default"
    try:
        DefaultAzureCredential().get_token(scope)
        print(f"\n        token for {scope}: ACQUIRED")
    except ClientAuthenticationError as exc:
        print(f"\n        token FAILED -- sign-in problem, not a role problem:\n        {exc}")
        return 2

    # Step 2 -- build the config WITHOUT api_key and run one real judge call.
    judge = AzureOpenAIModelConfiguration(
        azure_endpoint=endpoint,
        api_version=api_version,
        azure_deployment=deployment,
    )
    evaluator = GroundednessEvaluator(judge, is_reasoning_model=True)

    try:
        score = evaluator(
            query="What are the store hours?",
            context="Riverside Hardware is open 7am to 7pm Monday through Saturday.",
            response="Riverside Hardware is open from 7am to 7pm, Monday to Saturday.",
        )
    except Exception as exc:  # noqa: BLE001 -- the exception TYPE is the finding here
        print(f"\n  [2/2] evaluator FAILED -- {type(exc).__name__}")
        print(f"        {exc}")
        print("\n  VERDICT: keyless is NOT a drop-in for the Evaluation SDK on 1.18.3.")
        print("           Read the exception type above: a KeyError/TypeError means the")
        print("           config shape is wrong (a code problem); a 401/403 inside the")
        print("           message means the shape is right and the ROLE is the problem.")
        print("           These are different findings -- do not record them as one.")
        print("           Either way, row 4's second half does NOT close today, and M10's")
        print("           sizing should carry these 2 call sites as open.")
        return 1

    print(f"\n  [2/2] evaluator SUCCEEDED -- {score}")
    print("\n  VERDICT: the Evaluation SDK works keyless with api_key omitted, and")
    print("           Foundry User covers it. Row 4's second half closes. The fix for")
    print("           m6_evaluate.py and m7_evaluator_tool.py is 'delete the api_key")
    print("           line', not the token-provider swap m10-prep.md prescribes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
