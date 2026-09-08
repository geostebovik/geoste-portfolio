# Content Item Plan — M7 Synthetic Set (Riverside Hardware & Supply)

**Status:** written before any drafting, generation, or evaluation code runs —
same discipline as `loan-agreement-expected-output.md`. This is the rubric M7's
computer-vision audit and evaluator harness get graded against: for each item
below, the "Expected result" row is what a correct pipeline run should find.
If a run disagrees with this table, that's a finding to investigate, not
something to quietly wave through.

Items 1-5 are the CV-audit set: two clean controls (prove the audit doesn't
flag things that are actually fine — a false-positive check, not just a
true-positive one) and three items each carrying exactly one planted flaw, one
per audit dimension named in `STATUS.md`'s M7 scope (brand consistency,
legibility, info accuracy).

**Items 6 and 7 were added 2026-09-08 and are a different category** — they
plant their flaw in the *topic*, for `evaluate_draft` to catch, not in the
thumbnail. See "Text-path items 6 and 7" below. The 5x3 audit matrix items 1-5
define is unchanged by them, and stays the figure prior runs are compared
against.

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

## Text-path items 6 and 7 (added 2026-09-08)

**A different category from items 1-5, deliberately.** Every item above
plants its flaw in the *thumbnail*, for the CV audit to catch. These two plant
it in the *topic*, for `evaluate_draft` to catch. They exist because
`INSTRUCTIONS_V3`'s remediation clauses -- the two-redraft cap, "replace
unsupported claims with supported ones", stop-on-pass -- have **zero
observations**: both V3 runs passed every item on the first draft, so the
entire redraft branch has never executed. Certifying a path that has never run
certifies nothing, which is why the multi-run pass is gated behind these.

**Why a plan change and not just a run.** Forcing the failure requires a topic
the fact sheet cannot support, and the topic set is specified here. That makes
this the same fixture-vs-answer-key decision item 1 turned on (2026-09-03),
and it was made deliberately: **add items, do not move existing ones.** Moving
an existing topic would have destroyed a graded cell in a 5x3 matrix that has
returned 15/15 twice, and each of the five has a stated job here -- two
controls, three single planted flaws. None was spare.

**Why a false-premise topic works.** It fails through one of two doors and
there is no third. Either the agent restates the unsupported premise, and
`GroundednessEvaluator` marks it down against this fact sheet; or it writes
around the premise, and `RelevanceEvaluator` marks it down, because the query
passed to that evaluator has the topic embedded verbatim and the response no
longer answers it. Either door sets `all_passed` false, which is the field the
instructions branch on. What separates item 6 from item 7 is whether the
topic's **spine** is supported or only its **details**.

**Both reuse `item1-paint-mixing-CLEAN.png`.** No fixture is re-rendered and
`build.py` is untouched -- deliberate, because a naive rerun of `build.py`
risks putting fresh pixels under item3's 1.19:1 contrast margin (see item 1's
rebuild note). `audit_thumbnail()` never receives the topic, so the audit
verdict is unaffected by the mismatch. **Known confound, accepted and recorded
rather than fixed:** the agent *does* see a paint-mixing thumbnail attached to
a tool-rental topic and may remark on the mismatch in its report. That is noise
in the prose, not in the graded cells.

## Item 6 — "Tool Rental Pricing: Daily and Weekly Rates Explained"

- **Planted flaw:** text-path, **recoverable**
- **Thumbnail:** `item1-paint-mixing-CLEAN.png` (reused clean control)
- **Where the flaw lives:** the spine is supported -- this fact sheet lists
  "Tool rental (daily and weekly rates)" as a service. The *details* are not:
  it carries no prices at all, and "Rates Explained" demands numbers. A draft
  that answers the topic as asked has to invent figures.
- **The substitution the redraft has available:** the daily/weekly rate
  structure itself, the phone number (555) 014-7742 for current rates, and
  Mon-Sat 8:00 AM - 6:00 PM. This is what makes the item recoverable, and it
  is the specific clause under test -- *replace* unsupported claims with
  supported ones, rather than only deleting them.
- **Expected result:** first `evaluate_draft` call fails; the agent redrafts
  and the run ends passed, within the cap of two. Redraft count of 1 or 2 are
  both correct. CV audit passes all three dimensions.
- **Pre-registered branches, all three recorded before the run.** Item 6 sits
  in a regime no run has yet touched: fact sheet present, topic spine
  supported, specific details absent. `INSTRUCTIONS_V3`'s two 15/15 runs used
  fully supported topics; `INSTRUCTIONS_V2`'s collapse had no fact sheet at
  all. So the item is a measurement whose value does not depend on it failing,
  and **the direction of any correction is not knowable in advance** -- which
  is why the topic was not pre-emptively hardened. Registering the direction
  along with each branch is the point:
  1. **Fails, then recovers within the cap.** The intended observation. The
     substitution clause and stop-on-pass are exercised; nothing to change.
  2. **Passes on the first draft.** The fixture is too weak, not broken. It
     would mean clause 4 is stronger than the fixture -- a finding worth
     reporting. Correction: a **harder** topic, built from the draft text and
     the judge's `reason` this run persists. Not a rewritten answer key.
  3. **Fails and never recovers; the cap fires.** The fixture is too strong --
     it has become a second item 7, and leaves substitution and stop-on-pass
     still unobserved. Correction: an **easier** topic, in the opposite
     direction from branch 2.
  Branches 2 and 3 call for opposite corrections, so pre-emptively "raising
  the odds of failure" would be a coin-flip on the sign of the error. A
  hardened topic also stacks a second unsupported element on the first, which
  makes a fail-to-fail result ambiguous between "the cap fired correctly" and
  "the topic was unsatisfiable" -- a compound variable, and the mistake the
  Sep 2 audit split was implemented with frozen wording to avoid.

## Item 7 — "Meet the Riverside Crew: The People Behind the Counter"

- **Planted flaw:** text-path, **unrecoverable**
- **Thumbnail:** `item1-paint-mixing-CLEAN.png` (reused clean control)
- **Where the flaw lives:** the spine itself is unsupported, and this fact
  sheet says so in its own words -- "Out of scope ... No employee names, no
  ownership history." There is no judgment call about whether the topic is
  supportable; the ground truth declares it absent.
- **The substitution available:** none. That is the point.
- **Expected result:** all three drafts fail, the two-redraft cap fires
  (3 `evaluate_draft` calls, `redrafts` = 2), the agent keeps the third draft
  per clause 7, and the final line is `FLAGGED FOR REVIEW` naming the text
  check. CV audit still passes all three dimensions.
- **Pre-registered alternative, recorded before the run:** the agent may
  refuse to draft at all and name the missing facts, the way item3 did under
  `INSTRUCTIONS_V2` on 2026-09-07. **That is correct behavior and a different
  result** -- it would leave the cap still unobserved, and the follow-up would
  be a topic the agent will attempt but cannot satisfy, not a rewritten
  instruction. Registering both branches here, before the run, is what stops
  the reading of the result from being decided by whichever one arrives.

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
