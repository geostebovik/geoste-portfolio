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

ONLY TWO OF THE THREE FIELDS ARE MODEL-JUDGED (true since 2026-09-03, said
out loud here 2026-09-11). text_legible comes from audit_legibility() --
Azure AI Vision Read locating each text element, then WCAG contrast
arithmetic against the 3.0:1 large-text minimum -- and returns the same
value every run by construction. So a 5-fixture x 3-field x RUNS matrix is
5 x 2 x RUNS model-judged cells plus 5 x 1 x RUNS deterministic ones, and
the summary below reports those totals separately. At RUNS=15 that is 150
judged and 75 deterministic, not 225 judged. Rolling them into one figure
overstates what the probe measured; the totals are printed apart so a
number lifted from this output into a claim is already the right one.

Full per-run results (including notes, not just booleans) get written to a
timestamped JSON file in scripts/results/, matching the existing naming
convention there -- console output is the summary, the JSON is the record.

RESULTS FILE SHAPE CHANGED 2026-09-11, when provenance was added. Fixtures
now sit under a "fixtures" key with "run" beside it, instead of fixture
names sitting bare at top level. Files written before that date have the old
shape; anything comparing across the boundary should read
`data.get("fixtures", data)`, which handles both. The nesting was chosen
over sitting "run" alongside the fixture keys because a flat top level mixes
metadata with data in one keyspace, and that is a latent collision for the
sake of eyeball-compatibility with three superseded September baselines.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from m7_cv_audit_tool import (
    EXPECTED_RESULTS,
    ContentAudit,
    audit_thumbnail,
    build_content_messages,
)
from provenance import core_provenance

# Called here explicitly rather than relying on build_audit_client() having
# already done it by the time provenance is assembled. The deployment name
# below must be the VALUE that ran, not the env var's name, and reading it
# out of an unloaded environment would silently record "".
load_dotenv()

FIXTURES_DIR = (
    Path(__file__).parent / ".." / "iip-docs" / "m7-riverside-hardware"
).resolve()
RESULTS_DIR = Path(__file__).parent / "results"

FIELDS = ("text_legible", "brand_consistent", "info_accurate")

# text_legible is not one of these -- see the module docstring. Kept as an
# explicit tuple rather than derived by subtraction so that adding a fourth
# field to the rubric forces a deliberate decision about which side it lands
# on instead of silently defaulting to "judged".
MODEL_JUDGED_FIELDS = ("brand_consistent", "info_accurate")
DETERMINISTIC_FIELDS = ("text_legible",)

# 7, not the usual 5 -- matches the manual batch Gerard already ran by hand
# on 2026-09-01 (item2's info_accurate split 4/3 at n=5-ish, close enough to
# a coin flip that the extra 2 runs are worth it for a real characterization
# of whichever wording is live when this runs).
RUNS = 15
STABLE_THRESHOLD = 0.8

# The confabulation check, added 2026-09-11 with ContentAudit.observed_colors.
# item3 contains no cream, and before the observed_colors field the model
# asserted an "orange/cream palette" for it on 15 runs of 15 -- a green verdict
# reasoned from the brand guide rather than from the image. Checking it by
# hand means reading 15 prose strings and deciding what counts, which is how a
# result gets graded by whoever is looking. This makes it an assertion instead.
#
# It is a SEPARATE, NAMED measurement, not a pass/fail bolted onto the verdict
# tally: a wrong description under a right verdict is exactly the case this
# probe previously could not see, and rolling the two together would hide it
# again from the other side.
ABSENT_COLOR_CHECKS = {
    "item3-tool-rental-FLAW-legibility.png": "cream",
}


def observed_colors_of(notes: str) -> str:
    """Pull the [observed] fragment back out of the merged notes string.

    audit_thumbnail() concatenates three labelled fragments into one `notes`
    field so the orchestrator's tool contract does not move. This probe wants
    one of them on its own. Splitting the string here, rather than widening
    audit_thumbnail()'s return shape for the probe's convenience, keeps the
    tool contract the reason it is shaped the way it is.
    """
    for line in notes.splitlines():
        if line.startswith("[observed] "):
            return line[len("[observed] "):]
    return ""


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
            "observed_colors": observed_colors_of(actual["notes"]),
        })
        print(f"  {fixture_name}: "
              f"{ {field: actual[field] for field in FIELDS} }")

print("\n=== Stability summary ===")

judged_correct = judged_total = 0
deterministic_correct = deterministic_total = 0

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

        # Per-cell, not per-majority: the cell total is what "225/225" style
        # figures have always counted, and a majority-only tally would hide a
        # 14/15 the way a 15/15 does not.
        correct_cells = sum(1 for v in values if v == expected[field])
        if field in MODEL_JUDGED_FIELDS:
            judged_correct += correct_cells
            judged_total += RUNS
        else:
            deterministic_correct += correct_cells
            deterministic_total += RUNS

        print(f"  {field}: {true_count}/{RUNS} True ({agreement:.0%}) -- "
              f"{status}, majority={majority} ({match_note})")

print("\n=== Verdict cells ===")
print(f"  model-judged:  {judged_correct}/{judged_total} correct "
      f"({', '.join(MODEL_JUDGED_FIELDS)})")
print(f"  deterministic: {deterministic_correct}/{deterministic_total} correct "
      f"({', '.join(DETERMINISTIC_FIELDS)} -- Read + WCAG arithmetic, "
      f"invariant by construction)")
print("  Report these separately. A combined figure counts the deterministic "
      "cells as if a model had gotten them right.")

print("\n=== Perception check (absent colors) ===")
perception = {}
for fixture_name, absent_color in ABSENT_COLOR_CHECKS.items():
    runs = raw_results.get(fixture_name, [])
    hits = [r["run"] for r in runs
            if absent_color.lower() in r["observed_colors"].lower()]
    perception[fixture_name] = {
        "absent_color": absent_color,
        "runs_naming_it": hits,
        "count": len(hits),
        "of": len(runs),
    }
    verdict = "CLEAN" if not hits else "CONFABULATED"
    print(f"  {fixture_name}: names '{absent_color}' in {len(hits)}/{len(runs)} "
          f"runs -- {verdict}")
    if hits:
        print(f"    runs: {hits}")
print("  This is independent of the verdict tally above. A fixture can be "
      "15/15 correct there and still be described wrongly, which is the whole "
      "reason this section exists.")

RESULTS_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
out_path = RESULTS_DIR / f"{timestamp}_fixture_stability.json"

# The live prompt is READ OUT OF THE FUNCTION THAT BUILDS IT, not copied.
# m7-orientation.md's item 2 named "no copy of the clause wording that was
# live" as part of this probe's provenance gap, and a pasted copy closes that
# gap only until someone edits the prompt and not the copy. build_content_
# messages() takes an image_b64 it embeds in the user turn; "" is passed
# because only the system turn is wanted and no call is made.
content_system_prompt = build_content_messages("")[0]["content"]

with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "run": core_provenance(
            script=Path(__file__).name,
            extra={
                # No agent and no judge in this probe -- audit_thumbnail()
                # makes one chat-completions call against the CV deployment.
                # Named here rather than in provenance.py precisely so that no
                # shared function can assert a judge that never ran.
                "audit_deployment": os.environ.get(
                    "CHAT_DEPLOYMENT_GPT_5_4_MINI", ""),
                "runs": RUNS,
                "stable_threshold": STABLE_THRESHOLD,
                "model_judged_fields": list(MODEL_JUDGED_FIELDS),
                "deterministic_fields": list(DETERMINISTIC_FIELDS),
                "content_schema_fields": list(ContentAudit.model_fields),
                "content_system_prompt": content_system_prompt,
                "note": ("no agent and no judge in this run: those fields are "
                         "omitted because none applied, not because they were "
                         "unknown. temperature=0 and seed=42 are pinned inside "
                         "audit_thumbnail(); text_legible is not model-judged."),
            },
        ),
        "totals": {
            "model_judged_correct": judged_correct,
            "model_judged_total": judged_total,
            "deterministic_correct": deterministic_correct,
            "deterministic_total": deterministic_total,
        },
        "perception": perception,
        "fixtures": raw_results,
    }, f, indent=2)

print(f"\nSaved: {out_path}")
