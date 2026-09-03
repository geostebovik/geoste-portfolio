# M7 Orientation — Where Things Stand (start here each session)

**Status:** current-state snapshot only — not a log (that's `STATUS.md`) and
not a plan (that's `agent-system-project-plan.md`). This page answers one
question: "what does the M7 build actually look like right now, and where
does the piece I'm about to touch fit in?" Update this page whenever a piece
of M7 moves from *designed* to *built*, or *built* to *verified* — otherwise
it goes stale and becomes one more untrustworthy doc, which defeats the point
of having it.

## Session-start checklist (added 2026-09-03)

Run these before touching anything. Every item is here because it has already
cost this project a session, a data point, or a wrong answer — none of it is
hygiene for its own sake. Counterpart to the end-of-session reconcile above.

1. **Confirm the folders are actually connected — do not assume they carried
   over.** Two are needed: `C:\Users\gerar\geoste-portfolio\ai-103` for the
   working files, and `C:\Users\gerar\geoste-portfolio` for git, because
   `.git` lives at the repo root and not in `ai-103` — git commands run from
   `ai-103` alone fail with "not a git repository ... stopping at filesystem
   boundary". Claude checks this with `get_device_info` and reads
   `connectedFolders`; one call, start of session. Added Sep 3 after both
   folders had to be requested mid-session despite having been attached when
   the thread was opened — **folder attachment did not survive into the
   session.** The failure is quiet if nobody looks: an attached-but-not-
   connected folder returns directory *names* only, with file contents
   withheld, which reads like a sparse or empty folder rather than an access
   problem.

2. **State the working folder path explicitly in the opening prompt.**
   Standing rule — never assume it from memory — and naming both paths up
   front collapses item 1 into zero approval round-trips.

3. **Run `git status` and `git log` fresh. Distrust the handoff's git
   section.** It has now gone stale twice: once before Sep 2 (flagged in that
   day's own handoff) and again Sep 3, when `STATUS.md` and
   `m7-orientation.md` were described as uncommitted but had already been
   swept up by `3abbae8`. Same root cause both times — the git-state section
   gets written *before* the day's final commit. Writing it last is the fix;
   until then, treat it as a hypothesis and verify.

4. **Read git through the bridge read-only.** `GIT_OPTIONAL_LOCKS=0 git
   --no-optional-locks <cmd>`. Writes through that shell strand `.git` locks
   and temp files (see Backlog). Standing arrangement: Claude prepares the
   commit message, Gerard commits on Windows.

5. **Confirm the working tree matches `HEAD` before taking any
   measurement.** An unexplained delta between the two is how the Aug 31
   unsaved-edit data point got poisoned, and Sep 3 opened with an unstaged
   one-line prompt change that had to be resolved before any run could be
   read. Decide it, do not defer it — a number measured against an
   undocumented working-tree diff is not attributable to anything and cannot
   be re-derived later.

6. **Check the Todoist "IIP — AI-103 Punch List" before assuming what to work
   on.** The punch list is what is *open*; this doc is what is *true*. Read
   both, in that order, and reconcile any disagreement before starting rather
   than at the end.

7. **Read this file — status box, "What's actually left to build", Backlog —
   before the dated session prompt's narrative.** This doc is the map; the
   session prompt is only what changed and what is next. When they disagree,
   this doc wins, and the disagreement itself is a finding worth fixing on
   the spot.

## End-of-session checklist (added 2026-09-02)

Before closing for the day, reconcile the Todoist "IIP — AI-103 Punch List"
against what this session actually resolved — close or update any task a doc
here already documents as done. Added after the `brand_consistent` regression
task sat open in Todoist a full day past `m7-orientation.md` already recording
it as resolved (Sep 1 resolution, caught and fixed Sep 2).

**Write the next handoff's git-state section after the day's final commit, not
before** (added Sep 3). Both recorded staleness incidents trace to that one
ordering mistake — see session-start item 3. A handoff that describes files as
uncommitted which were committed minutes later is worse than one that omits
git state entirely, because it reads as verified.

## Standing lessons worth not relearning (added 2026-09-03)

Consolidated here from the dated session prompts, where they were restated
from memory each handoff and had begun to drift. **Session prompts should now
reference this section rather than re-listing it** — one copy, one place to
correct.

- **Verify the file is saved on disk before running anything.** Cost a suspect
  data point on Aug 31 and nearly cost another on Sep 2. An editor showing the
  change is not the same as the change being on disk.
- **Read every run against the ~2/7 noise floor.** One or two runs out of seven
  is not a result — not an improvement, not a regression. Big effects (the
  7/7 → 0/7 swings that drove the Sep 2 decisions) still are. See the Backlog
  entry that established this.
- **Change one variable at a time.** Standing practice, and the reason the
  split was implemented with both clauses' wording frozen: each clause had
  already been proven correct in *some* configuration, so moving wording and
  structure together would have made the result unattributable.
- **Define the condition that produces the verdict, rather than enumerating
  what shouldn't cause it.** That is what finally fixed `info_accurate`
  ("when nothing legible contradicts the fact sheet, record it as True").
  Blocking wrong paths is endless; naming the right one is bounded.
- **The answer key's language describes the FAILING state.** Lifting it into a
  definition of passing inverts the rule — happened once on Sep 2, caught
  immediately.
- **Test when the answer depends on model behavior you can't predict; reason
  when it's a design choice you can derive.** Both are cheap; confusing them
  is not.
- **Verify a document's structure before citing it.** Claims about what a doc
  contains — a section name, a heading, "it already says X" — get checked
  against the file, not recalled. Added Sep 3 after Claude twice asserted a
  "tooling note" section in *this file* that does not exist (the phrase
  belongs to the dated session prompt) and built a recommendation on top of
  it. Same failure class the CV-audit exists to catch: an assertion past what
  the source supports, delivered in the register of something the source says.

## Where M7 sits in the whole picture

IIP (this repo) is the hands-on lab work behind two things at once: the
AI-103 certification (AZ-900 and AZ-104 already passed, AI-103 is the
current target) and the portfolio site content at ostebovik.net. M7 is the
seventh and final milestone of the IIP lab work — M0 through M6 (Foundry
redeploy, document analyzer, extraction pipeline, RAG Q&A, evaluator
harness) are all done. M7 is the one that combines the largest-weighted
AI-103 exam domain (Generative AI / agentic solutions, 30–35%) with the one
domain none of M1–M6 touched at all: computer vision.

M7 builds a single Foundry orchestrator agent that manages content review
for a synthetic small-business scenario — Riverside Hardware & Supply,
entirely fictional, defined in `fact-sheet.md`. This is deliberately **not**
built against a real client or business — see `agent-system-project-plan.md`'s
"Decoupling note" (Aug 4) for why this was cut loose from the earlier
Anne-Collins-engagement business idea. It's a clean training exercise now,
nothing more.

## The M7 architecture, as designed so far

```
                    Orchestrator agent (Foundry Agent Service)
                    NOT YET BUILT — instructions text + toolset
                              still to design/write
                                      |
                +---------------------+----------------------+
                |                                              |
      Tool 1: draft evaluator                        Tool 2: CV-audit
      STATUS: built + verified                        STATUS: main() written + run
      (wraps m7_evaluator_tool.py)                       live (Aug 29-31). Structured
                |                                        outputs confirmed working
      Uses GroundednessEvaluator +                        against gpt-5.4-mini on the
      RelevanceEvaluator (Azure AI                         bumped API version -- no
      Evaluation SDK)                                      fallback needed.
                |                                      Checks 3 things:
      Checks drafted title/description                   - text_legible
      text against fact-sheet.md                          - brand_consistent
                                                            - info_accurate
                                                            (+ notes: reasoning)
                                                      SPLIT BUILT + RUN (Sep 2).
                                                      Call A: text_legible (no fact
                                                      sheet). Call B: brand + info.
                                                      brand_consistent and
                                                      info_accurate now 7/7 CORRECT
                                                      on all 5 fixtures, verified
                                                      across 3 runs. item1's
                                                      over-claim FIXED + verified
                                                      Sep 3. Only open cell: item3
                                                      text_legible (6/7, 5/7, 3/7
                                                      True; expected 0/7) --
                                                      fixture-side only. See item
                                                      2 below.
```

Both tools check a different *kind* of output against the same ground
truth — `fact-sheet.md` — the same role the loan agreement PDF played for
M5's RAG pipeline. `content-items-plan.md` is the answer key: 5 test items
(2 clean controls, 3 each carrying exactly one planted flaw) that a finished
CV-audit run should score exactly as documented there — that table is what
"done and working" gets measured against, not a vibe check.

## What's actually left to build, in order

1. ~~CV-audit tool wrapper~~ — **done (Aug 28).** `m7_cv_audit_tool.py` has
   the client, `ThumbnailAudit` schema, and `audit_thumbnail()` fully
   written, including the real system/user prompts (Gerard wrote those
   himself as a prompt-engineering exercise). Never run against real Azure.
2. ~~Run `main()`'s fixture test loop~~ — **done (Aug 29-31).** Structured
   outputs (`response_format=ThumbnailAudit`) confirmed working live against
   `gpt-5.4-mini` on the bumped `STRUCTURED_OUTPUT_API_VERSION` -- no
   fallback needed. First live run: 4/5, item3 failed `text_legible` only.
   Root-caused through a reliability/generalization testing process (full
   detail in STATUS.md's Aug 29-31 entries and
   `probe_legibility_variants.py` / `probe_legibility_detail_level.py`):
   the original wording asked whether *any* text was legible, which the
   always-present business-name wordmark trivially satisfied regardless of
   what happened to the manipulated title text -- an existential-vs-universal
   quantifier bug, not a vision-perception limit. Rewrote `text_legible`'s
   wording to require each distinct text element to be judged on its own,
   with an explicit instruction not to let one legible element cover for
   another.
   **`brand_consistent` regression resolved (Sep 1) -- was noise.**
   `temperature=0`/`seed=42` pinned on the audit call specifically to
   settle this, then 7 plain reruns of all 5 fixtures: `brand_consistent`
   never failed on item3 once. Most likely the noise (or the invalid
   unsaved-edit run) already flagged as suspect from the Aug 31 write-up.
   Closed.

   **New finding from those same 7 runs, since fixed: `info_accurate` was
   genuinely unstable on item2 (4 True / 3 False out of 7) even with
   temperature and seed pinned.** `content-items-plan.md` confirmed item2 is
   designed with zero factual claims, so any `False` was a wrong answer, not
   an open question. Root cause: the wording never distinguished a
   topic/headline from an explicit factual assertion, so the model
   inconsistently read item2's "Seasonal Home Maintenance Checklist" title
   as an implied service claim. Wording rewritten (several iterations --
   Gerard drafted, Claude critiqued each pass) to use "assertions" instead
   of "claims"/"offerings" and to explicitly exempt headlines/titles from
   being checkable. Verified via the new `probe_fixture_stability.py` (7
   runs, automated): item2 now 7/7 clean, items 1/4/5 unaffected. See
   `content-items-plan.md`'s "Design constraint for future items" for the
   consequence this has on any new fixture design.

   ~~**`text_legible` on item3**~~ -- **resolved Sep 2.** Fixture strength
   was ruled out first by measuring item3's actual WCAG contrast ratio from
   `build.py`'s colors: **1.19:1**, against a 3:1 large-text minimum -- the
   fixture was never underpowered, so the bar in the wording was the
   problem. Gerard added "or vice versa" (an illegible element can't drag a
   legible one down) plus an explicit bar: "readable by a typical human
   without undue effort or assistance." Result: item3 went 7/7 True to
   **0/7 True (7/7 correctly False)**, right reasoning every run, and
   `text_legible` is now correct and stable on all five fixtures.

   **`info_accurate` regressions -- THIS is the actual next step (Sep 2).**
   The `text_legible` edit above, with no other clause touched, knocked
   `info_accurate` off on two fixtures: **item2 7/7 -> 4/7**, **item3 7/7 ->
   2/7** (baseline diff:
   `results/20260901-145716_fixture_stability.json` vs.
   `results/20260902-103821_fixture_stability.json`). **Cross-check
   contamination is therefore confirmed** -- the three checks share one
   system prompt, and strengthening one instruction outvotes instructions
   near it. The Aug 31 dismissal of contamination for `brand_consistent`
   still stands on its own evidence; what's falsified is the general
   assumption that editing one check can't disturb another. **Standing
   consequence: any wording edit to any check now requires a full
   5-fixture `probe_fixture_stability.py` run, never a single-fixture
   spot check.**

   Three distinct causes behind the failures, from the run's `notes`:
   (a) illegibility contaminating info accuracy -- "too obscured to verify
   all text cleanly ... marking info accuracy as false" (item3 runs 3, 6);
   (b) the Sep 1 headline-as-assertion bug returning verbatim (item2, and
   item3 run 4) -- the exemption is still in the prompt, just outvoted;
   (c) the boolean contradicting its own `notes` (item3 runs 2, 5) -- prose
   reasons to a pass, field says `False`.

   **Outcome (Sep 2 PM): the `info_accurate` edit cleared BOTH regressions
   -- and broke `text_legible` in the reverse direction.** Final wording:
   "When nothing legible contradicts the fact sheet, record it as True"
   (defining the passing condition by what's *absent* rather than what's
   confirmed, so unreadable text drops out of the comparison instead of
   counting as a failed match). item2 `info_accurate` 4/7 -> **7/7**, item3
   `info_accurate` 2/7 -> **7/7** -- and cause (b) resolved without the
   headline exemption being touched at all. But item3's `text_legible`
   reverted 0/7 -> **7/7 True (wrong)** on a clause verified byte-for-byte
   unchanged, with the original bug's reasoning back verbatim ("readable
   despite the low-contrast overlay"). Two edits, 14/15 correct both times,
   a different cell failing each time.

   **DECISION (Sep 2): split the audit into two calls.** The pre-registered
   trigger -- further edits causing regressions elsewhere -- was met. The
   mechanism is salience competition between instructions sharing one
   prompt, not any individual sentence being wrong (proven by cause (b)
   fixing itself when neighboring text changed). Wording tuning has
   unbounded cost with no convergence guarantee; the split has a bounded,
   known one. **Two calls, not three:** every contamination event has been
   between `text_legible` and `info_accurate`; `brand_consistent` was 7/7
   correct on every fixture in every run and never implicated. So
   `text_legible` gets its own call, `brand_consistent` + `info_accurate`
   stay together. Added cost (one extra image upload per audit, two prompts
   to maintain) accepted deliberately.

   ~~**Next step: implement the split with both clauses' wording FROZEN
   as-is.**~~ -- **done Sep 2 PM, see below.**
   Do not tune wording and split in the same step. Each clause has been
   proven correct in some configuration; the split's first probe run tests
   whether both can be correct simultaneously. ~~Open design question to
   decide deliberately: how to merge two reasoning strings into a schema with
   one `notes` field?~~ -- **resolved by the implementation, confirmed against
   live output Sep 3:** prefixed concatenation, `[legibility] ... [content]
   ...`, which keeps per-call attribution without changing the return shape.
   `audit_thumbnail()` still merges into a single `ThumbnailAudit`, so the
   orchestrator's tool contract does not move.
   Cause (c) is unaffected by the split and stays in the backlog.
   **SPLIT BUILT AND RUN (Sep 2 PM) -- it delivered what it was bought
   for.** `m7_cv_audit_tool.py` now makes two calls: `build_legibility_
   messages()` (text_legible only, no fact sheet -- legibility needs no
   ground truth) and `build_content_messages()` (brand_consistent +
   info_accurate, with the fact sheet), merged by `audit_thumbnail()` into
   an unchanged `ThumbnailAudit` so the orchestrator's tool contract does
   not move. Committed as `b8d100a` before its first live run.
   **Result across two split runs: `info_accurate` and `brand_consistent`
   are 7/7 CORRECT on all five fixtures** -- including item3, which the
   combined prompt could never get right at the same time as
   `text_legible`. Wording changes to one check can no longer disturb
   another; that is now structural, not a matter of care.

   ~~**OPEN THREAD 1 -- item1's over-claim (a CLEAN control is
   defective).**~~ -- **CLOSED Sep 3, fixed and verified.** item1's
   `info_accurate` had moved 7/7 -> 5/7 between two split runs with a
   byte-identical content-call prompt; both failing runs blamed the headline
   "Mix Any Exterior Paint Color -- In Store" against `fact-sheet.md`'s
   "Custom paint mixing" (no "any", no "exterior"), making them arguably the
   *more* compliant runs under item1's own rule.
   **Decision: correct the fixture, not the answer key.**
   `content-items-plan.md` already specified item1's thumbnail as having "no
   factual claims in the image" and already titled the item "How to Mix
   Exterior Paint Colors at Home" -- `build.py` was what diverged, on two
   counts. Moving the expected result would have left one clean control
   instead of two, halving the false-positive coverage both controls exist
   to provide. It also removed item1 from the Sep 1 headline-exemption
   boundary: the old headline was an imperative offering claim, not a topic,
   which is why it was *bistable* rather than simply wrong.
   **Verified: `info_accurate` 7/7 (`20260903-104108`) -- and closed on the
   mechanism, not the count**, since `20260902-151734` also read 7/7 before
   drifting. The notes carry it: Sep 2's failures named the string ("the
   visible claim says 'Mix Any Exterior Paint Color -- In Store'"), Sep 3's
   passes route through a different path ("the visible text is a topic/title
   ... no legible claims ... contradict the fact sheet"). That is the
   headline exemption firing as designed.
   **Rebuild method worth reusing.** `build.py` renders all five fixtures in
   one pass, so a naive rerun risked putting fresh pixels under item3's
   1.19:1 contrast margin. Verified rather than assumed: re-rendering the
   *original* item1 in a Linux container reproduced it byte-identically
   (SHA-256), proving the Aug 21 originals were rendered on Linux with
   Liberation Sans, not Windows Arial. The full rebuild then left items 2-5
   byte-identical. Because it ran on Linux, `build.py`'s `/tmp` + naive
   `file://` bug never applied and stays untouched in the Backlog.

   **OPEN THREAD 2 -- item3's legibility threshold. THE ONLY OPEN CELL IN
   THE MATRIX, and prompt-side is now closed off entirely (updated Sep 3).**
   Four split runs have produced 0/7, 6/7, 5/7 and 3/7 True (expected 0/7).
   The Sep 3 run used the *committed* wording -- the same one behind the 6/7
   -- against a byte-identical image, so that is a **3/7 swing on an
   identical prompt**, wider than the 2/7 figure in the Backlog. Do not read
   6 -> 5 -> 3 as a trend: three points, no controlled variable, and the last
   repeated an earlier wording.
   **Do not read the Sep 3 summary line as progress either.** At 3/7,
   `majority = 3 >= 3.5` is False, so the console prints "majority=False
   (matches expected)" for the first time since the split. It is not a pass:
   `agreement` is 43% against `STABLE_THRESHOLD = 0.8`, and the same line
   reads NOT STABLE.
   **What the Sep 3 notes prove -- prompt-side is finished.** That batch is
   *not* the graded boundary seen Sep 2; it is cleanly bimodal with no
   hedging. All four `False` runs apply the per-element rule correctly ("the
   business name ... is readable, but the other overlaid text in the center
   ... is too faint and blended into the background"). All three `True` runs
   assert flatly that the headline "can be read", with no effort
   acknowledged. So the `False` runs are not following the rule *better* --
   they are seeing something the `True` runs do not see at all. When the
   pixel decode succeeds, the model has no notion that recovery was hard, so
   no instruction can make it report effort it never experienced.
   **Reframe (Sep 2, correcting that morning's reasoning; confirmed Sep 3):** the clause asks the model to judge readability
   "by a typical human", but it has no human eye -- it decodes pixel values,
   where item3's 1.19:1 contrast is faint to a person but easy to recover
   numerically. The morning's contrast calculation answered "could a human
   read this?" when the operative question was "will this model call it
   readable?" Hypothesis 1 (fixture not strong enough) was closed on the
   wrong evidence and **is back in play** -- push item3's contrast to
   effectively zero rather than asking the model to simulate an eye. Caveat:
   diag-b/c already returned True at near-zero contrast, but under the old
   quantifier-buggy wording; that combination is untested.

3. **`evaluate_draft()` wrapper** — a thin function around the already-working
   evaluator that returns `json.dumps(...)` instead of a raw dict, with its
   own reST docstring. Small, but not done yet.
4. **Orchestrator instructions text** — the actual job description telling
   the agent when to draft, when to call each tool, and what to do with a
   failing result (redraft? flag for review?). Not yet written.
5. **Wire it together** — `AgentsClient` + `ToolSet` + `enable_auto_function_calls`,
   then run all 5 `content-items-plan.md` items through it and compare actual
   results to the expected-results table.

## Backlog — everything deferred, in one place (per Gerard's Aug 28 preference: no digging through STATUS.md scrollback for these)

Nothing here blocks anything else. Pulled together from scattered
"not urgent" mentions across past sessions plus new ones as they come up —
add new items here going forward instead of leaving them buried in a
session's narrative paragraph in `STATUS.md`.

**M7 / current build:**

- **Harness resolution: a cell can move at least 3/7 between runs on an
  IDENTICAL prompt and image (established Sep 2, revised Sep 3).**
  **Correction:** this entry originally cited item1's `info_accurate` 7/7 ->
  5/7 as its evidence. That movement turned out to have a *cause* -- a
  fixture defect, fixed Sep 3, and the variance went with it. The floor is
  still real, but its supporting example is now item3's `text_legible`,
  which spans 6/7, 5/7 and 3/7 across three runs on the same image with
  `temperature=0`/`seed=42` pinned. **Read every future run against this: a
  1-2 run difference out of 7 is not an improvement or a regression, and on
  a contested cell even 3/7 may not be.** Equally important, and the reason
  the correction matters: **treat unexplained movement as a hypothesis to
  chase first, and call it noise only after chasing it** -- the one case
  this entry documented as irreducible turned out to be diagnosable. Big effects (the 7/7 -> 0/7 swings that drove the Sep 2
  decisions) are still trustworthy; fine-grained wording comparisons need
  more runs or a bigger effect to be readable. Raising `RUNS` in
  `probe_fixture_stability.py` is the obvious lever if a question ever
  genuinely turns on 1-2 runs -- at 2x the calls now that the audit is
  split.
- **Open question deliberately NOT measured: does removing the fact sheet
  from the legibility call matter?** The split changed three things at once
  (checks separated, framing sentence, fact sheet dropped from call A).
  Decided not to spend a run isolating the third, on the reasoning that a
  legibility check which only works when unrelated business context happens
  to be in the prompt is *balanced*, not fixed -- the same accidental
  coupling the split exists to remove. Recorded as a known confound rather
  than a measurement. Revisit only if a fixture-side fix fails too.
- **git WRITES through the desktop bridge strand lock and temp files (Sep
  2).** The split commit left `.git/HEAD.lock`, `.git/objects/maintenance.
  lock` and seven `tmp_obj_*` hard links behind -- that shell cannot unlink
  files in mounted folders, and `HEAD.lock` blocks the next commit. Reads
  are fine with `git --no-optional-locks`; **writes are not.** Standing
  arrangement: Claude prepares the commit message, Gerard commits on
  Windows. Cleanup needs `-Force`: `Get-ChildItem .git\objects -Recurse
  -Filter tmp_obj_* -Force | Remove-Item -Force`.

- **`notes` is not always faithful to the boolean it accompanies (found Sep
  2).** In 2 of 7 item3 runs the prose reasoned explicitly to a pass ("so
  the info check passes for the visible assertions") while `info_accurate`
  came back `False`. Structured outputs guarantee the response *shape*, not
  that the free-text and boolean fields came from the same line of
  reasoning. Close-reading `notes` is still the best diagnostic available
  and found both real bugs to date -- but it is now known to be unreliable
  at roughly 2-in-7 on a contested field, so a conclusion drawn from a
  single run's notes needs a second run before it's trusted. Not fixed by
  splitting the prompt; it's an LLM-as-judge reliability problem, not a
  contamination one.
- ~~**Decision point: split the three checks into separate calls?**~~ --
  **DECIDED Sep 2: yes, into two calls** (`text_legible` alone;
  `brand_consistent` + `info_accurate` together). Trigger condition was met
  the same day it was written: two consecutive wording edits each fixed
  their target and broke a different check. Added cost accepted. Not a
  backlog item any more -- it's the next build step, see "What's actually
  left to build" item 2. Note this does NOT fix the `notes`/boolean
  contradiction above, which is a separate class of problem.
- **`.git/index.lock` files left behind by Claude's desktop-bridge shell
  (diagnosed Sep 2).** Not a repo problem, not VS Code: `git status` run
  through the bridge takes the optional index lock and then can't unlink it
  (that shell is barred from deleting files in mounted folders). Confirmed
  by file ownership, timestamp, and the "unable to unlink ... Operation not
  permitted" warning in the command's own output. Fix: `git
  --no-optional-locks status` / `GIT_OPTIONAL_LOCKS=0` for read-only
  queries from that shell; stale locks get deleted from Windows.
- **Normalize `CHAT_API_VERSION` across the project (added Aug 28).**
  `m7_cv_audit_tool.py` pins its own `STRUCTURED_OUTPUT_API_VERSION` at
  `"2024-08-01-preview"` (needed for structured outputs) instead of using
  the shared `CHAT_API_VERSION` (`"2024-06-01"`, in `.env`) that M5/M6 and
  the rest of M7 depend on. Deliberate, not sloppy — bumping the shared
  version now would touch already-verified pipelines without re-testing
  them. Once M7 is done and stable: bump `CHAT_API_VERSION` deliberately,
  then re-run M5/M6's existing verification steps to confirm nothing
  regressed before treating it as done. Worth checking at that point
  whether to converge on Azure OpenAI's newer GA `v1` API surface instead
  of just picking a newer dated preview string, since preview versions are
  more likely to get retired later.
- **Ungrounded embellishment in `description-template.md`'s own worked
  example (flagged Aug 27).** Its reference example includes "matched to
  any swatch or sample you bring in" and "we'll mix it while you shop" —
  neither is stated in `fact-sheet.md`'s Services list. Confirmed real
  against the fact sheet directly, not just a judge-model guess. Small,
  cosmetic, doesn't block anything — it's the template's own example text,
  not something a real drafted item inherited.

**CV-audit investigation threads (added Aug 31, none block the regression fix above):**

- **Diagnostic-variant findings, not yet fully closed.** Four controlled
  thumbnail variants built (`iip-docs/m7-riverside-hardware/
  build_legibility_diagnostics.py`, deliberately separate from the official
  `build.py`/`ITEMS` content) isolating one variable at a time: diag-a
  (heavy clutter), diag-b (near-zero title/background contrast), diag-c
  (title color pushed as close to background as CSS would render), diag-d
  (3px title font). Clutter and gradual contrast were both ruled out as
  causes -- even diag-b/c returned `text_legible: True` under the original
  wording, confirming the real bug was the quantifier issue fixed above, not
  a vision-perception limit. Two open threads: (1) diag-d showed genuine
  1-in-4 run-to-run variance under the corrected wording
  (`probe_legibility_variants.py`, 5 runs/variant, 80% stability threshold)
  -- worth more runs before treating either diag-c or diag-d's boundary as
  settled; (2) a drafted-but-untested wording addition for the
  "expected-but-absent" case ("if a headline/title element would normally
  be expected and none is visibly distinguishable from the background,
  treat that as illegible, not merely absent") was considered for diag-c
  specifically and never applied or tested.
- **`"detail": "high"` on the image_url content ruled out as a cause.**
  Tested via `probe_legibility_detail_level.py` against diag-c/d at default
  vs. high detail -- results were consistent with the quantifier-bug
  explanation, not detail level. Not worth revisiting unless the regression
  investigation turns up something that specifically implicates it.
- ~~`temperature` unpinned in `m7_cv_audit_tool.py`~~ — **decided and done
  (Sep 1).** Pinned `temperature=0`/`seed=42` on the audit call, ahead of
  the brand_consistent reruns rather than after -- see `STATUS.md`'s Sep 1
  entry for why that ordering mattered. Neither param guarantees bit-exact
  determinism on Azure OpenAI, just substantially reduces variance (item2's
  `info_accurate` still swung 4/7-3/7 under pinning before its wording got
  fixed -- pinning narrows the noise, doesn't eliminate every source of it).
  Test scripts (`probe_*.py`) still don't pin it -- worth doing if any of
  them get reused for a real stability question rather than a one-off
  screen.
- **General confabulation risk in vision-judgment `notes` fields --
  partially closed.** `info_accurate`'s `notes` got the same close-reading
  treatment as `text_legible` did originally (Sep 1) and surfaced a real
  bug: the model was reading item2's headline as an implied service claim.
  Fixed -- see item 2 in "What's actually left to build" above. `
  brand_consistent`'s `notes` still haven't been examined this closely --
  it passed clean 7/7 in the Sep 1 batch, so there's no active reason to,
  but the general risk (confabulating plausible-sounding justification
  rather than grounded evidence) hasn't been ruled out there, just hasn't
  shown up yet either.
- **`build.py`'s own `/tmp` + naive `file://` string-concat bug, not
  fixed.** `build_legibility_diagnostics.py` had the identical bug
  (hardcoded `/tmp` path, `"file://" + path` string concatenation instead
  of a proper file URI) and was fixed using `tempfile.gettempdir()` +
  `pathlib.Path.as_uri()` -- see the new `python-patterns.md` entry.
  `build.py` itself, the official content-generation script, still has the
  same bug, left deliberately untouched since this session's diagnostic
  work didn't need to touch it. Will bite the moment it's run on Windows
  without WSL/Cloud Shell.
- **Test/QA script naming convention adopted, not retroactive.** New
  descriptive test/QA scripts now use a `probe_<what-it-tests>.py` pattern
  (e.g. `probe_legibility_variants.py`, `probe_legibility_detail_level.py`)
  instead of `testerN.py`. Existing `tester.py` / `tester2.py` /
  `tester3.py` are staying as-is -- no retroactive rename or doc-churn on
  already-closed artifacts.

**M6 infra (carried forward from Aug 6, none block M5/M7):**

- **`m6_assemble.py` confirmation output.** Prints which generate-results
  file it read, but nothing confirms `m6_eval_input.jsonl` actually got
  written — add a "Saved: ..." print matching `m6_generate.py`'s pattern.
  Worth also writing the source generate-results filename into
  `m6_eval_input.jsonl` (or a sidecar), since there's currently no way to
  trace which generate-run produced a given eval input after the fact
  without checking timestamps by hand.
- **`m6_evaluate.py`'s hardcoded judge deployment.** `azure_deployment=
  "gpt-5-2"` is still hardcoded directly in `model_config()`, unlike the
  other deployments, which read from `.env`. `CHAT_DEPLOYMENT_GPT_5_2` now
  exists in `.env` (added Aug 26) — migrating this is just a consistency
  fix at this point, not blocked on anything. Still optional; the script
  works as-is.
- **CRLF line endings in `m6_assemble.py` and `m6_generate.py` — confirmed
  still present as of Aug 28**, not just historically flagged: `file`
  reports both as CRLF right now, despite `.gitattributes` covering `*.py`
  since Aug 6. Fix per-file with `git add --renormalize <file>` (explicit
  paths, not a repo-wide pathspec — a repo-wide renormalize already swept
  up unrelated files once this project, caught before committing).
- **cwd-relative paths in `m6_generate.py` and `m6_assemble.py`.** Both use
  paths relative to the terminal's current directory (`"../iip-docs/..."`),
  which only work when launched from exactly `scripts/` — hit directly
  once already as a `FileNotFoundError`. Fix: base paths on
  `Path(__file__).parent`, the pattern every M7 script already uses.

**M5 (complete, these are polish, not gaps in what M5 proved):**

- **Generalize `m5_retrieve.py`'s hardcoded test question.** Currently a
  fixed string in `main()`; a CLI arg or an `input()` prompt would make it
  reusable for more than one question without editing the file.
- **Whether M5's retrieval quality needs systematic evaluation beyond the
  one manual spot-check already done.** If it ever does, M6's
  evaluator-harness pattern (`Groundedness`/`Relevance`/`F1Score`) is the
  proven template to reuse — not proposed as work to do now, just a known,
  real gap rather than an assumed non-issue.

## Which doc answers which question

| Question | Doc |
|---|---|
| What happened last session, and why? | `STATUS.md` |
| What's the full multi-phase plan / business context behind M7? | `agent-system-project-plan.md` |
| How does a Foundry concept (agent/thread/tool/FunctionTool) actually work? | `agent-service-primer.md` |
| What's the ground truth for Riverside Hardware content? | `iip-docs/m7-riverside-hardware/fact-sheet.md` |
| What result should each test item produce? | `iip-docs/m7-riverside-hardware/content-items-plan.md` |
| What CLI command do I need for X? | `iip-cli-runbook.md` |
| What does the system look like right now, and where do I pick up? | **this file** |
