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
