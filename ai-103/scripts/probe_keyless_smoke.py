#!/usr/bin/env python3
"""
M10 smoke test -- every migrated auth path, checked before the 95-minute run.

WHY BEFORE THE ACCEPTANCE TEST. A migration typo that fails at minute 3 costs
the slot. This exercises each migrated path in ~60 seconds.

TWO KINDS OF CHECK, AND THE SPLIT IS NOT ARBITRARY.

  LIVE  -- modules that are safe to import. One real call each.
  STATIC -- m6_generate.py and m6_probe.py, which CANNOT be imported: both run
            real work at module scope (m6_generate does a full generate loop
            across two deployments and writes a results file; m6_probe fires a
            completion). Importing them to test them would run them. So their
            migration is verified by reading the source instead, and they are
            smoke-tested deliberately, by hand, as M10's done-when requires.
            m5_retrieve.py's docstring already flagged this hazard about
            m6_generate on Aug 20; it is now also the reason two scripts can't
            be covered live here. Logged as a backlog item.

Written by Claude 2026-09-22 at Gerard's direction.

Run (from scripts/, venv active):
    python probe_keyless_smoke.py
"""

import os
import re
import traceback
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).parent
FIXTURES = (HERE / ".." / "iip-docs" / "m7-riverside-hardware").resolve()
results = []


def record(ok, label, detail):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {label}\n        {detail}")


def live(label, fn):
    try:
        record(True, label, fn())
    except Exception:  # noqa: BLE001 -- reporting every failure is the point
        record(False, label, "\n        ".join(traceback.format_exc().strip().splitlines()[-3:]))


def static(fname, must_have, must_not_have):
    src = (HERE / fname).read_text(encoding="utf-8")
    missing = [p for p in must_have if not re.search(p, src)]
    present = [p for p in must_not_have if re.search(p, src)]
    if missing or present:
        record(False, f"{fname} (static)",
               f"missing={missing} unexpectedly_present={present}")
    else:
        record(True, f"{fname} (static)", "keyless pattern present, no api_key=key")


def chat(build, env_var):
    def run():
        client = build()
        dep = os.environ[env_var]
        r = client.chat.completions.create(
            model=dep,
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
            max_completion_tokens=2000,
        )
        return f"{dep} -> {r.choices[0].message.content!r}"
    return run


def main():
    load_dotenv()
    print("M10 SMOKE -- keyless auth on every migrated path\n")
    print("-- STATIC (modules with module-scope side effects; cannot be imported) --")
    for f in ("m6_generate.py", "m6_probe.py"):
        static(f, [r"azure_ad_token_provider=build_token_provider\(\)"],
                  [r"api_key=key"])

    print("\n-- LIVE --")
    import m7_vision_test, m7_cv_audit_tool, m5_retrieve

    live("m7_vision_test.build_client", chat(m7_vision_test.build_client, "CHAT_DEPLOYMENT_GPT_5_4"))
    live("m7_cv_audit_tool.build_audit_client (bumped api_version)",
         chat(m7_cv_audit_tool.build_audit_client, "CHAT_DEPLOYMENT_GPT_5_4_MINI"))
    live("m5_retrieve.build_chat_client", chat(m5_retrieve.build_chat_client, "CHAT_DEPLOYMENT_GPT_5_4_MINI"))

    def vision():
        from m7_legibility_check import audit_legibility
        legible, _ = audit_legibility(FIXTURES / "item1-paint-mixing-CLEAN.png")
        return f"Vision Read OK, text_legible={legible}"
    live("m7_legibility_check.audit_legibility", vision)

    def judge():
        # Must make a REAL judge call. Building the config proves nothing about
        # auth -- it is a TypedDict, and an unusable config constructs happily.
        # (An earlier version of this check only built it, and passed against a
        # config the SDK's validator went on to reject. 2026-09-22.)
        import m7_evaluator_tool
        from azure.ai.evaluation import GroundednessEvaluator
        cfg = m7_evaluator_tool.build_judge_config()
        if cfg.get("api_key"):
            raise AssertionError("api_key present in judge config -- migration incomplete")
        if cfg.get("credential"):
            raise AssertionError("credential present -- the SDK validator rejects this; see m6_evaluate.py")
        score = GroundednessEvaluator(cfg, is_reasoning_model=True)(
            query="What are the store hours?",
            context="Riverside Hardware is open 7am to 7pm Monday through Saturday.",
            response="Riverside Hardware is open from 7am to 7pm, Monday to Saturday.",
        )
        return f"deployment={cfg.get('azure_deployment')}, groundedness={score.get('groundedness')}"
    live("m7_evaluator_tool judge -> real evaluator call (Evaluation SDK)", judge)

    def embeddings():
        import m5_index
        client = m5_index.build_embedding_client()
        r = client.embeddings.create(model=os.environ["EMBEDDING_DEPLOYMENT"], input=["smoke"])
        return f"{os.environ['EMBEDDING_DEPLOYMENT']} -> {len(r.data[0].embedding)}-dim vector"
    live("m5_index.build_embedding_client (plain OpenAI, /openai/v1/)", embeddings)

    def search():
        from azure.identity import DefaultAzureCredential
        from azure.search.documents import SearchClient
        sc = SearchClient(endpoint=f"https://{os.environ['SEARCH_SERVICE']}.search.windows.net",
                          index_name=os.environ["SEARCH_INDEX_NAME"],
                          credential=DefaultAzureCredential())
        return f"query returned {len(list(sc.search(search_text='*', top=1)))} doc(s)"
    live("m5_retrieve search path (SearchClient)", search)

    passed = sum(results)
    print(f"\n  {passed}/{len(results)} passed")
    if passed < len(results):
        print("\n  DO NOT START THE ACCEPTANCE TEST -- fix the failures above first.")
        return 1
    print("\n  All migrated paths authenticate keylessly.")
    print("  NOT covered here: a hand-run of m6_generate.py / m6_probe.py, which")
    print("  cannot be imported without executing them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
