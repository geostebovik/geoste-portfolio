"""
M7 -- judge-isolation probe. Calls evaluate_draft() directly on a RECORDED
draft, N times, with no agent in the loop.

WHY THIS EXISTS. On 2026-09-08 the redraft branch produced its one clean
stop-on-pass observation (20260908-143613, item6, run 15): draft 1 scored
relevance 2.0 and failed, one redraft, draft 2 scored 3.0 and passed. But the
judge's PRIMARY criticism was identical on both drafts -- "does not include the
key requested specifics: sizes, prices, and turnaround times" -- while the score
moved across the threshold. The observed variance on that cell is exactly the
size of the movement, so from one observation the recovery cannot be attributed
to the edit.

That matters because it inverts a decision. If the redraft loop REMEDIATES, a
higher cap gives the agent more chances to fix a draft. If it RE-ROLLS, a higher
cap is just more dice, and the correct cap goes DOWN, not up. The certification
pass was assumed to settle the cap directly; it cannot, until this is answered.

WHAT REMOVING THE AGENT BUYS. AGENT_TEMPERATURE=0 does not make an Agents-SDK
run repeatable -- 21 runs of item6 produced 19 distinct first drafts, because
the SDK has no `seed` parameter. So in the 21-run probe, judge variance and
draft variance are confounded and cannot be separated. Here the text is FIXED
and re-read from the run record, so every point of spread that appears is
judge-side by construction. There is nothing else left to vary.

THE PAIRED DESIGN, AND WHY IT IS NOT JUST THE FAILING DRAFT. Running draft 1
alone answers "is the judge noisy on a borderline text". That is worth knowing
and it is not the question that gates certification. The gating question is
whether draft 2 is actually BETTER, and that needs both distributions:

  - If draft 1 ever scores >= 3.0, a fixed failing draft can pass on a re-read.
    The loop can recover a draft it did not improve. One crossing is decisive.
  - If draft 2 ever scores < 3.0, a fixed passing draft can fail on a re-read,
    so run 15's pass was a draw from a distribution straddling the bar.
  - If the two distributions overlap substantially, the redraft did not move the
    text across the threshold; the re-read did. Retry-until-lucky, demonstrated
    rather than inferred.
  - If draft 2 sits cleanly above draft 1 with no overlap, the redraft earned
    it, the remediation clause works, and a higher cap is defensible.

GROUNDEDNESS IS THE BUILT-IN CONTROL. It scored 4.0 on both drafts and 4.0 on
all 21 first drafts in the stability probe -- zero variance observed anywhere.
If groundedness also spreads here, the finding is "this judge deployment is
noisy" rather than anything about relevance or the redraft loop, and the
relevance reading has to be re-framed. Reported either way, not assumed.

THE DRAFT TEXT IS EXTRACTED, NOT TYPED. Hardcoding a draft into this file would
put a transcription error between the run record and the measurement, and would
pin the probe to one moment. --results/--item/--run/--drafts address any
recorded draft, so this is reusable against any later borderline case. The exact
text and query judged are echoed to the console and written into the results
file, so the measurement is readable without the source JSON.

USAGE
  python probe_judge_isolation.py                       # run 15's drafts 1+2, n=10
  python probe_judge_isolation.py --n 20
  python probe_judge_isolation.py --drafts 1            # failing draft only
  python probe_judge_isolation.py --item item7 --run 1 --drafts 1,2,3

BUDGET. Each evaluate_draft() call is TWO judge calls (groundedness carries
fact-sheet.md, relevance does not) at roughly 3.9K tokens combined -- measured
2026-09-04. So n=10 on two drafts is ~78K tokens and, at 30K TPM, a few minutes
of throughput. Note these tokens do NOT appear in any orchestrator run.usage:
the judge runs on its own deployment, which is why every budget figure quoted
before 2026-09-08 undercounts.
"""

import argparse
import json
import os
import statistics
from datetime import datetime
from math import comb
from pathlib import Path

from dotenv import load_dotenv

# evaluate_draft is imported, never reimplemented: it is the function under
# test. A local copy of the judge config would measure something adjacent to
# what the orchestrator actually calls, which is the whole point of the probe.
from m7_evaluator_tool import evaluate_draft

# RESULTS_DIR and run_provenance come from the orchestrator for the same reason
# probe_orchestrator_stability.py imports them: a measurement that is not
# attributable to a commit cannot be re-derived later.
from m7_orchestrator import RESULTS_DIR, run_provenance

DEFAULT_RESULTS = "20260908-143613_orchestrator_stability.json"
DEFAULT_ITEM = "item6"
DEFAULT_RUN = 15


def extract_drafts(path: Path, item_id: str, run_number: int) -> list[dict]:
    """Pull every evaluate_draft call out of one recorded run, in order.

    Returns one dict per draft with the query and response exactly as the agent
    passed them, plus the score that call originally received. The original
    score is carried so the probe's re-reads can be compared against the number
    the run actually recorded -- if a re-read never reproduces it, that is
    itself a finding about the judge rather than about the draft.

    :param path: A results JSON written by probe_orchestrator_stability.py.
    :param item_id: Item id as it appears under the file's "items" key.
    :param run_number: 1-based run index, matching the console numbering.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        records = data["items"][item_id]
    except KeyError:
        available = sorted((data.get("items") or {}).keys())
        raise SystemExit(f"item {item_id!r} not in {path.name}; has: {available}")
    if not 1 <= run_number <= len(records):
        raise SystemExit(
            f"run {run_number} out of range for {item_id}: file has {len(records)} runs"
        )

    record = records[run_number - 1]
    drafts = []
    for call in record.get("tool_calls") or []:
        if call.get("tool") != "evaluate_draft":
            continue
        args = call.get("arguments")
        if isinstance(args, str):
            args = json.loads(args)
        try:
            original = json.loads(call["output"])
        except (KeyError, TypeError, ValueError):
            original = {}
        drafts.append({
            "query": args.get("query"),
            "response": args.get("response"),
            "original_groundedness": (original.get("groundedness") or {}).get("score"),
            "original_relevance": (original.get("relevance") or {}).get("score"),
            "original_all_passed": original.get("all_passed"),
        })
    if not drafts:
        raise SystemExit(f"{item_id} run {run_number} made no evaluate_draft calls")
    return drafts


def judge_repeatedly(query: str, response: str, n: int) -> list[dict]:
    """Call evaluate_draft() n times on one fixed text.

    A judge call that errors is recorded with null scores and NOT retried. It
    must not be silently replaced by a successful call: a failed measurement and
    a measured failure are different events, and letting them share a
    denominator is the defect that made a server_error read as three wrong
    audit cells on 2026-09-08.
    """
    out = []
    for i in range(1, n + 1):
        try:
            parsed = json.loads(evaluate_draft(query, response))
            g, r = parsed.get("groundedness") or {}, parsed.get("relevance") or {}
            row = {
                "call": i,
                "groundedness": g.get("score"),
                "groundedness_passed": g.get("passed"),
                "groundedness_reason": g.get("reason"),
                "relevance": r.get("score"),
                "relevance_passed": r.get("passed"),
                "relevance_reason": r.get("reason"),
                "threshold": r.get("threshold"),
                "all_passed": parsed.get("all_passed"),
                "error": None,
            }
            print(f"    call {i:>2}: groundedness {row['groundedness']}, "
                  f"relevance {row['relevance']}, all_passed {row['all_passed']}")
        except Exception as exc:                     # noqa: BLE001 -- recorded, not handled
            row = {"call": i, "groundedness": None, "groundedness_passed": None,
                   "groundedness_reason": None, "relevance": None,
                   "relevance_passed": None, "relevance_reason": None,
                   "threshold": None, "all_passed": None, "error": repr(exc)}
            print(f"    call {i:>2}: FAILED -- {exc!r}")
        out.append(row)
    return out


def spread(values: list[float]) -> dict | None:
    """min/max/mean/values for a list of scores, or None if nothing measured."""
    if not values:
        return None
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.fmean(values), 3),
        "distinct": sorted(set(values)),
        "values": values,
    }


def summarize(label: str, draft: dict, rows: list[dict]) -> dict:
    """Per-draft summary, printed and persisted.

    `crossings` is the number the probe exists to produce: how many re-reads of
    this FIXED text landed on the opposite side of the threshold from the
    verdict the run originally recorded. Any non-zero count on the failing draft
    means a draft can pass without being changed.
    """
    g = [r["groundedness"] for r in rows if r["groundedness"] is not None]
    r_ = [r["relevance"] for r in rows if r["relevance"] is not None]
    measured = [r for r in rows if r["all_passed"] is not None]
    failed_calls = [r["call"] for r in rows if r["error"] is not None]

    passes = sum(1 for r in measured if r["all_passed"] is True)
    original = draft["original_all_passed"]
    crossings = sum(1 for r in measured if r["all_passed"] is not original)

    print(f"\n  {label} -- originally groundedness {draft['original_groundedness']}, "
          f"relevance {draft['original_relevance']}, all_passed {original}")
    if measured:
        print(f"    all_passed on re-read : {passes}/{len(measured)}")
        print(f"    THRESHOLD CROSSINGS  : {crossings}/{len(measured)} "
              f"(re-reads disagreeing with the recorded verdict)")
    else:
        print("    no measured calls")
    print(f"    groundedness : {spread(g)}")
    print(f"    relevance    : {spread(r_)}")
    if failed_calls:
        print(f"    NOT MEASURED : call(s) {failed_calls} errored and are "
              f"excluded from the counts above")

    return {
        "label": label,
        "query": draft["query"],
        "response": draft["response"],
        "original_groundedness": draft["original_groundedness"],
        "original_relevance": draft["original_relevance"],
        "original_all_passed": original,
        "calls_requested": len(rows),
        "calls_measured": len(measured),
        "calls_errored": failed_calls,
        "all_passed_count": passes,
        "threshold_crossings": crossings,
        "groundedness": spread(g),
        "relevance": spread(r_),
        "calls": rows,
    }


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for the 2x2 table [[a, b], [c, d]].

    Used on PASS/FAIL counts -- a binary outcome -- not on the 1-5 scores. That
    distinction matters: a significance test on a three-point ordinal scale
    would dress the scale up as something finer than it is, but "do these two
    pass RATES differ" is an ordinary proportion question and deserves a real
    answer rather than an eyeball.
    """
    n = a + b + c + d
    if n == 0 or (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
        return 1.0
    def p_table(x: int) -> float:
        return (comb(a + b, x) * comb(c + d, a + c - x)) / comb(n, a + c)
    observed = p_table(a)
    lo = max(0, a + c - (c + d))
    hi = min(a + b, a + c)
    # Sum every table at least as extreme as the observed one. The tolerance is
    # not cosmetic: without it, a table with the same probability as the
    # observed one is intermittently dropped by float comparison and the
    # p-value comes out too small -- i.e. the error runs toward false
    # confidence, which is the direction that matters here.
    total = 0.0
    for x in range(lo, hi + 1):
        px = p_table(x)
        if px <= observed * (1 + 1e-9):
            total += px
    return min(1.0, total)


def compare(summaries: list[dict]) -> dict | None:
    """Did the redraft move the score, or did the re-read?

    THIS REPLACED A CRUDER TEST, and the reason is worth keeping. The first
    version asked only whether the two drafts' score RANGES intersect, and
    printed "retry-until-lucky" whenever they did. Run against the 2026-09-09
    data it called OVERLAP on draft 1 [2.0, 3.0] against draft 2 [3.0, 3.0] --
    ranges that touch at a single point while describing visibly different
    distributions, 7/10 passing against 10/10. The verdict string was stronger
    than the data underneath it: the same failure class as every other
    over-claim this project logs, committed by the instrument this time.

    So the verdict is now split into the two questions that actually have
    different answers, and neither is allowed to borrow the other's confidence:

      1. CAN A FIXED FAILING DRAFT PASS UNCHANGED? Counted directly, no test
         needed. One crossing is decisive, because the draft did not change.
      2. IS THE REDRAFT MEASURABLY BETTER? A two-proportion question, answered
         with Fisher's exact test, which at n=10 will usually say "cannot
         tell" -- and saying so is the correct output, not a weaker one.
    """
    usable = [s for s in summaries if s["relevance"]]
    if len(usable) < 2:
        return None
    a, b = usable[0], usable[1]

    a_pass, a_n = a["all_passed_count"], a["calls_measured"]
    b_pass, b_n = b["all_passed_count"], b["calls_measured"]
    p = fisher_two_sided(a_pass, a_n - a_pass, b_pass, b_n - b_pass)
    distinguishable = p < 0.05

    # Question 1. `a` is the draft the run recorded as FAILING, so any pass
    # here is a fixed text crossing the bar with nothing changed.
    unchanged_passes = a_pass if a["original_all_passed"] is False else None

    if unchanged_passes:
        q1 = (f"YES -- {a['label']} was recorded as FAILING and passed "
              f"{unchanged_passes}/{a_n} re-reads with its text unchanged. The "
              f"redraft loop can pass a draft it did not improve, so a pass "
              f"after a redraft is not by itself evidence the redraft worked.")
    elif unchanged_passes == 0:
        q1 = (f"NO -- {a['label']} failed all {a_n} re-reads. On this text the "
              f"recorded verdict is reproducible, and a pass after a redraft "
              f"is not explained by re-reading alone.")
    else:
        q1 = "N/A -- the first draft compared was not a recorded failure."

    q2 = (f"{'YES' if distinguishable else 'CANNOT TELL'} -- {a['label']} "
          f"{a_pass}/{a_n} vs {b['label']} {b_pass}/{b_n}, Fisher two-sided "
          f"p={p:.3f}. "
          + ("The pass rates differ; the redraft moved something real."
             if distinguishable else
             f"At this n the pass rates are not separable. The redraft may have "
             f"helped, may not have; this data cannot say. Raising n is the only "
             f"thing that changes this answer."))

    print(f"\n  {a['label']} relevance {a['relevance']['distinct']}, "
          f"passed {a_pass}/{a_n}")
    print(f"  {b['label']} relevance {b['relevance']['distinct']}, "
          f"passed {b_pass}/{b_n}")
    print(f"\n  Q1 -- can a fixed failing draft pass unchanged?")
    print(f"     {q1}")
    print(f"  Q2 -- is the redraft measurably better?")
    print(f"     {q2}")

    return {
        "compared": [a["label"], b["label"]],
        "pass_rates": {a["label"]: [a_pass, a_n], b["label"]: [b_pass, b_n]},
        "fisher_p": round(p, 4),
        "rates_distinguishable": distinguishable,
        "q1_fixed_failing_draft_can_pass": q1,
        "q2_redraft_measurably_better": q2,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--results", default=DEFAULT_RESULTS,
                        help=f"results filename under results/ (default {DEFAULT_RESULTS})")
    parser.add_argument("--item", default=DEFAULT_ITEM,
                        help=f"item id within that file (default {DEFAULT_ITEM})")
    parser.add_argument("--run", type=int, default=DEFAULT_RUN,
                        help=f"1-based run number (default {DEFAULT_RUN})")
    parser.add_argument("--drafts", default="1,2",
                        help="1-based draft numbers to re-judge (default 1,2)")
    parser.add_argument("--n", type=int, default=10,
                        help="re-reads per draft (default 10)")
    args = parser.parse_args()

    load_dotenv()

    path = RESULTS_DIR / args.results
    if not path.exists():
        raise SystemExit(f"no such results file: {path}")

    drafts = extract_drafts(path, args.item, args.run)
    wanted = [int(s) for s in args.drafts.split(",") if s.strip()]
    for d in wanted:
        if not 1 <= d <= len(drafts):
            raise SystemExit(
                f"draft {d} out of range: {args.item} run {args.run} has "
                f"{len(drafts)} evaluate_draft call(s)"
            )

    provenance = run_provenance()
    # run_provenance() is written for the orchestrator, so it records the agent
    # name, temperature and instructions text. NO AGENT RUNS HERE. Leaving those
    # fields in place would put an agent configuration into a results file that
    # never used one -- exactly the kind of confidently-wrong record the Sep 7
    # scheduled-task lesson is about. The git fields are what this probe needs
    # from it, and those are kept verbatim.
    provenance["script"] = Path(__file__).name
    provenance["note"] = ("no agent in this run: evaluate_draft() called directly. "
                          "Agent fields removed because none applied.")
    for agent_only in ("model_deployment", "agent_name", "temperature",
                       "instructions_label", "instructions"):
        provenance.pop(agent_only, None)
    provenance["judge_deployment"] = os.environ.get("CHAT_DEPLOYMENT_GPT_5_2", "")

    if provenance["git_dirty"]:
        print("WARNING: working tree is dirty. This result is not attributable to "
              "a commit and cannot be re-derived later.")
        for line in provenance["git_dirty_files"]:
            print(f"  {line}")

    print(f"\nsource : {path.name} -- {args.item}, run {args.run}")
    print(f"drafts : {wanted}, re-judged {args.n}x each, no agent in the loop")

    summaries = []
    try:
        for d in wanted:
            draft = drafts[d - 1]
            label = f"draft {d}"
            print(f"\n{'=' * 70}\n{label} -- the text being judged\n{'=' * 70}")
            print(f"query   : {draft['query']}")
            print(f"response:\n{draft['response']}\n")
            rows = judge_repeatedly(draft["query"], draft["response"], args.n)
            summaries.append(summarize(label, draft, rows))
    finally:
        # Written even on a crash: a partial batch is still evidence.
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n{'=' * 70}\n=== Judge-isolation summary ===\n{'=' * 70}")
        comparison = compare(summaries) if len(summaries) >= 2 else None
        out = RESULTS_DIR / (datetime.now().strftime("%Y%m%d-%H%M%S")
                             + "_judge_isolation.json")
        out.write_text(json.dumps({
            "run": provenance,
            "probe": {
                "source_results": path.name,
                "item": args.item,
                "source_run": args.run,
                "drafts": wanted,
                "reads_per_draft": args.n,
            },
            "comparison": comparison,
            "drafts": summaries,
        }, indent=2), encoding="utf-8")
        print(f"\nresults written: {out}")


if __name__ == "__main__":
    main()
