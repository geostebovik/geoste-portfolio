"""
M7 -- full 5-fixture stability probe, same reliability discipline as
probe_legibility_variants.py's diag-a/b/c/d treatment (5-run / 80%-
agreement standard, adopted Aug 31).

Runs m7_cv_audit_tool.py's audit_thumbnail() against all 5 EXPECTED_RESULTS
fixtures RUNS times each (temperature=0/seed=42 pinned as of 2026-09-01 --
see m7_cv_audit_tool.py's own dated comment on the parse() call), tallying
every field's boolean per fixture instead of eyeballing
scripts/results/audit_tool_results.txt by hand.

Written after 7 manual runs (2026-09-01, logged in that file) already
showed why this matters: item1/item3/item4/item5 came back 7/7 identical
(100% agreement -- real signal, not noise) but item2's info_accurate swung
4 True / 3 False -- close to a coin flip even with temperature and seed
both pinned. That's not sampling noise settling down with more runs, it's
a genuine ambiguity in how the model reads "Seasonal Home Maintenance
Checklist" against the fact sheet -- this script exists to confirm that
read is still unstable (or to confirm a wording/fixture fix resolved it),
not to keep re-running the same unresolved question by hand.

EXPECTED_RESULTS is imported, not duplicated -- m7_cv_audit_tool.py is the
one place that answer key is allowed to live.

Full per-run results (including notes, not just booleans) get written to a
timestamped JSON file in scripts/results/, matching the existing naming
convention there -- console output is the summary, the JSON is the record.
"""

import json
from datetime import datetime
from pathlib import Path

from m7_cv_audit_tool import audit_thumbnail, EXPECTED_RESULTS

FIXTURES_DIR = (
    Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware"
).resolve()
RESULTS_DIR = Path(__file__).parent / "results"

FIELDS = ("text_legible", "brand_consistent", "info_accurate")

# 7, not the usual 5 -- matches the manual batch Gerard already ran by hand
# on 2026-09-01 (item2's info_accurate split 4/3 at n=5-ish, close enough to
# a coin flip that the extra 2 runs are worth it for a real characterization
# of whichever wording is live when this runs).
RUNS = 7
STABLE_THRESHOLD = 0.8

# fixture_name -> list of {run, actual, notes} dicts, one per run
raw_results = {name: [] for name in EXPECTED_RESULTS}

for i in range(RUNS):
    print(f"=== Run {i + 1}/{RUNS} ===")
    for fixture_name in EXPECTED_RESULTS:
        image_path = FIXTURES_DIR / fixture_name
        actual = json.loads(audit_thumbnail(str(image_path)))
        raw_results[fixture_name].append({
            "run": i + 1,
            "actual": {field: actual[field] for field in FIELDS},
            "notes": actual["notes"],
        })
        print(f"  {fixture_name}: "
              f"{ {field: actual[field] for field in FIELDS} }")

print("\n=== Stability summary ===")
for fixture_name, runs in raw_results.items():
    expected = EXPECTED_RESULTS[fixture_name]
    print(f"\n{fixture_name} (expected {expected}):")
    for field in FIELDS:
        values = [r["actual"][field] for r in runs]
        true_count = sum(values)
        agreement = true_count / RUNS
        stable = agreement >= STABLE_THRESHOLD or (1 - agreement) >= STABLE_THRESHOLD
        majority = true_count >= RUNS / 2
        matches_expected = majority == expected[field]
        status = "STABLE" if stable else "NOT STABLE"
        match_note = "matches expected" if matches_expected else "MISMATCHES expected"
        print(f"  {field}: {true_count}/{RUNS} True ({agreement:.0%}) -- "
              f"{status}, majority={majority} ({match_note})")

RESULTS_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
out_path = RESULTS_DIR / f"{timestamp}_fixture_stability.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(raw_results, f, indent=2)

print(f"\nSaved: {out_path}")
