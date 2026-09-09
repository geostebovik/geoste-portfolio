"""
M7 -- what does this deployment actually accept? Introspects the reasoning-model
parameter contract against the live service, per deployment.

WHY THIS EXISTS. Microsoft's reasoning-models page lists gpt-5.2, gpt-5.4 and
gpt-5.4-mini as reasoning models, and states that reasoning models do NOT support
`temperature`, `top_p`, `presence_penalty`, `frequency_penalty`, `logprobs`,
`top_logprobs`, `logit_bias` or `max_tokens`. All three of those deployments are
in use here, and two project decisions rest on parameters from that list:

  - `m7_cv_audit_tool.py` pins `temperature=0`/`seed=42` on gpt-5-4-mini,
    decided 2026-09-01 specifically to settle the brand_consistent question.
  - `m7_orchestrator.py` pins `AGENT_TEMPERATURE = 0.0` on gpt-5-4, and the
    standing lesson built on it says temperature "narrows the distribution and
    does not collapse it".

If the service ignores those parameters, neither claim was ever true, and the
unexplained variance both were meant to control has a simpler cause than the one
on record. The calls do not error today, so the parameters are either accepted
or silently dropped -- and "silently dropped" is indistinguishable from "working"
without asking the service directly. That is what this does.

THE API VERSION IS PART OF THE QUESTION, NOT A DETAIL. `.env` sets
CHAT_API_VERSION, and `reasoning_effort` was introduced in 2024-12-01-preview
per the same docs page. A request sent on an older version cannot carry a
parameter that version does not define, so a parameter can be "unsupported"
because of the model, because of the API version, or both -- and those need
different fixes. Every check below prints the API version it ran under, and
--api-version re-runs the whole thing on another so the two can be compared.

WHAT IT REPORTS, per deployment:
  1. Does an explicit `temperature`/`seed` request succeed, or is it rejected?
  2. Is `reasoning_effort` accepted, and which values?
  3. Are reasoning tokens actually being spent? `completion_tokens_details.
     reasoning_tokens` == 0 means the model answered without reasoning, which
     for a judge is a plausible mechanism for the same evidence producing
     different scores on different calls.
  4. Does the same prompt return byte-identical text three times?

WHAT IT DOES NOT DO. It does not decide anything. A rejected parameter is a
fact; "therefore the pinning was inert" is an inference that still has to be
checked against what the pinned runs actually produced.

USAGE (run from scripts/)
  python probe_reasoning_params.py
  python probe_reasoning_params.py --api-version 2025-04-01-preview
  python probe_reasoning_params.py --deployments CHAT_DEPLOYMENT_GPT_5_2

BUDGET: about a dozen single-sentence completions. Negligible.
"""

import argparse
import os

from dotenv import load_dotenv
from openai import AzureOpenAI

# Same helpers m7_evaluator_tool.py uses to reach the account -- reused rather
# than reimplemented, so this probe authenticates exactly the way the judge does.
# If these ever diverge, the probe stops describing the thing under test.
from m3_analyze import get_endpoint, get_subscription_key

PROMPT = "Reply with exactly: ok"
DEPLOYMENT_VARS = [
    "CHAT_DEPLOYMENT_GPT_5_2",
    "CHAT_DEPLOYMENT_GPT_5_4",
    "CHAT_DEPLOYMENT_GPT_5_4_MINI",
]
EFFORT_VALUES = ["none", "minimal", "low", "medium", "high"]


def build_client(api_version: str) -> AzureOpenAI:
    account, rg = os.environ["AIF_ACCOUNT"], os.environ["AIF_RESOURCE_GROUP"]
    return AzureOpenAI(
        azure_endpoint=get_endpoint(account, rg),
        api_key=get_subscription_key(account, rg),
        api_version=api_version,
    )


def call(client: AzureOpenAI, deployment: str, **kwargs) -> tuple[bool, str, dict]:
    """One completion. Returns (ok, text_or_error, usage_details).

    Errors are returned rather than raised: a rejection IS the measurement here,
    so a probe that stops on the first 400 would answer nothing.
    """
    try:
        r = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": PROMPT}],
            **kwargs,
        )
        details = {}
        usage = getattr(r, "usage", None)
        if usage is not None:
            ctd = getattr(usage, "completion_tokens_details", None)
            details = {
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "reasoning_tokens": getattr(ctd, "reasoning_tokens", None) if ctd else None,
            }
        return True, (r.choices[0].message.content or "").strip(), details
    except Exception as exc:                      # noqa: BLE001 -- the error is data
        return False, f"{type(exc).__name__}: {exc}"[:300], {}


def probe(client: AzureOpenAI, deployment: str, api_version: str) -> dict:
    print(f"\n{'=' * 70}\n{deployment}   (api_version={api_version})\n{'=' * 70}")
    result = {"deployment": deployment, "api_version": api_version}

    # 1. Baseline -- if this fails, nothing below means anything.
    ok, text, details = call(client, deployment)
    print(f"  baseline call            : {'OK' if ok else 'FAILED'} -- {text}")
    result["baseline"] = {"ok": ok, "text": text, **details}
    if not ok:
        print("  (skipping the rest: the deployment did not answer a plain call)")
        return result
    if details:
        rt = details.get("reasoning_tokens")
        print(f"  reasoning tokens spent   : {rt}"
              + ("   <-- ZERO: answered without reasoning" if rt == 0 else ""))

    # 2. temperature + seed -- the two the CV audit and the orchestrator pin.
    for label, kwargs in (
        ("temperature=0", {"temperature": 0}),
        ("seed=42", {"seed": 42}),
        ("temperature=0 + seed=42", {"temperature": 0, "seed": 42}),
    ):
        ok, text, _ = call(client, deployment, **kwargs)
        print(f"  {label:<24} : {'ACCEPTED' if ok else 'REJECTED'} -- {text}")
        result[label] = {"accepted": ok, "detail": text}

    # 3. reasoning_effort -- never set anywhere in this project.
    accepted_efforts = []
    for effort in EFFORT_VALUES:
        ok, text, details = call(client, deployment, reasoning_effort=effort)
        rt = details.get("reasoning_tokens")
        print(f"  reasoning_effort={effort:<8} : {'ACCEPTED' if ok else 'REJECTED'}"
              + (f" (reasoning_tokens={rt})" if ok else f" -- {text}"))
        if ok:
            accepted_efforts.append({"value": effort, "reasoning_tokens": rt})
    result["reasoning_effort_accepted"] = accepted_efforts

    # 4. Repeatability of the plain call. Three identical requests.
    # NOT a determinism claim about the judge -- one short prompt says nothing
    # about a long evaluation prompt. It only shows whether identical inputs can
    # return identical outputs at all on this deployment.
    texts = [call(client, deployment)[1] for _ in range(3)]
    identical = len(set(texts)) == 1
    print(f"  same prompt x3 identical : {identical}  {texts if not identical else ''}")
    result["repeatable_short_prompt"] = identical

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--api-version", default=None,
                        help="override CHAT_API_VERSION from .env")
    parser.add_argument("--deployments", default="",
                        help="comma-separated .env variable NAMES (not values); "
                             "default is all three chat deployments")
    args = parser.parse_args()

    load_dotenv()
    api_version = args.api_version or os.environ["CHAT_API_VERSION"]
    wanted = [s.strip() for s in args.deployments.split(",") if s.strip()] or DEPLOYMENT_VARS

    print(f"CHAT_API_VERSION in .env : {os.environ.get('CHAT_API_VERSION')}")
    print(f"api_version used here    : {api_version}")
    if api_version < "2024-12-01":
        print("  NOTE: reasoning_effort was introduced in 2024-12-01-preview. On an\n"
              "  older version a REJECTED result means the API version lacks the\n"
              "  parameter, not that the model lacks the capability. Re-run with\n"
              "  --api-version to separate the two.")

    client = build_client(api_version)
    for var in wanted:
        deployment = os.environ.get(var)
        if not deployment:
            print(f"\n{var}: not set in .env, skipped")
            continue
        probe(client, deployment, api_version)

    print(f"\n{'=' * 70}")
    print("Read this against two claims on record, and correct them if it "
          "contradicts them:")
    print("  - m7_cv_audit_tool.py pins temperature=0/seed=42 (decided Sep 1)")
    print("  - m7_orchestrator.py pins AGENT_TEMPERATURE=0.0, and the standing")
    print("    lesson says temperature narrows the distribution")
    print("A parameter the service rejects or ignores never did either.")


if __name__ == "__main__":
    main()
