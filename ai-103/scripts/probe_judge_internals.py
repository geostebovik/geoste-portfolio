"""
M7 -- what can we actually control and see inside the Evaluation SDK's judge?

TWO QUESTIONS, AND THE ANSWER DECIDES THE NEXT EXPERIMENT. As of 2026-09-09
`GroundednessEvaluator` is known to return 1.0 and 4.0 on interchangeable drafts
of the same item, with the same four observations in both reason texts. Two
candidate levers exist and only one of them may be reachable:

  Q1. DOES THE JUDGE SPEND REASONING TOKENS ON A REAL EVALUATION PROMPT?
      probe_reasoning_params.py found every deployment answering "say ok" with
      reasoning_tokens=0, and gpt-5-2 -- the judge -- staying at 0 through
      reasoning_effort=medium where gpt-5-4 and gpt-5-4-mini start reasoning at
      low. But "say ok" is a trivial prompt and proves nothing about a
      2,000-token evaluation prompt. No past run can answer this either:
      _flatten() drops the SDK's _properties payload before anything is stored.

  Q2. IS reasoning_effort REACHABLE THROUGH THE SDK AT ALL?
      m7_evaluator_tool.py passes is_reasoning_model=True, which per the docs
      adjusts max_completion_tokens and strips unsupported parameters. It does
      NOT set reasoning_effort, so the judge runs at the deployment default.
      If the parameter can be threaded through, the next experiment is ONE
      parameter on a FIXED judge -- the cleanest available. If it cannot, the
      only remaining lever is the deployment.
      ANSWERED 2026-09-09: NOT reachable. Accepted by **kwargs, retained
      nowhere, while is_reasoning_model=True lands visibly as
      _is_reasoning_model. So the deployment it is.

WHY IT IS BUILT THIS WAY. Introspection first, then exactly ONE live evaluator
call. The introspection is free and answers Q2 without spending anything; the
single call answers Q1. Nothing here modifies m7_evaluator_tool.py -- that module
is the thing under test, and editing an instrument to measure it is the mistake
this project keeps a standing lesson about.

WHAT IT DELIBERATELY DOES NOT PRINT. The SDK's _properties payload embeds the
full judge prompt, fact-sheet.md verbatim included -- roughly 2.3 KB per call and
the reason _flatten() drops it. This prints STRUCTURE (keys, types, sizes) and
any usage/token numbers it can find, never the payload. --dump writes the whole
thing to a file if it needs reading by hand.

USAGE (run from scripts/)
  python probe_judge_internals.py
  python probe_judge_internals.py --dump raw_judge_result.json
  python probe_judge_internals.py --no-call        # introspection only, free
"""

import argparse
import inspect
import json
import os
from pathlib import Path

from dotenv import load_dotenv

RESULTS_DIR = Path(__file__).parent / "results"
DEFAULT_RESULTS = "20260909-122233_orchestrator_stability.json"
DEFAULT_ITEM = "item7"
DEFAULT_RUN = 1          # the draft that scored groundedness 1.0
DEFAULT_DRAFT = 1

TOKENISH = ("usage", "token", "reasoning", "completion", "prompt_tokens", "effort")


def hr(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


# ---------------------------------------------------------------------------
# Q2 -- introspection. Free, and it decides which experiment is possible.
# ---------------------------------------------------------------------------

def introspect() -> dict:
    from azure.ai.evaluation import (
        AzureOpenAIModelConfiguration,
        GroundednessEvaluator,
        RelevanceEvaluator,
    )
    import azure.ai.evaluation as aie

    out = {"sdk_version": getattr(aie, "__version__", "unknown")}
    hr(f"azure-ai-evaluation {out['sdk_version']}")

    # The model config is a TypedDict in this SDK, so its accepted keys are its
    # annotations. If reasoning_effort is not among them it cannot be set here,
    # whatever the underlying model supports.
    ann = dict(getattr(AzureOpenAIModelConfiguration, "__annotations__", {}))
    print("AzureOpenAIModelConfiguration accepts:")
    for k, v in ann.items():
        print(f"    {k}: {getattr(v, '__name__', v)}")
    out["model_config_fields"] = list(ann)
    out["model_config_has_reasoning_effort"] = "reasoning_effort" in ann

    for cls in (GroundednessEvaluator, RelevanceEvaluator):
        print(f"\n{cls.__name__}")
        try:
            sig = inspect.signature(cls.__init__)
            print(f"  __init__{sig}")
            out[f"{cls.__name__}_init"] = str(sig)
        except (TypeError, ValueError) as exc:
            print(f"  __init__ signature unavailable: {exc}")
        try:
            sig = inspect.signature(cls.__call__)
            print(f"  __call__{sig}")
        except (TypeError, ValueError) as exc:
            print(f"  __call__ signature unavailable: {exc}")
        print(f"  MRO: {' -> '.join(c.__name__ for c in cls.__mro__[:5])}")

    # Does the constructor tolerate an extra kwarg, and does it survive onto the
    # instance? **kwargs that is silently swallowed is WORSE than a rejection --
    # it looks like the parameter was set. Checked, not assumed.
    hr("Q2 -- can reasoning_effort be threaded through the constructor?")
    from m7_evaluator_tool import build_judge_config
    cfg = build_judge_config()
    try:
        ev = GroundednessEvaluator(cfg, is_reasoning_model=True, reasoning_effort="high")
        print("  constructor ACCEPTED reasoning_effort='high' (did not raise)")
        found = [(p, v) for p, v in _search_attrs(ev) if "reasoning_effort" in p]
        if found:
            print("  and it is retained on the instance at:")
            for p, v in found:
                print(f"    {p} = {v!r}")
            out["reasoning_effort_reachable"] = True
        else:
            print("  BUT it is NOT retained anywhere on the instance -- swallowed by\n"
                  "  **kwargs. Accepting a parameter and dropping it is indistinguishable\n"
                  "  from setting it, from the caller's side. Treat as NOT reachable.")
            out["reasoning_effort_reachable"] = False
    except Exception as exc:                       # noqa: BLE001 -- the error is data
        print(f"  constructor REJECTED it: {type(exc).__name__}: {exc}")
        out["reasoning_effort_reachable"] = False

    # Where does is_reasoning_model actually land? Same question, for a parameter
    # known to be honored -- it gives a reference point for what "retained" looks
    # like in this SDK.
    try:
        ev2 = GroundednessEvaluator(cfg, is_reasoning_model=True)
        hits = [(p, v) for p, v in _search_attrs(ev2)
                if "reasoning" in p.lower() or "max_completion" in p.lower()]
        print("\n  reference: where is_reasoning_model=True lands on the instance:")
        for p, v in hits[:12]:
            print(f"    {p} = {v!r}")
        if not hits:
            print("    (nowhere findable by attribute walk -- it may be applied at "
                  "call time rather than stored)")
    except Exception as exc:                       # noqa: BLE001
        print(f"  reference construction failed: {type(exc).__name__}: {exc}")

    return out


def _search_attrs(obj, prefix="", depth=0, seen=None):
    """Walk an object's attributes a few levels deep, yielding (path, value).

    Deliberately shallow and defensive: this is looking for a small scalar in an
    SDK whose internals are not part of its public contract, so it must not
    explode on a property that raises, and must not recurse forever.
    """
    if seen is None:
        seen = set()
    if depth > 3 or id(obj) in seen:
        return
    seen.add(id(obj))
    for name in dir(obj):
        if name.startswith("__"):
            continue
        try:
            val = getattr(obj, name)
        except Exception:                          # noqa: BLE001 -- properties can raise
            continue
        if callable(val):
            continue
        path = f"{prefix}.{name}" if prefix else name
        if isinstance(val, (str, int, float, bool, type(None))):
            yield path, val
        elif isinstance(val, dict):
            for k, v in val.items():
                if isinstance(v, (str, int, float, bool, type(None))):
                    yield f"{path}[{k!r}]", v
        elif hasattr(val, "__dict__"):
            yield from _search_attrs(val, path, depth + 1, seen)


# ---------------------------------------------------------------------------
# Q1 -- one live call, and read what the SDK returns BEFORE _flatten drops it.
# ---------------------------------------------------------------------------

def extract_draft(path: Path, item_id: str, run_no: int, draft_no: int) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data["items"][item_id]
    record = records[run_no - 1]
    calls = [c for c in record.get("tool_calls") or [] if c.get("tool") == "evaluate_draft"]
    call = calls[draft_no - 1]
    args = call["arguments"]
    if isinstance(args, str):
        args = json.loads(args)
    recorded = {}
    try:
        parsed = json.loads(call["output"])
        recorded = {
            "groundedness": (parsed.get("groundedness") or {}).get("score"),
            "relevance": (parsed.get("relevance") or {}).get("score"),
        }
    except (KeyError, TypeError, ValueError):
        pass
    return {"query": args.get("query"), "response": args.get("response"),
            "recorded": recorded}


def find_numbers(obj, prefix=""):
    """Every numeric leaf whose key looks token- or usage-related."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (int, float)) and any(t in str(k).lower() for t in TOKENISH):
                yield p, v
            else:
                yield from find_numbers(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:20]):
            yield from find_numbers(v, f"{prefix}[{i}]")
    elif isinstance(obj, str) and len(obj) < 20000:
        # The SDK sometimes nests a JSON string inside the result payload.
        s = obj.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                yield from find_numbers(json.loads(s), prefix + "(parsed)")
            except ValueError:
                pass


def live_call(draft: dict, dump: str | None) -> dict:
    from azure.ai.evaluation import GroundednessEvaluator
    from m7_evaluator_tool import build_judge_config, context

    hr("Q1 -- one real evaluator call, raw result before _flatten()")
    print(f"  judging a recorded draft: groundedness was {draft['recorded'].get('groundedness')}, "
          f"relevance {draft['recorded'].get('relevance')}")
    print(f"  response is {len(draft['response'] or '')} chars, "
          f"context (fact sheet) is {len(context)} chars")

    ev = GroundednessEvaluator(build_judge_config(), is_reasoning_model=True)
    raw = ev(query=draft["query"], response=draft["response"], context=context)

    print("\n  top-level keys returned:")
    for k, v in raw.items():
        kind = type(v).__name__
        size = f", {len(v)} chars" if isinstance(v, str) else ""
        print(f"    {k}: {kind}{size}")

    hits = sorted(set(find_numbers(dict(raw))))
    print("\n  token/usage numbers found anywhere in the payload:")
    if hits:
        for p, v in hits:
            print(f"    {p} = {v}")
        rt = [v for p, v in hits if "reasoning" in p.lower()]
        if rt:
            print(f"\n  => reasoning tokens on a REAL evaluation prompt: {rt}")
            if all(v == 0 for v in rt):
                print("     ZERO. The judge is not deliberating internally when it grades,\n"
                      "     which makes reasoning_effort the parameter to test -- if Q2 says\n"
                      "     it can be reached.")
        else:
            print("\n  => no reasoning-token field present. The SDK does not surface it here,\n"
                  "     so Q1 cannot be answered from the evaluator's return value. Falling\n"
                  "     back on the deployment default measured by probe_reasoning_params.py\n"
                  "     is an INFERENCE, not a measurement -- label it as one.")
    else:
        print("    none -- the SDK returns no usage information through this path at all.")

    if dump:
        Path(dump).write_text(json.dumps(dict(raw), indent=2, default=str),
                              encoding="utf-8")
        print(f"\n  full raw payload written to {dump} "
              f"(contains the judge prompt and fact-sheet.md verbatim)")

    return {"keys": list(raw), "token_numbers": hits}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--results", default=DEFAULT_RESULTS)
    parser.add_argument("--item", default=DEFAULT_ITEM)
    parser.add_argument("--run", type=int, default=DEFAULT_RUN)
    parser.add_argument("--draft", type=int, default=DEFAULT_DRAFT)
    parser.add_argument("--dump", default=None,
                        help="write the full raw evaluator payload to this file")
    parser.add_argument("--no-call", action="store_true",
                        help="introspection only; makes no evaluator call")
    parser.add_argument("--judge-deployment", default=None,
                        help="deployment NAME to judge with (e.g. gpt-5-4-mini). "
                             "Default is JUDGE_DEPLOYMENT or CHAT_DEPLOYMENT_GPT_5_2 "
                             "from .env")
    args = parser.parse_args()

    load_dotenv()
    # MUST happen before m7_evaluator_tool is imported anywhere below:
    # build_judge_config() runs at that module's scope, so the environment has to
    # be right at import time, not at call time. introspect() and live_call()
    # import it lazily for exactly this reason.
    if args.judge_deployment:
        os.environ["JUDGE_DEPLOYMENT"] = args.judge_deployment
    print(f"judge deployment : {os.environ.get('JUDGE_DEPLOYMENT') or os.environ.get('CHAT_DEPLOYMENT_GPT_5_2')}"
          + ("   (overridden)" if args.judge_deployment else "   (default)"))

    findings = introspect()

    if not args.no_call:
        path = RESULTS_DIR / args.results
        if not path.exists():
            raise SystemExit(f"no such results file: {path}")
        findings.update(live_call(extract_draft(path, args.item, args.run, args.draft),
                                  args.dump))

    hr("What this decides")
    reachable = findings.get("reasoning_effort_reachable")
    if reachable:
        print("  reasoning_effort IS reachable. Next experiment: hold the judge\n"
              "  deployment fixed and vary reasoning_effort on the two item7 drafts\n"
              "  that scored 1.0 and 4.0. One parameter, one variable.")
    elif reachable is False:
        print("  reasoning_effort is NOT reachable through the SDK, so the deployment is\n"
              "  the only judge-side variable left. Use --judge-deployment.\n"
              "\n"
              "  CORRECTED 2026-09-09: an earlier version of this message said a swap\n"
              "  moves the model AND its default reasoning behavior together, so the two\n"
              "  could not be separated. That was wrong. probe_reasoning_params.py\n"
              "  measured the DEFAULT at reasoning_tokens=0 on all three deployments --\n"
              "  they diverge only when effort is requested explicitly, which is exactly\n"
              "  what cannot be done here. At the settings the SDK actually uses, a swap\n"
              "  changes the model alone. One variable.\n"
              "  Caveat that keeps it honest: that default was measured on a trivial\n"
              "  prompt. Run this probe per deployment to get a real-prompt reading\n"
              "  before relying on it.")
    else:
        print("  inconclusive -- read the introspection output above before choosing.")


if __name__ == "__main__":
    main()
