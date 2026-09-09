"""
M7 -- detector for the agent writing its own grounding scaffolding into
customer-facing copy.

WHAT IT CATCHES. On 2026-09-08 every redraft observed -- 3 of 3, across two
different topics and two different runs -- put the grounding document into the
marketing description: "sticks to the details confirmed in the fact sheet",
"as presented in the store fact sheet", "questions about store policies not
listed there". That is copy addressed to a customer talking about an internal
document. Groundedness passed it three times; relevance marked it down for a
different reason; no INSTRUCTIONS_V3 clause forbids it.

WHY A SCRIPT AND NOT AN EYE. "3 of 3" was counted by reading drafts by hand.
That is fine for finding a defect and useless for tracking one: it cannot be
re-run over old files, it does not scale past a handful of runs, and after
INSTRUCTIONS_V4 the question becomes "did the fix hold across 21 runs", which
nobody is going to answer by reading 60 drafts. This makes it a measured field.

WHAT IT IS AND IS NOT. It is a phrase matcher, not a classifier. It reports
every match with the sentence around it so a human can confirm or dismiss each
one -- the same discipline the notes-vs-boolean entry earned: close reading
found the real bugs, and it is trusted as a pointer rather than a verdict. A
zero count is meaningful only for the phrasings listed in PATTERNS; a new
evasion invents new wording, and the honest response to a clean run after V4 is
to read a sample and confirm the copy is clean for the right reason.

DELIBERATELY STANDALONE. It touches neither m7_orchestrator.py nor
probe_orchestrator_stability.py. Those are the instruments the certification
pass runs on, and editing an instrument during the session that uses it is how
a measurement stops being attributable.

USAGE
  python check_meta_commentary.py                          # every results file
  python check_meta_commentary.py --results 20260908-143613_orchestrator_stability.json
  python check_meta_commentary.py --quiet                  # counts only, no excerpts
"""

import argparse
import json
import re
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

# Each entry is (label, pattern). Kept narrow on purpose: a loose pattern that
# fires on ordinary marketing copy would make the count worthless in the
# direction that matters, since a false positive here reads as a regression
# that has to be chased.
PATTERNS = [
    ("fact sheet",      r"\bfact[-\s]?sheets?\b"),
    ("the instructions", r"\b(?:the|these|my)\s+instructions?\b"),
    ("as instructed",   r"\bas\s+instructed\b"),
    ("source document", r"\b(?:source|provided|internal|grounding)\s+document\b"),
    ("confirmed in",    r"\bconfirmed\s+in\b"),
    ("listed there",    r"\b(?:not\s+)?listed\s+there\b"),
]
COMPILED = [(label, re.compile(pat, re.IGNORECASE)) for label, pat in PATTERNS]


def scan(text: str) -> list[dict]:
    """Every pattern hit in one draft, with the sentence it sits in.

    The excerpt is the point. A bare count cannot be audited, and this project
    has already logged one instrument that reported a number nobody could trace
    back to what produced it.
    """
    hits = []
    for label, rx in COMPILED:
        for m in rx.finditer(text or ""):
            start = text.rfind(".", 0, m.start()) + 1
            end = text.find(".", m.end())
            end = len(text) if end == -1 else end + 1
            hits.append({
                "pattern": label,
                "matched": m.group(0),
                "sentence": text[start:end].strip(),
            })
    return hits


def drafts_in(record: dict) -> list[str]:
    """Every drafted response text in one item record, in order."""
    out = []
    for call in record.get("tool_calls") or []:
        if call.get("tool") != "evaluate_draft":
            continue
        args = call.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                continue
        out.append((args or {}).get("response") or "")
    return out


def scan_file(path: Path, quiet: bool) -> dict:
    """Scan one results file. Handles both orchestrator and stability shapes.

    m7_orchestrator.py writes a flat list of records; the stability probe writes
    a dict of item_id -> list of records. Both are read here rather than
    normalized upstream, because normalizing would mean editing an instrument.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items")
    if isinstance(items, list):
        buckets = {r.get("id", f"record{i}"): [r] for i, r in enumerate(items)}
    elif isinstance(items, dict):
        buckets = items
    else:
        return {"file": path.name, "skipped": "no recognizable items key"}

    total_drafts = first_hits = redraft_hits = 0
    total_first = total_redrafts = 0
    findings = []

    for item_id, records in buckets.items():
        for run_no, record in enumerate(records, 1):
            for draft_no, text in enumerate(drafts_in(record), 1):
                total_drafts += 1
                is_first = draft_no == 1
                if is_first:
                    total_first += 1
                else:
                    total_redrafts += 1
                hits = scan(text)
                if not hits:
                    continue
                if is_first:
                    first_hits += 1
                else:
                    redraft_hits += 1
                findings.append({
                    "item": item_id, "run": run_no, "draft": draft_no,
                    "is_redraft": not is_first, "hits": hits,
                })

    print(f"\n{path.name}")
    print(f"  drafts scanned      : {total_drafts} "
          f"({total_first} first, {total_redrafts} redrafts)")
    # Split because the defect has only ever been observed on redrafts, and a
    # first-draft hit would be a genuinely new finding rather than more of the
    # same one.
    print(f"  FIRST drafts hit    : {first_hits}/{total_first}")
    print(f"  REDRAFTS hit        : {redraft_hits}/{total_redrafts}")
    if findings and not quiet:
        for f in findings:
            tag = "redraft" if f["is_redraft"] else "first draft"
            print(f"    {f['item']} run {f['run']}, {tag} {f['draft']}:")
            for h in f["hits"]:
                print(f"      [{h['pattern']}] {h['sentence']}")

    return {
        "file": path.name,
        "drafts_scanned": total_drafts,
        "first_drafts": total_first,
        "redrafts": total_redrafts,
        "first_drafts_hit": first_hits,
        "redrafts_hit": redraft_hits,
        "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--results", default="",
                        help="one filename under results/; default scans every "
                             "*_orchestrator*.json")
    parser.add_argument("--quiet", action="store_true",
                        help="counts only, no matched sentences")
    args = parser.parse_args()

    if args.results:
        paths = [RESULTS_DIR / args.results]
        if not paths[0].exists():
            raise SystemExit(f"no such results file: {paths[0]}")
    else:
        paths = sorted(RESULTS_DIR.glob("*_orchestrator*.json"))
        if not paths:
            raise SystemExit(f"no orchestrator results found in {RESULTS_DIR}")

    summaries = [scan_file(p, args.quiet) for p in paths]

    print(f"\n{'=' * 70}\nTOTALS across {len(summaries)} file(s)")
    tf = sum(s.get("first_drafts", 0) for s in summaries)
    tr = sum(s.get("redrafts", 0) for s in summaries)
    hf = sum(s.get("first_drafts_hit", 0) for s in summaries)
    hr = sum(s.get("redrafts_hit", 0) for s in summaries)
    print(f"  first drafts referencing the fact sheet : {hf}/{tf}")
    print(f"  redrafts referencing the fact sheet     : {hr}/{tr}")
    if tr and hr == tr:
        print("  => EVERY redraft on record does it. Not topic-specific, not "
              "occasional: it is what the agent does when it redrafts.")


if __name__ == "__main__":
    main()
