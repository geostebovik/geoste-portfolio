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

**Items 6, 7 and 8 were added 2026-09-08 and are a different category** — they
plant their flaw in the *topic*, for `evaluate_draft` to catch, not in the
thumbnail (item 8 is a reproduction control rather than a flaw fixture). See
"Text-path items 6-8" below. The 5x3 audit matrix items 1-5
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

## Text-path items 6-8 (added 2026-09-08, v1 superseded the same day)

**A different category from items 1-5, deliberately.** Every item above plants
its flaw in the *thumbnail*, for the CV audit to catch. These plant it in the
*topic*, for `evaluate_draft` to catch. They exist because `INSTRUCTIONS_V3`'s
remediation clauses -- the two-redraft cap, "replace unsupported claims with
supported ones", stop-on-pass -- have **zero observations**: every V3 run has
passed every item on the first draft, so the entire redraft branch has never
executed. Certifying a path that has never run certifies nothing, which is why
the multi-run pass is gated behind these.

**Why a plan change and not just a run.** Forcing the failure requires a topic
the fact sheet cannot support, and the topic set is specified here. That makes
this the same fixture-vs-answer-key decision item 1 turned on (2026-09-03),
and it was made deliberately: **add items, do not move existing ones.** Moving
an existing topic would have destroyed a graded cell in a 5x3 matrix that has
returned 15/15 twice, and each of the five has a stated job here -- two
controls, three single planted flaws. None was spare.

**All reuse `item1-paint-mixing-CLEAN.png`.** No fixture is re-rendered and
`build.py` is untouched -- deliberate, because a naive rerun of `build.py`
risks putting fresh pixels under item3's 1.19:1 contrast margin (see item 1's
rebuild note). `audit_thumbnail()` never receives the topic, so the audit
verdict is unaffected by the mismatch. **Known confound, accepted and recorded
rather than fixed:** the agent does see a paint-mixing thumbnail attached to an
unrelated topic and may remark on it in its report. Noise in the prose, not in
the graded cells.

### What the first attempt taught, and why these topics changed

**Run `20260908-115858` -- both v1 items passed on the first draft.** The v1
design rested on a claim that turned out to be false: that a topic the fact
sheet cannot support must fail groundedness. Measured results:

| v1 item | topic | groundedness | relevance | redrafts |
|---|---|---|---|---|
| item6 | Tool Rental Pricing: Daily and Weekly Rates Explained | 4.0 | **3.0** | 0 |
| item7 | Meet the Riverside Crew: The People Behind the Counter | 4.0 | 4.0 | 0 |

**Three things follow, and they are what these v2 topics are built on.**

1. **`INSTRUCTIONS_V3` is designed to prevent the failure being observed.** A
   compliant agent answers any answerable topic honestly and passes. v1 item6
   never invented a price -- it wrote "explains that the store offers daily and
   weekly rates", asserting only that rates exist. Clause 4 held exactly as
   written. So the first draft can only fail if the *honest* answer fails, and
   there are two doors: the honest answer contradicts the fact sheet (it will
   not -- clause 4 stops it), or the honest answer is **too thin to be
   responsive**. Only the second door is reachable.
2. **Groundedness forgives unsupported *generalities*; it penalises
   unsupported *specifics*.** v1 item7's topic is declared out of scope by
   `fact-sheet.md` itself, and it still scored 4.0 -- higher than item6. The
   judge named the gap and excused it: *"adds a general claim about 'team
   behind the counter' without specific employee details (which is fine since
   none exist in scope)."* The agent then padded with grounded but off-topic
   material -- the full services list, the phone number verbatim -- and
   relevance rated the whole thing 4.0 for aligning with the theme. **The
   evaluators score the draft as a whole, not the topic-specific claims**, so
   padding defeats both. **n=1**; item8 exists to test whether it reproduces.
3. **Recoverability is not about whether the topic is answerable.** It is about
   whether **unused grounded material exists to thicken the redraft with** --
   which is V2's 2026-09-07 collapse read in reverse, where the agent stripped
   because it had nothing to add.

**The measured lever.** v1 item6's relevance came in at exactly 3.0 against a
threshold of 3 -- the lowest score anywhere in that run, sitting on the bar.
One notch lower and it fails. So the v2 design pushes on responsiveness, not on
supportability, and it pushes from a measured starting point rather than a
guess. This is what running the v1 fixtures as designed bought: had they been
pre-emptively hardened that morning, this number would not exist.

## Item 6 — "Propane Tank Refill: Sizes, Prices and Turnaround"

- **Planted flaw:** text-path, **recoverable**. v2, replacing the tool-rental
  pricing topic that scored 4.0/3.0 and passed.
- **Thumbnail:** `item1-paint-mixing-CLEAN.png` (reused clean control)
- **Where the flaw lives:** `fact-sheet.md` says exactly four words on this
  service -- "Propane tank refill". The topic demands three specific dimensions
  and the fact sheet supplies none of them, so an honest draft is nearly empty
  *on the topic*. This attacks responsiveness, the one door the v1 run proved
  is reachable, rather than supportability, which it proved is not.
- **The substitution the redraft has available:** hours, phone number, address,
  the tagline, brand voice, and the four adjacent services -- all unused by a
  thin first draft. This is what makes the item recoverable, and it is the
  clause under test: *replace* unsupported claims with supported ones, rather
  than only deleting them.
- **Expected result — RE-REGISTERED 2026-09-09 (Gerard's call). Branch 2
  fired, and this item is now a well-posed control rather than a recoverable
  failure.**
  **Now:** first `evaluate_draft` call **passes**; run ends passed; CV audit
  passes all three dimensions. Redraft count is not pinned — item6 drew a
  groundedness 2.0 once in 30 runs and recovered on one redraft, and a rare dip
  is measured variance, not an answer-key failure, so 0 and 1 are both the
  system working.
  **Previously:** "first `evaluate_draft` call fails; the agent redrafts and the
  run ends passed, within the cap of two."
  **Why it changed, and why this is not the goalpost move rejected on item 1.**
  Two findings retired the original design. (a) The relevance **step function**:
  a supported spine scores 3.0 and passes however much specificity the topic
  demands; an absent spine scores 2.0 and cannot recover. The condition that
  produces a first-draft failure is the same one that prevents recovery, so a
  recoverable-failure fixture may be **structurally impossible** in this design.
  (b) Measured at n=30 on 2026-09-09: item6 passes on the first draft **29 times
  out of 30**. Branch 2 below anticipated exactly this and said the honest
  conclusion might be that the fixture cannot be made to fail on a well-formed
  topic — that is the conclusion, reached after two topics rather than assumed.
  Item 1's rejected move was bending an answer key to excuse a defective
  fixture. This fixture is not defective; it is doing something real that it was
  not built for. **It is the well-posed control that made the Sep 9 judge
  comparison readable** — all three judge deployments returned groundedness
  4.0 ×10 and relevance 3.0 ×10 on it, which is what established that the judge
  is exact where the question is well-posed and divergent only where it is not.
  That is worth more than a recoverable-failure fixture nobody can build.
  **What is lost, stated plainly:** there is now no fixture that exercises
  fail-then-recover by design. The remediation clauses are still observed — the
  cap and keep-the-third on item7, stop-on-pass twice on item6 — but by variance,
  not by construction. Any future claim about the redraft path rests on those
  variance-driven observations, and the judge-isolation probe showed a fixed
  failing draft passes 7 of 10 re-reads unchanged, so a recovery is not by itself
  evidence a redraft worked.
- **Pre-registered branches — RESOLVED 2026-09-09: branch 2 fired.** Kept
  verbatim below because the pre-registration is what makes the outcome
  attributable: branches 2 and 3 called for opposite corrections, so reading them
  after the fact is not the same as having written them before.
  1. **Fails, then recovers within the cap.** The intended observation.
  2. **Passes on the first draft.** Fixture still too weak. Correction: harder
     again — and at that point the honest conclusion may be that
     `INSTRUCTIONS_V3` cannot be made to fail on a well-formed topic, which is
     itself the reportable result.
  3. **Fails and never recovers.** Overshot into item 7's territory.
     Correction: **easier**, the opposite direction from branch 2.
  Branches 2 and 3 call for opposite corrections, which is why the topic was
  moved one measured step rather than as far as it would go.
- **Subject overlap with item 5 is coincidental and harmless** — item 5 is a
  CV-audit item on a different thumbnail, and every item runs on its own
  thread, so nothing is shared between them.

### item 6 at n=21 — `20260908-143613`

The v2 topic was run 21 times through `probe_orchestrator_stability.py`.

| measure | result |
|---|---|
| first-draft relevance | **3.0 x19, 2.0 x2** (runs 13, 15) — dip rate 9.5% |
| first-draft groundedness | 4.0 x21, zero variance |
| distinct first drafts | **19 of 21**, at `AGENT_TEMPERATURE=0` |
| stop-on-pass | fired on runs 13 and 15; **only run 15 is unambiguous** |

**The step function is confirmed, and item 6 is confirmed to sit exactly on the
step.** 19 of 21 first drafts landed on 3.0 — the threshold itself — which is
what makes this fixture useful and also what makes it a poor pass/fail control:
its verdict is decided by a coin-flip-adjacent margin, not by the design.
Deliberately not "fixed", per item 1's precedent: the expected row still says
what a correct pipeline should produce.

**What it bought.** The redraft branch was reachable after all — not by making
the topic harder, which two attempts showed does not move relevance, but by
running the borderline fixture enough times for variance to push a draft under
the bar. Run 15: draft 1 at 2.0, one redraft, draft 2 at 3.0, stopped with a
call to spare.

**What it did not settle.** The judge's primary criticism was identical on both
drafts, and the variance on this cell is the same size as the score movement, so
the recovery is unattributable. See `m7-orientation.md`'s Backlog.

**Design constraint this adds:** a fixture whose expected verdict depends on a
score landing exactly on the threshold is not a control — it is a coin flip with
a documented bias. Any future text-path item should be designed to land clear of
the bar in one direction, and item 6 should be read as a variance instrument
rather than as a pass/fail cell.

## Item 7 — "Our Price-Match Guarantee and Return Policy"

- **Planted flaw:** text-path, **unrecoverable**. v2, replacing the crew topic
  that scored 4.0/4.0 and passed.
- **Thumbnail:** `item1-paint-mixing-CLEAN.png` (reused clean control)
- **Where the flaw lives:** `fact-sheet.md` contains no policies of any kind —
  no price matching, no returns, no warranty, no terms. **Crucially, the
  services list is not a substitute for a policy question**, so the padding
  strategy that rescued the v1 crew topic is transparently non-responsive here
  and relevance should punish it rather than forgive it. That is the specific
  correction the v1 result calls for.
- **The substitution available:** none. That is the point.
- **Expected result:** all three drafts fail, the cap fires (3 `evaluate_draft`
  calls, `redrafts` = 2), the agent keeps the third draft per clause 7, and the
  final line is `FLAGGED FOR REVIEW` naming the text check. CV audit passes.
- **Pre-registered alternative:** the agent may refuse to draft and name the
  missing facts, as item3 did under `INSTRUCTIONS_V2` on 2026-09-07. Correct
  behavior, different result — it leaves the cap still unobserved, and the
  follow-up would be a topic the agent will attempt but cannot satisfy.

## Item 8 — "Meet the Riverside Crew: The People Behind the Counter"

- **Purpose: a reproduction control, not a flaw fixture.** This is the v1
  item7 topic, carried forward **unchanged**, to test whether finding 2 above
  reproduces. One observation against a documented ~2/7 noise floor is a
  hypothesis with a mechanism, not a result.
- **Thumbnail:** `item1-paint-mixing-CLEAN.png` (reused clean control)
- **Expected result — and read this carefully, because it is unlike every
  other row in this document.** The expected row encodes the **observed**
  2026-09-08 behavior (passes first draft, groundedness 4.0, relevance 4.0,
  zero redrafts), **not** a standard of correctness. A `text_matches_expected`
  of True here means *the finding reproduced*; False means it did not. Nothing
  about this row asserts that passing is the right answer — by the design
  intent of the topic, it is the wrong one. Registering it this way is what
  keeps "did it reproduce" separate from "is it correct", which are different
  questions that a single boolean would otherwise conflate.
- **If it reproduces**, the groundedness-forgives-vagueness behavior goes into
  the docs as a property of the evaluator, with the consequence that
  `INSTRUCTIONS_V3` clause 4's "do not compensate by writing vaguely" is not
  enforced by anything downstream of it.
- **If it does not reproduce**, the v1 result was noise and the finding is
  withdrawn, not softened.


### Measured outcome of the v2 topics — run `20260908-133724`

| item | topic | grounded | relevance | redrafts | branch |
|---|---|---|---|---|---|
| 6 | Propane Tank Refill: Sizes, Prices and Turnaround | 4.0 | **3.0** | 0 | **2** — passed first draft |
| 7 | Our Price-Match Guarantee and Return Policy | 4.0 ×3 | **2.0** ×3 | **2** | cap fired as designed |
| 8 | Meet the Riverside Crew (control) | **5.0** | 4.0 | 0 | reproduced |

**item 7 did what it was built to do.** Three `evaluate_draft` calls, the cap
firing at two redrafts, the third draft kept, `FLAGGED FOR REVIEW: text check`.
The correction from v1 was right: a services list is transparently
non-responsive to a policy question, and relevance punished it — 2.0 on every
draft — where it had forgiven the same padding on the crew topic.

**item 6 landed on 3.0 for the second time, and that is the important
number.** The v1 topic scored 3.0; this one demands three specific dimensions
against four words in the fact sheet and also scored 3.0. **Relevance did not
move.** Against item 7's 2.0 the pattern is a step, not a slope: spine
supported → 3.0 → passes however much specificity the topic demands; spine
absent → 2.0 → fails, with nothing to substitute. **So the recoverable-failure
fixture this section was written to build may not exist in this design** — the
condition producing a first-draft failure is the same one preventing recovery.
Recorded rather than tuned, per item 3's precedent. The untried regime is a
**partially supported spine** — a topic half answerable, where a redraft can
drop the unsupported half and lean into the supported one.

**item 8 reproduced at n=2, so the finding stands.** Groundedness rose to 5.0
while the topic remained one `fact-sheet.md` declares out of scope. Combined
with item 7's three drafts, that is five observations of groundedness scoring
4.0-5.0 on drafts its own reason text calls non-responsive. See
`m7-orientation.md`'s Backlog for the consequence.

**Design constraint this adds, alongside the 2026-09-01 one below:** a
text-path item's planted flaw cannot be "the fact sheet does not support this
topic". Groundedness will not fail it. The flaw has to be one relevance can
see — a topic the draft cannot answer — and that lands in the unrecoverable
regime unless the spine is partially supported.

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
