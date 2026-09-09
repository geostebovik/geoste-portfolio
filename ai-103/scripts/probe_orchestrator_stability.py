"""
M7 -- multi-run stability probe for the ORCHESTRATOR, the counterpart to
probe_fixture_stability.py (which covers the CV audit only).

WHY THIS EXISTS, AND WHY IT IS NOT ONLY A CERTIFICATION TOOL. The high-RUNS
pass owed before any public "stable" claim needs this. But as of 2026-09-08 it
also has a second job, and that job is why it was built today rather than after
the last open observation.

  `stop-on-pass` -- INSTRUCTIONS_V3 clause 7's "Stop as soon as `all_passed` is
  true" -- has zero observations. Two runs on 2026-09-08 fired the two-redraft
  cap (item7) and the keep-the-third-and-report clause, but no draft has ever
  passed AFTER a failure, so the early exit has never executed.

  Topic design looks unable to produce it. Relevance returns 3.0 (pass) when
  the topic's spine is supported and 2.0 (fail) when it is not, with nothing
  observed in between, so the condition producing a first-draft failure is the
  same one preventing recovery. See content-items-plan.md, "the relevance step
  function".

  VARIANCE CAN PRODUCE IT WHERE DESIGN CANNOT. item6 has scored relevance
  EXACTLY 3.0 against a threshold of 3, twice, on two different topics. The
  judge's own scores are not pinned -- unlike the CV audit's temperature=0 /
  seed=42 -- and item8 moved 4.0 -> 5.0 on an identical topic between runs, so
  +/-1 is the observed spread. An item sitting exactly on a threshold in a
  system with that spread should eventually draw below it. When it does,
  `all_passed` goes false, the agent redrafts, and the next draw very likely
  lands back at or above 3 -- which is stop-on-pass firing on its own, with no
  new fixture theory required. That is a prediction this script tests, not a
  fact it assumes.

WHAT IT MEASURES. Per item, across RUNS runs: the distribution of the FIRST
evaluate_draft verdict, the FINAL verdict, the redraft count, and every
individual groundedness/relevance SCORE. Scores, not just booleans -- the
audit probe tallies True/False because audit_thumbnail returns nothing else,
but here the interesting quantity is where relevance lands relative to 3.0, and
booleans would discard exactly that.

NOTHING IS DUPLICATED FROM m7_orchestrator.py. ITEMS, run_item(), the client,
the toolset and the provenance all import from it, the same way
probe_fixture_stability.py imports EXPECTED_RESULTS rather than copying the
answer key. A second copy of the item list would drift, and the probe would
quietly stop measuring the thing that actually runs.

USAGE
  python probe_orchestrator_stability.py                     # all items, 7 runs
  python probe_orchestrator_stability.py --items item6       # one item
  python probe_orchestrator_stability.py --items item6 --runs 7
  python probe_orchestrator_stability.py --items item6,item7 --runs 3

BUDGET, measured 2026-09-08: ~11.6K tokens per item per run, ~20.8K for an item
that exhausts the cap. Seven runs of one item is ~81K; seven runs of all eight
is ~715K and, at 30K TPM, well over half an hour of pure throughput.
"""

import argparse
import json
import os
import statistics
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from m7_orchestrator import (
    ACTIVE_INSTRUCTIONS,
    ACTIVE_INSTRUCTIONS_LABEL,
    AGENT_NAME,
    AGENT_TEMPERATURE,
    ITEMS,
    RESULTS_DIR,
    build_client,
    build_toolset,
    run_item,
    run_provenance,
)

STABLE_THRESHOLD = 0.8   # same 80% agreement bar as probe_fixture_stability.py


def draft_scores(record: dict) -> list[dict]:
    """Per-draft scores out of one item record's evaluate_draft calls.

    run_item() stores each tool call's raw output, so the judge's numbers are
    already in the record -- this only reshapes them. Returns one dict per
    draft, in order, so draft 1 vs draft 3 stays readable.
    """
    out = []
    for call in record.get("tool_calls") or []:
        if call.get("tool") != "evaluate_draft":
            continue
        try:
            parsed = json.loads(call["output"])
        except (KeyError, TypeError, ValueError):
            out.append({"groundedness": None, "relevance": None, "all_passed": None})
            continue
        out.append({
            "groundedness": (parsed.get("groundedness") or {}).get("score"),
            "relevance": (parsed.get("relevance") or {}).get("score"),
            "all_passed": parsed.get("all_passed"),
        })
    return out


def stop_on_pass_fired(record: dict) -> bool:
    """Did clause 7's early exit actually execute in this run?

    True only when the first evaluate_draft verdict was False and the last was
    True -- i.e. the agent failed, redrafted, and stopped on the pass. This is
    the event the 2026-09-08 sessions were unable to produce by fixture design;
    it is called out by name in the summary so one occurrence in seven runs
    cannot be missed in a JSON file.
    """
    return record.get("first_text_passed") is False and record.get("final_text_passed") is True


def summarize(item_id: str, records: list[dict], runs: int) -> dict:
    """Console summary plus the dict that goes into the results file."""
    firsts = [r.get("first_text_passed") for r in records]
    finals = [r.get("final_text_passed") for r in records]
    redrafts = [r.get("redrafts") for r in records]
    fired = [i + 1 for i, r in enumerate(records) if stop_on_pass_fired(r)]

    # Scores of the FIRST draft only. Later drafts exist only in runs that
    # failed, so mixing them in would compare different populations.
    first_g = [s[0]["groundedness"] for s in (draft_scores(r) for r in records)
               if s and s[0]["groundedness"] is not None]
    first_r = [s[0]["relevance"] for s in (draft_scores(r) for r in records)
               if s and s[0]["relevance"] is not None]

    def spread(values):
        if not values:
            return None
        return {
            "min": min(values),
            "max": max(values),
            "mean": round(statistics.fmean(values), 3),
            "values": values,
        }

    # A run whose agent crashed has first_text_passed None. It is NOT a failed
    # draft and must not share a denominator with one -- the same defect that
    # made a server_error read as three wrong audit cells on 2026-09-08, and
    # which would here drag the agreement figure down and read as instability.
    measured = [v for v in firsts if v is not None]
    unmeasured_runs = [i + 1 for i, v in enumerate(firsts) if v is None]
    first_pass_count = sum(1 for v in measured if v is True)
    agreement = first_pass_count / len(measured) if measured else 0.0
    stable = (agreement >= STABLE_THRESHOLD or (1 - agreement) >= STABLE_THRESHOLD) \
        if measured else False

    print(f"\n{item_id}:")
    if measured:
        print(f"  first draft passed : {first_pass_count}/{len(measured)} "
              f"({agreement:.0%}) -- {'STABLE' if stable else 'NOT STABLE'}")
    else:
        print("  first draft passed : no measured runs")
    print(f"  final passed       : {sum(1 for v in finals if v is True)}"
          f"/{len([v for v in finals if v is not None])}")
    if unmeasured_runs:
        print(f"  NOT MEASURED       : run(s) {unmeasured_runs} produced no "
              f"evaluate_draft verdict and are excluded from the counts above")
    print(f"  redrafts per run   : {redrafts}")
    if first_g:
        print(f"  groundedness (draft 1): {spread(first_g)}")
    if first_r:
        print(f"  relevance    (draft 1): {spread(first_r)}")
    if fired:
        print(f"  *** stop-on-pass FIRED on run(s) {fired} -- clause 7's early "
              f"exit executed for the first time ***")
    else:
        print("  stop-on-pass: not observed in this batch")

    return {
        "runs": runs,
        "first_text_passed": firsts,
        "final_text_passed": finals,
        "redrafts": redrafts,
        "first_draft_groundedness": spread(first_g),
        "first_draft_relevance": spread(first_r),
        "measured_runs": len(measured),
        "unmeasured_runs": unmeasured_runs,
        "first_pass_agreement": agreement,
        "stable": stable,
        "stop_on_pass_runs": fired,
        "per_run_draft_scores": [draft_scores(r) for r in records],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--runs", type=int, default=7,
                        help="runs per item (default 7, matching the audit probe)")
    parser.add_argument("--items", default="",
                        help="comma-separated item ids; default is every item")
    parser.add_argument("--sleep", type=float, default=5.0,
                        help="seconds between runs, to stay clear of the 30K TPM ceiling")
    args = parser.parse_args()

    wanted = [s.strip() for s in args.items.split(",") if s.strip()]
    items = [i for i in ITEMS if not wanted or i["id"] in wanted]
    if wanted:
        missing = set(wanted) - {i["id"] for i in items}
        if missing:
            parser.error(f"unknown item id(s): {sorted(missing)}")
    if not items:
        parser.error("no items selected")

    load_dotenv()
    # Its own name, not m7_orchestrator.py -- run_provenance lives in that
    # module, so Path(__file__).name there is the module, not the caller.
    provenance = run_provenance(script=Path(__file__).name)
    if provenance["git_dirty"]:
        print("WARNING: working tree is dirty. This result is not attributable to "
              "a commit and cannot be re-derived later.")
        for line in provenance["git_dirty_files"]:
            print(f"  {line}")

    client = build_client()
    toolset = build_toolset()
    client.enable_auto_function_calls(toolset)

    # item_id -> list of per-run records
    raw: dict[str, list[dict]] = {i["id"]: [] for i in items}
    try:
        agent = client.create_agent(
            model=os.environ["CHAT_DEPLOYMENT_GPT_5_4"],
            name=AGENT_NAME,
            instructions=ACTIVE_INSTRUCTIONS,
            toolset=toolset,
            temperature=AGENT_TEMPERATURE,
        )
        print(f"agent created: {agent.id} ({AGENT_NAME}), "
              f"instructions={ACTIVE_INSTRUCTIONS_LABEL}, "
              f"temperature={AGENT_TEMPERATURE}")
        print(f"probing {[i['id'] for i in items]} x {args.runs} runs")
        try:
            for n in range(args.runs):
                print(f"\n{'=' * 70}\n=== Run {n + 1}/{args.runs} ===\n{'=' * 70}")
                for item in items:
                    raw[item["id"]].append(run_item(client, agent.id, item))
                if args.sleep and n < args.runs - 1:
                    time.sleep(args.sleep)
        finally:
            client.delete_agent(agent.id)
            print(f"\nagent deleted: {agent.id}")
    finally:
        # Written even on a crash: a partial batch is still evidence, and
        # losing it is the failure run persistence was added to stop.
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        print("\n=== Stability summary ===")
        summaries = {iid: summarize(iid, recs, len(recs))
                     for iid, recs in raw.items() if recs}
        fired_any = sorted(iid for iid, s in summaries.items() if s["stop_on_pass_runs"])
        print("\n" + ("-" * 70))
        if fired_any:
            print(f"stop-on-pass OBSERVED on: {fired_any}")
        else:
            print("stop-on-pass: NOT observed in this batch. Clause 7's early exit "
                  "still has zero observations.")
        path = RESULTS_DIR / (datetime.now().strftime("%Y%m%d-%H%M%S")
                              + "_orchestrator_stability.json")
        path.write_text(json.dumps({
            "run": provenance,
            "probe": {
                "runs_requested": args.runs,
                "items": [i["id"] for i in items],
                "sleep_between_runs": args.sleep,
                "stable_threshold": STABLE_THRESHOLD,
            },
            "summary": summaries,
            "items": raw,
        }, indent=2), encoding="utf-8")
        print(f"\nresults written: {path}")


if __name__ == "__main__":
    main()
