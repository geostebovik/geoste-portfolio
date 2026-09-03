# Content Item Plan — M7 Synthetic Set (Riverside Hardware & Supply)

**Status:** written before any drafting, generation, or evaluation code runs —
same discipline as `loan-agreement-expected-output.md`. This is the rubric M7's
computer-vision audit and evaluator harness get graded against: for each item
below, the "Expected result" row is what a correct pipeline run should find.
If a run disagrees with this table, that's a finding to investigate, not
something to quietly wave through.

Five items: two clean controls (prove the audit doesn't flag things that are
actually fine — a false-positive check, not just a true-positive one) and three
items each carrying exactly one planted flaw, one per audit dimension named in
`STATUS.md`'s M7 scope (brand consistency, legibility, info accuracy).

---

## Item 1 — "How to Mix Exterior Paint Colors at Home"

- **Planted flaw:** none (clean control)
- **Thumbnail:** on-brand orange/cream palette, legible text, no factual claims
  in the image that could contradict the fact sheet
- **Expected result:** description drafts clean and grounded; CV audit passes
  on all three dimensions (brand, legibility, info accuracy)

## Item 2 — "Seasonal Maintenance Checklist for Homeowners"

- **Planted flaw:** none (clean control)
- **Thumbnail:** on-brand orange/cream palette, legible text, no factual claims
- **Expected result:** same as Item 1 — clean pass across the board

## Item 3 — "Tool Rental 101: What We Offer"

- **Planted flaw:** legibility
- **Thumbnail:** low-contrast text overlay on a busy/cluttered background —
  readable to a human only with effort, if at all
- **Expected result:** CV audit should flag legibility specifically; brand
  and info-accuracy dimensions should still pass (this item isolates one
  failure mode, not a pile of unrelated problems)

**Measured outcome (2026-09-03) — RESOLVED, but not by the CV-audit's
original method. Two entries below: the failed approach, then the fix. The
expected result above never changed.**
Across four `probe_fixture_stability.py` runs the `text_legible` cell has
returned 0/7, 6/7, 5/7 and 3/7 `True` against an expected 0/7, including a
3/7 swing between two runs on a byte-identical image with an identical
prompt. Both levers are exhausted:

- *Prompt-side.* The Sep 3 notes are cleanly bimodal with no hedging. All
  four `False` runs apply the per-element rule correctly ("the business name
  ... is readable, but the other overlaid text in the center ... is too faint
  and blended into the background"); all three `True` runs assert flatly that
  the headline "can be read", with no effort acknowledged. The `False` runs
  are not following the rule better — they are seeing something the `True`
  runs do not see at all. When the pixel decode succeeds the model has no
  notion that recovery was hard, so no wording can make it report effort it
  never experienced.
- *Fixture-side.* The clutter pattern sets the contrast floor. Composited
  over `#FD5A1E` at 0.55 opacity the tiles land at 1.003:1 and **1.128:1**,
  so a title matching the background exactly is *worse* (1.128:1 worst-case)
  than the optimum `#F86A2E` (**1.065:1**). Best achievable with clutter is
  1.065:1 against 1.191:1 today, and the model already recovers text at
  1.191:1.

**The finding:** a legibility flaw must be perceptible-but-hard *for a
human*, which is precisely the regime where an LLM-as-judge has no analogue.
Pushed past it to genuinely invisible, the fixture stops testing legibility
and starts testing absence — a different check. So `text_legible` is not
reliably measurable **by an LLM-as-judge**. The expected result stays as
written because the audit still *should* flag legibility; moving the answer
key to match the data is the goalpost move rejected on item1 the same day.
`brand_consistent` and `info_accurate` are unaffected — both 7/7 correct on
all five fixtures across three runs.

**Resolution the same day: the check was assigned to the wrong kind of
tool.** Contrast is computable, so the judgment moved out of the model and
only the perception stayed in it — Azure AI Vision Read locates each text
element, and `m7_legibility_check.py` measures WCAG contrast inside the word
polygons against the 3:1 large-text minimum. Same answer every run. First
full run, all five fixtures, all five verdicts correct:

| fixture | title | brand | other | verdict | expected |
|---|---|---|---|---|---|
| item1 | 14.46 | 4.95 | | True | True |
| item2 | 3.03 | 4.64 | | True | True |
| item3 | **1.24** | **2.97** | | **False** | **False** |
| item4 | 7.01 | 5.56 | | True | True |
| item5 | 14.46 | 4.95 | badge 3.03 | True | True |

Measured values match `build.py`'s declared colors exactly on 9 of 11
elements; the two that drift (item3's title by 0.05, its brand line by 0.02)
are the only two with the clutter pattern behind them, which is where a third
color population intrudes on the two-population assumption. Minimum OCR word
confidence corroborates independently and was never used for the verdict:
0.93–0.99 on every passing element, **0.32** on item3's headline, which Read
also transcribed wrong ("What We Offer" → "what tye Offer").

**Two margins recorded here rather than fixed:**

1. **item2's title clears by 0.032** (3.032:1 against a 3:1 bar), and item5's
   badge sits at the same value for the same color pair. Both verdicts are
   correct and the measurement on those fixtures is exact, so they are stable
   in practice — but they are clean controls on a knife edge. Any change to
   those fixtures, or any move to the 4.5:1 normal-text bar, flips them.
   Deliberately not "fixed": changing a control that returns the right answer
   is the goalpost move rejected on item1.
2. **item3's brand line fails at 2.949:1 and was never planted.** item3's
   verdict is still correct, but the notes name two failing elements where
   this document says the item "isolates one failure mode." Documentation,
   not a defect.

## Item 4 — "Key Cutting While You Wait"

- **Planted flaw:** brand consistency
- **Thumbnail:** dominant color scheme is blue/gray — clearly outside the
  orange/cream family, not a borderline or "close enough" case
- **Expected result:** CV audit should flag brand consistency specifically;
  legibility and info-accuracy should still pass

## Item 5 — "Propane Tank Refill Safety Tips"

- **Planted flaw:** info accuracy
- **Thumbnail:** text overlay reads "Open 24/7" — directly contradicts the
  fact sheet's Mon–Sat 8am–6pm hours
- **Expected result:** CV audit should flag info accuracy specifically (the
  in-image claim vs. the fact sheet); legibility and brand should still pass

---

## Why one flaw per item, not multiple

Isolating exactly one planted issue per flawed item makes the audit results
unambiguous to grade — a wrong flag is either a false positive (control items)
or a missed/misattributed flag (flawed items), with no ambiguity about which
dimension caused a given result. Bundling multiple flaws into one thumbnail
would make it impossible to tell whether the CV module caught the right thing
for the right reason.

## Design constraint for future items (added 2026-09-01)

`info_accurate`'s check wording (`m7_cv_audit_tool.py`, `build_audit_messages()`)
now exempts headlines/titles that merely name a topic from being treated as
checkable assertions. This was fixed after item2's own headline, "Seasonal
Home Maintenance Checklist", kept getting misread as an implied service claim
— a 43% false-positive rate on a supposedly clean control, confirmed stable
under pinned `temperature=0`/`seed=42` (not sampling noise).

**Consequence: any future item's planted info-accuracy flaw must live in a
separate visible text element — a callout, a stated-hours line, a footer
claim — not inside the item's own headline/title.** Item5's "OPEN 24/7"
callout is the pattern to copy: it's visually and structurally distinct from
the item's headline ("Propane Tank Refill Safety Tips"), so it isn't caught
by the headline exemption. A headline that itself states the false claim
(e.g. a title like "Open 24/7 — Come By Anytime") would likely get waved off
under the current wording as "just a title, not a checkable assertion" — the
same escape hatch that fixed item2.
