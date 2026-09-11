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

**Log the session under its own `### Session — <date>` heading in `STATUS.md`,
and *replace* `## Current next action` rather than appending to it** (added Sep
6). This is the rule the Sep 6 restructure exists to enforce: `## Next action`
had quietly absorbed ~1,650 lines of session log across Aug 21 – Sep 4 because
each session appended its notes there instead of opening a heading, and the
`## Session —` headings stopped dead at Aug 20. It cost nothing per session and
a full cleanup session to undo.

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
- **Read what a scheduled task wrote before letting it stand.** Added Sep 7,
  after the Friday check-in's first run. It did good work — it found that
  "What's actually left to build" was reading as empty while two real next
  items sat in the Backlog, and promoted them — and in the same commit it
  added a dated weekly-log section to a file whose own header says it is a
  current-state snapshot and not a log, and recorded "the schedule needs
  checking" about a run that had been fired manually on purpose. Both were
  stated with the same confidence as the correct findings. **An unattended
  task cannot know what it was not told, and it commits anyway.** Treat its
  output as a hypothesis and diff it before it is pushed — the same standing
  lesson that applies to Claude's assertions, arriving from a scheduled task
  instead.
- **Check that the actor can see what the grader sees.** Added Sep 7, and it
  cost a whole instructions version. `INSTRUCTIONS_V2` told the orchestrator to
  ground every claim in `fact-sheet.md` while the fact sheet reached only the
  judge and the CV audit — an open-book exam where the grader has the book and
  the student does not. The agent behaved rationally: it removed everything it
  could not verify until the copy said nothing, and one item declined to act
  and named the missing document. The symptom looked like four separate
  problems (groundedness stuck, relevance collapsed, redrafts exhausted, one
  item refusing) and was one cause. **Before instructing an agent to comply
  with a source, confirm the agent has the source.**
- **An instruction must not contradict the tool's own documented contract.**
  Added Sep 7. `INSTRUCTIONS_V2` told the agent to pass a bare topic as
  `evaluate_draft`'s `query`; that function's docstring says in as many words
  not to, and predicts the exact failure that followed. The clause was written
  to remove a real variance, and standardised on the one value documented as
  broken. **Read the tool before writing the instruction that calls it** — and
  note the sting in the tail: the warning was in the docstring but truncated
  out of the schema, so the agent had never seen it either. Neither party was
  reading the contract.
- **`temperature=0` does not make an Agents-SDK run repeatable.** Added Sep 8,
  correcting an assumption Claude reasoned from rather than checked. 21 runs of
  one item at `AGENT_TEMPERATURE=0` produced **19 distinct drafts** — the SDK
  exposes temperature and top_p but no `seed`, so temperature narrows the
  distribution and does not collapse it. Consequence: any claim that "the
  drafting is pinned, so the variance must be judge-side" is unsupported, and
  separating the two needs a probe that removes the agent from the loop.
- **Do not infer a gradient from a single point sitting on a threshold.**
  Added Sep 8. A relevance score of 3.0 against a threshold of 3 looked like a
  fixture that was nearly hard enough, so the plan was to push the topic
  harder. A second topic in the same regime, demanding far more specificity,
  returned 3.0 again — it is a step function, not a slope. The right reading of
  a value sitting exactly on a bar is "this may be where the function lands",
  not "one more nudge will tip it".
- **Run the fixture you designed before improving it.** Added Sep 8, and it
  was Gerard's call against Claude's suggestion. Pre-emptively hardening item6
  that morning would have destroyed the baseline: with no observation of the
  original, no later result could be attributed to the change. The three
  pre-registered branches called for **opposite** corrections depending on the
  outcome, so acting early was a coin flip on the sign of the error. Running as
  designed is what produced the threshold measurement, the groundedness
  property and the step-function finding — none of which would exist otherwise.
- **A crashed item is not a failed item, and must never share a denominator
  with one.** Added Sep 8 after an Azure `server_error` killed item1 mid-run
  and its three unmeasured cells scored as three wrong verdicts, reading 12/15.
  In a multi-run certification pass that reads as instability in a tool that
  was correct on every fixture it reached.
- **The bridge and Windows disagree about line endings, and VS Code
  under-reports what changed.** Added Sep 8, two separate failures on one day.
  See the two Backlog entries; both point the same way — **`git status` in
  PowerShell is the authority**, not VS Code's Source Control view and not git
  read through the bridge.
- **Before blaming a shared component, vary the one thing you have not varied.**
  Added Sep 9, and it cost three revisions of one finding in a single day.
  Groundedness scoring 1.0 and 4.0 on interchangeable drafts was written up as a
  property of `GroundednessEvaluator` — a component shared by every run — on the
  strength of 30 observations. All 30 were on ONE judge deployment. Ten calls each
  on two others showed gpt-5-4 returning 4.0 every time, so the evaluator was
  behaving exactly as documented and the model underneath it was not. **n was
  never the problem; the design was.** Thirty runs of a single condition cannot
  distinguish a property of the component from a property of the configuration —
  only a second condition can, and it took ten calls.
  **The tell to watch for:** a finding phrased as "X does Y" where X is
  infrastructure everything shares. That phrasing is only earned once X has been
  observed under more than one configuration.
- **n=3 is not a distribution, and a clean run of identical values is the
  easiest thing to over-read.** Added Sep 9. Sep 8 recorded item7's groundedness
  as 4.0 three times and generalised it into a property of the evaluator
  ("groundedness does not measure responsiveness"). Thirty runs found the same
  cell ranging 1.0–4.0, and three consecutive 4.0s from that distribution has
  probability 0.081 — uncommon, not remarkable. **Repetition across a handful of
  runs is not stability; it is a small sample that happened to agree.** The tell
  is that the Sep 8 claim was stated as a mechanism, which is exactly the register
  that discourages anyone from re-testing it.
- **State the test before quoting the p-value, and check which baseline it
  compares against.** Added Sep 9, Claude's error. Before the V4 run Claude
  predicted 0/60 clean first drafts would land at p≈0.0025 — computed by treating
  the 9.5% baseline as a KNOWN rate. The honest comparison is against the actual
  2-of-21, which gives Fisher p=0.065. An order of magnitude, in the flattering
  direction, on the number that decides whether a fix gets called proven. **A
  baseline estimated from two events cannot support a confident denominator.**
- **The instrument can over-claim too, and it does it silently.** Added Sep 9.
  `probe_judge_isolation.py`'s first `compare()` collapsed a nuanced result into
  a binary and printed "Reads as retry-until-lucky" on ranges that touched at a
  single point while describing 7/10 against 10/10. Every over-claim this project
  logs was a person or a model asserting past the evidence; this one was compiled
  in and would have been quoted as output. **A verdict string in a script is a
  claim, and needs the same scrutiny as a sentence in a write-up** — including a
  legitimate "cannot tell" branch, because an instrument with no way to say that
  will always say something else.
- **Read each new finding against "what does this change?" before spending a
  thread on it.** A finding worth one backlog line gets one backlog line.
  Added Sep 6, promoted out of the Sep 4 session prompt before that prompt was
  replaced. Sep 2, 3 and 4 all went into characterising tools that were
  already passing their answer key, while the orchestrator — the
  largest-weighted AI-103 domain and the entire reason M7 exists — sat
  unbuilt. It then took one afternoon. The asymmetry is structural: a
  model-judged check can always be probed one run further, and probing is
  more interesting than building, so the drift is toward analysis and away
  from the thing being analysed.
- **A pass rate is not evidence of a working check. Read the reasoning behind
  the passes.** Added Sep 10, and it is the day's largest finding. `item3`'s
  `brand_consistent` read 12/15 correct — and several of those twelve passes
  asserted "the thumbnail uses an orange/cream palette" about an image
  containing **no cream at all**. The three failures observed the image
  correctly and applied the wrong rule; the twelve passes reached the right
  verdict from a false observation. A cell that agrees with its answer key is
  not thereby sound, and the agreement figure cannot tell the two apart —
  only the `notes` can. **Whenever a check is being trusted rather than
  merely tallied, sample its stated reasons by eye.** The same caveat already
  stands on `check_meta_commentary.py` for a different reason; this is the
  general form.
- **A clause that says what to FLAG without saying what PASSES will be read
  two ways.** Added Sep 10, and it has now fixed three checks, which makes it
  the most load-bearing lesson in this file. `info_accurate` was settled by
  "When nothing legible contradicts the fact sheet, record it as True".
  `text_legible` was settled by moving the judgment out of the model entirely.
  `brand_consistent` failed on exactly the same defect: it asked whether the
  palette *was* orange/cream, listed what to flag, then added exemptions —
  and never said what passing looked like. The slash between "orange" and
  "cream" was read as AND on 3 of 15 runs. **Both branches, explicitly:
  record True when X; record False only when Y.** "Only when" makes the rule
  total; without it the model fills the gap itself, differently each time.
- **An instruction can lose to its own source — and can also beat it.** Added
  Sep 10, extending the Sep 2 salience-competition finding from
  instruction-versus-instruction to instruction-versus-source. The content
  call receives `fact-sheet.md`, which states the brand rule precisely ("any
  thumbnail using a materially different palette (e.g. blue/gray) as its
  DOMINANT SCHEME is a violation"). The clause restated that rule more weakly
  and more strictly at once. The model held both, and on 3 of 15 runs the
  weaker restatement won. **A clause that restates its source must not be
  stricter than the source, or the two compete and the model arbitrates.**
- **Do not let one number carry two assumptions.** Added Sep 10, Claude's
  error. "30K TPM" was questioned as a SETTING — correctly, which is how the
  970K of unallocated quota was found — and in the same breath accepted as a
  BOTTLENECK, which it is not: the run is serially latency-bound at ~20K TPM
  sustained. The arithmetic that settles it (16K tokens ÷ 47 seconds) was
  available in the smoke-run result already read and quoted. **Questioning a
  figure's provenance is not the same as questioning its consequence.**
- **Commit before you measure — especially on an instrument with no
  provenance.** Added Sep 10, correcting advice Claude gave the same
  afternoon. Claude first proposed holding a clause change and committing it
  together with its verification result "as one change", which optimises for
  tidy history at the cost of attributability. `probe_fixture_stability.py`
  records **no provenance at all** — no `git_head`, no `git_dirty`, no
  deployment, no record of the wording that was live — so the commit history
  plus a filename timestamp is the *only* link between a run and the code
  that produced it. Dirty-tree measurement is unattributable in general; on an
  instrument like this one it is unrecoverable.
- **A total rule can only ever flag one thing — that is the price of making it
  total.** Added Sep 10, Gerard's observation, and it refines the lesson above
  rather than qualifying it away. The rewritten `brand_consistent` works
  because "Record as False ONLY when..." leaves the model no gap to fill with
  a standard of its own. But "only" also forecloses every other violation
  type: `fact-sheet.md`'s brand guide names a logo ("a simple toolbox icon, no
  wordmark flourishes") as well as colours, and under this clause a correct
  palette with a wrong logo is forced to True. **The check is named
  `brand_consistent` and now judges the colour scheme alone.** Deliberately
  accepted Sep 10, because no current fixture isolates a non-palette brand
  violation — all five carry the same toolbox — so broadening the clause would
  be a change no run could verify. **The response to an untested gap is a
  fixture, not a wording change.**

### A stopping rule must be specified in the instrument's own units, above its noise floor

Found 2026-09-11, and it is a lesson about Claude's error, not the project's.

Before the `observed_colors` run, Claude pre-registered an abort: *any verdict
regression → revert the change.* One cell moved (item2 `info_accurate`, 15/15 →
14/15) and the rule triggered on a result carrying no information at all. At
n=15 those two outcomes are indistinguishable, and the probe's own standard —
`STABLE_THRESHOLD = 0.8` — reports 14/15 as STABLE with the majority matching
expected.

**An ad-hoc bar stricter than the instrument that prints the result is not
discipline, it is a trigger that fires on noise.** The error is visible without
reference to which way the data went, which is the only thing that made amending
it an amendment rather than a goalpost move.

The rule: state a trigger in the units the instrument reports. "Any regression"
is not a trigger. "Majority flips, or agreement drops below 0.8" is.

### Schema position is an instruction, and a field description does not compete with prompt prose

Found 2026-09-11 while fixing `brand_consistent`'s confabulation.

Two mechanisms, both structural rather than verbal, and both cheaper than
another wording pass:

1. **Structured outputs generate in field order.** Declaring `observed_colors`
   BEFORE `brand_consistent` forces the model to write what it sees before it
   commits to a verdict. The same field declared after the verdict would be
   describing a conclusion already reached — which is the failure mode, not a
   fix for it.
2. **An instruction in a pydantic `Field(description=...)` has its own slot.**
   Prose added to the system prompt competes for salience with the verdict
   clauses beside it — the mechanism that forced the Sep 2 split, twice
   observed. A schema field cannot be outvoted by a neighbouring sentence, and
   it leaves the prompt text byte-identical, so verdict movement in the
   verifying run cannot be blamed on wording.

Generalization of the Sep 2 decision: **when wording tuning has unbounded cost,
look for the structural version of the same instruction.**

### A tool's "contract" covers its schema, not the content its callers read

Found 2026-09-11. `audit_thumbnail()` returns an unchanged `ThumbnailAudit`, so
adding `observed_colors` was described as contract-preserving. That is true of
the shape and false of the content: `notes` is a string the orchestrator agent
reads AND republishes in its own prose summary, and it now carries an extra
paragraph on every item.

**Anything a downstream consumer reads is part of the contract, whether or not
the type signature moved.** The consequence here was benign — the agent
reproduces it verbatim without confusion — but it is the reason the Sep 11
orchestrator re-certification was worth running rather than assuming.

### Do not change the machine's power or network state during a long unattended run

Found 2026-09-11, the expensive way. A 15-run orchestrator pass died at minute
18 of 95 with `ConnectionResetError 10054`, and `Kernel-Power` event 105 four
seconds earlier named the cause: the laptop was undocked. The dock's ethernet
adapter disappeared and every socket bound to it died mid-request.

**The change-one-variable rule applies to the physical layer too.** A pass that
costs ninety minutes should be started docked, on mains power, and then left
alone — and the machine's state during it belongs in the session notes the same
way a wording edit does.

Retries now absorb this (see `ITEM_ATTEMPTS` in `m7_orchestrator.py`), which
makes it survivable rather than fatal. It is still not free: each failure costs
four attempts and up to 35 seconds of backoff before the row is abandoned.

### An exception is not an `unmeasured` row, and the instrument could not tell

Found 2026-09-11 from the same crash. `unmeasured()` records "the run completed
but produced no verdict." An SDK exception never reaches the code that writes
that row — it propagates out of `run_item()`, out of the probe's item loop, and
ends the process.

So the crash-path gap tracked in the Backlog since Sep 8 was mis-stated. It was
not "this path has no observations yet." It was **"one whole category of failure
cannot produce an observation,"** and nobody noticed because nothing had crashed
that way yet.

**The general form: when an instrument has a hole, check whether the hole is
missing data or missing reachability.** Those need different fixes, and only the
second one gets worse the longer it goes unnoticed.

### The desktop shell failure is a Windows update, not this project's configuration

Settled 2026-09-11 by the experiment the Sep 11 session prompt pre-registered.

`no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared`. Both
hypotheses are dead:

- **Nesting ruled out.** One folder attached (repo root only, no `ai-103`),
  identical failure.
- **Desktop build ruled out.** The Sep 10 prompt named 1.49585.0 as the next
  suspect; Sep 11 ran 1.52386.0 and failed identically.

The error now names its own cause: *"A Windows update released September 8
prevents Claude's workspace from reaching your files. We're tracking this issue.
Claude Code is unaffected."* Host-side and vendor-tracked. **Stop spending
session time on it.**

**Unrelated to the Surface Book DTX fault**, despite both timelines containing
Sep 8. Two faults, same week, no shared cause — do not let either become
evidence about the other.

Working consequence: no git, no python, no probe runs from Claude's side; files
read and written through the bridge only. The standing "Gerard runs the
commands" arrangement now covers everything, and **his availability at the
keyboard is the binding constraint on a session, not elapsed time.** Say which
in the opening prompt.

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
                    BUILT + RUN Sep 4. INSTRUCTIONS TEXT DONE Sep 7 --
                    m7_orchestrator.py registers THREE tools via ToolSet +
                    enable_auto_function_calls, temperature pinned to 0
                    (the Agents SDK has no `seed` parameter at all, so runs
                    are narrowed, never repeatable).
                    ACTIVE: INSTRUCTIONS_V4 (2026-09-09). V4 = V3 plus two
                    clauses, built by .replace() with asserts so the diff is
                    provably those two and nothing else: clause 4 forbids
                    mentioning the fact sheet/instructions/process in copy,
                    clause 7 gives the redraft loop a legal move when nothing
                    is supportable (draft the best-supportable copy and allow
                    the check to fail). Measured: 0/53 redrafts and 0/60 first
                    drafts referencing the fact sheet, over 30 runs.
                    V3 scored 15/15 on two consecutive runs; its redraft path
                    is now fully observed. V1 (throwaway) and V2 (regressed to
                    12/15) are kept unused; provenance records which version
                    each run used, which is why V3 was restored byte-for-byte
                    rather than edited in place on Sep 9.
                                      |
                +---------------------+----------------------+
                |                                              |
      Tool 1: draft evaluator                        Tool 2: CV-audit
      STATUS: built + verified                       STATUS: BUILT + VERIFIED
      (wraps m7_evaluator_tool.py)                   (m7_cv_audit_tool.py)
                |                                              |
      Uses GroundednessEvaluator +                   HYBRID as of Sep 3 --
      RelevanceEvaluator (Azure AI                   one measured check, two
      Evaluation SDK)                                judged ones:
                |                                      - text_legible
      Checks drafted title/description                   DETERMINISTIC: Vision
      text against fact-sheet.md                         Read locates text,
                                                         m7_legibility_check.py
                                                         measures WCAG contrast
                                                         vs 3:1. No model
                                                         judgment. 5/5 correct.
                                                       - brand_consistent
                                                       - info_accurate
                                                         one model call w/ the
                                                         fact sheet; 7/7 correct
                                                         on all 5 fixtures
                                                         across 3 runs
                                                       (+ notes: [legibility]
                                                         and [content] merged
                                                         into one ThumbnailAudit)

                                                     ALL 15 CELLS NOW CORRECT.
                                                     History: split into 2 model
                                                     calls Sep 2 (cross-check
                                                     contamination); item1's
                                                     over-claim fixed Sep 3;
                                                     text_legible moved out of
                                                     the model entirely Sep 3.
                    Tool 3: get_fact_sheet (m7_fact_sheet_tool.py)
                    ADDED Sep 7. Returns fact-sheet.md verbatim to the
                    AGENT. Until then the fact sheet reached the judge and
                    the CV audit but never the drafter, while the
                    instructions told it to ground everything in that
                    document -- an open-book exam where only the grader had
                    the book. That is what INSTRUCTIONS_V2's 12/15 was.
                    Whole file, deliberately: the judge grades against the
                    whole file, and a curated subset would reintroduce the
                    same drafter/grader mismatch in miniature.
```

The two checking tools each check a different *kind* of output against the same
ground truth — `fact-sheet.md` — the same role the loan agreement PDF played for
M5's RAG pipeline. Since Sep 7 the drafter is measured against a document it can
also read. `content-items-plan.md` is the answer key: 5 test items
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

   ~~**OPEN THREAD 2 -- item3's legibility threshold.**~~ -- **CLOSED Sep 3
   BY SOLVING IT, via a different attack vector.** The first conclusion that
   day was to accept the limitation and move on; it was superseded within the
   hour by a better one. Both levers *inside the model-judged approach* were
   genuinely exhausted (evidence below) -- but that proved only that the check
   had been assigned to the wrong kind of tool, not that it was unmeasurable.
   **Contrast is computable.** So the judgment moved out of the model and only
   the perception stayed in it: Azure AI Vision Read locates each text
   element, `m7_legibility_check.py` measures WCAG contrast inside the word
   polygons against a 3:1 large-text minimum. **Result: 5/5 fixtures correct,
   deterministic, the same answer every run** -- on the cell that had produced
   0/7, 6/7, 5/7 and 3/7. Full numbers and two recorded margins live in
   `content-items-plan.md` item 3.
   **The lesson worth carrying: move the judgment out of the model and leave
   the perception in it.** OCR is a task with a ground truth, which models are
   reliable at; "would a human find this hard to read" is not. The dead end
   recorded below is kept deliberately -- the evidence in it is what justified
   the redesign.
   **Prompt-side was closed on evidence.** Four split runs produced 0/7, 6/7,
   5/7 and 3/7 True (expected 0/7).
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
   **Fixture-side is closed too -- measured Sep 3, not assumed.** The clutter
   pattern sets item3's contrast floor. Composited over the `#FD5A1E`
   background at 0.55 opacity, the tile colors land at `#f1662d` (1.003:1 vs
   bg) and `#f77439` (**1.128:1** vs bg), so a title matching the background
   *exactly* is worse (1.128:1 worst-case) than the true optimum `#F86A2E`
   (**1.065:1**). Best achievable with clutter present is 1.065:1, against
   1.191:1 today -- and the model already recovers text at 1.191:1. "Push the
   contrast to effectively zero" is **not reachable while the clutter
   exists**, and removing the clutter is a *plan* change, since
   `content-items-plan.md` specifies a "busy/cluttered background" (the same
   fixture-vs-answer-key distinction Thread 1 turned on).
   **The conceptual problem underneath, which is the actual finding.** A
   legibility flaw has to be perceptible-but-hard *for a human*, and that is
   exactly the regime where the model has no analogue -- it decodes pixels
   and has no notion that recovery was hard. Push the fixture past that
   regime to genuinely invisible and it stops testing legibility and starts
   testing *absence*, which is a different check needing the untested
   expected-but-absent clause. So `text_legible`, as specified, is not
   reliably measurable by an LLM-as-judge on this fixture -- and that is a
   result worth reporting, not a cell to tune until it turns green. Recorded
   in `content-items-plan.md` under item 3; its expected result was
   deliberately **not** changed, since the audit still *should* flag
   legibility -- moving the answer key to match the data is the goalpost move
   Thread 1 rejected.

   **ITEM 2 IS COMPLETE (Sep 3).** All 15 cells of the 5x3 matrix now
   return the expected value: `text_legible` 5/5 deterministic,
   `brand_consistent` and `info_accurate` 7/7 each across three runs.
   `m7_cv_audit_tool.py` lost 96 lines in the surgery -- the
   `LegibilityAudit` schema and `build_legibility_messages()` are gone, and
   the "readable by a typical human without undue effort or assistance"
   clause went with them rather than being frozen. `ThumbnailAudit` is
   unchanged, so the orchestrator's tool contract never moved. New files:
   `m7_legibility_check.py` (the measurement + `audit_legibility()` entry
   point) and `probe_read_ocr.py` (the Read smoke test).

3. ~~**`evaluate_draft()` tool wrapper**~~ — **DONE Sep 4, verified live.**
   `evaluate_draft()` is now `-> str` ending in `json.dumps(...)`, with a reST
   docstring that is the tool schema the orchestrator reads. A `_flatten()`
   helper drops the SDK's `_properties` payload -- it carries the full judge
   prompt including `fact-sheet.md` verbatim, roughly 3,900 tokens per call
   (SDK-reported `prompt_tokens` 2,026 + 1,848) to deliver about 1 KB of
   signal. Score, `passed` and `threshold` are the SDK's own values; no
   threshold is invented. Non-finite scores are coerced to `null` because
   `json.dumps` emits a bare `NaN`, which is not valid JSON and would reach
   the agent unparseable. Claude wrote it; Gerard ran it and approved the
   wording changes. The pre-Sep-4 text of this item follows.

   **NOTE (corrected Sep 3): the
   function itself already exists and works.** `m7_evaluator_tool.py` line 45
   has `evaluate_draft(query, response) -> dict`, verified live Aug 27. This
   entry previously read "not done yet", which was wrong. What is missing is
   the *tool-shaped* version: a `json.dumps(...)` return (Foundry's auto
   function calling needs a string to put back in the thread, not a dict) and
   a reST docstring with `:param:`/`:return:`. **The docstring is not
   documentation here -- it IS the tool schema the orchestrator reads to
   decide when to call this tool**, and `evaluate_draft()` currently has no
   docstring at all.
4. ~~**Orchestrator instructions text**~~ — **DONE Sep 7 as
   `INSTRUCTIONS_V3`.** Claude drafted; Gerard owned the wording, made every
   decision below, and wrote the redraft clause's operative fix. Three
   versions, and the middle one regressed — the arc is the finding.

   **V1** was the deliberate throwaway: call both tools, silent on failure.
   It scored 15/15 on the audit and never exercised a redraft, because
   nothing failed on the text side that morning.

   **V2 regressed to 12/15 on two bugs, both Claude's.** (a) It instructed
   the agent to ground every claim in `fact-sheet.md` — a document the
   orchestrator had never been given, since the fact sheet reaches the judge
   and the CV audit only. The agent stripped every unverifiable specific
   until the copy was empty, groundedness sat at 2.0, relevance fell 4.0 →
   2.0 for being uninformative, and item3 refused to act, correctly naming
   the missing fact sheet. The redraft clause ("remove, and do not add detail
   to compensate") could only subtract with no source to add from.
   (b) The `query` clause told the agent to pass a bare topic, which
   `evaluate_draft`'s own docstring explicitly forbids — "a bare title scores
   as an unanswered question" — written to close a variance and standardised
   on the one broken value.

   **V3 fixed both and scored 15/15 twice, 5/5 text checks, zero redrafts.**
   `get_fact_sheet()` is a third tool rather than inlined text — **Gerard's
   call**, on his standing preference for the tool-shaped option, and the
   better fit for AI-103's largest domain. The redraft clause now substitutes
   rather than only subtracts (**Gerard's wording**). The `query` clause uses
   the exact sentence the tool's docstring specifies — still zero variance,
   now the correct constant.

   **The four Sep 4 observations, as V3 answers them.** Report-only is the
   default and every part of remediation is instructed (observation 1, as
   corrected Sep 7 — the agent advises on passes, not failures). Redrafting
   is capped at two and stops on pass (observation 2, still unobserved — see
   Backlog). `description-template.md` is enforced in the instructions rather
   than by a fourth tool (observation 3), and every CTA now carries real
   hours or the real phone number. Tool output must be quoted exactly,
   garbled OCR included (observation 4) — confirmed working: the Sep 7 runs
   quote 1.24:1 and "Tool Rental 101 what tye Offer" verbatim.

   **What is NOT settled by this item being done:** the redraft path has zero
   observations, the certification pass is unrun, and the orchestrator's model
   was never chosen deliberately. All three are Backlog entries below, and the
   first is `STATUS.md`'s current next action.

5. ~~**Wire it together**~~ — **DONE Sep 4. First run returned 15/15.**
   All five items matched their expected row exactly; both tools were called
   on every item. The reST docstrings functioned as tool schemas on the first
   attempt, on a function that had no docstring at all that morning. Claude
   wrote the script and predicted a messy first run; Gerard cleared the config
   and ran it. Config note: `AIF_PROJECT_ENDPOINT` is the account's
   `services.ai.azure.com` host plus `/api/projects/<project>`, from the
   portal's project Overview -- the CLI's `properties.endpoints` is
   account-level and does not contain it. Details of the original scaffolding
   follow.

   **SCAFFOLDED Sep 4, not yet run.**
   `m7_orchestrator.py` (Claude wrote it) builds the `AgentsClient` against
   the *project* endpoint with `DefaultAzureCredential`, registers both tools
   in a `ToolSet`, calls `enable_auto_function_calls`, and runs each of the
   five `content-items-plan.md` items **on its own thread** -- deliberate, so
   one item's draft and tool results cannot sit in context while the next is
   drafted, the same contamination the Sep 2 audit split removed. It prints
   which tools the agent actually called, per item, against that item's
   expected-results row.
   **Blocked on two config items, both Gerard's:** `AIF_PROJECT_ENDPOINT` is not
   in `.env` (the project endpoint, not the account endpoint M2-M6 use), and
   `azure-ai-agents` / `azure-identity` were added to `requirements.txt` but
   not yet installed. `DefaultAzureCredential` also means this is the first
   M7 script to authenticate as Gerard rather than by account key, so an
   RBAC gap on the project surfaces here first.

6. ~~**Get one clean observation of a failing `evaluate_draft`.**~~ —
   **CLOSED 2026-09-09.** All four clauses are now observed, and the open
   question underneath the item is answered.
   - **Observed Sep 8:** the two-redraft cap and keep-the-third-and-report
     (`20260908-133724` item7); stop-on-pass (`20260908-143613` run 15, n=1).
   - **Observed again Sep 9:** stop-on-pass a second time
     (`20260909-122233` item6 run 30) — and the dip was GROUNDEDNESS (2.0) this
     time rather than relevance, where V3's was relevance. **n=2.**
   - ~~"replace unsupported claims with supported ones" degenerated to
     meta-commentary~~ — fixed by `INSTRUCTIONS_V4`, 0/53 redrafts. See the
     Backlog.
   - **The question that kept this open is answered, and it inverted.** The
     redraft loop re-rolls: a fixed failing draft passes 7 of 10 re-reads
     unchanged. So a pass after a redraft is not evidence the redraft worked, a
     higher cap raises the false-pass rate, and `final_text_passed` is not the
     number to certify on. Full detail in the Backlog entry and `STATUS.md`'s
     Sep 9 session.

7. ~~**Certify — on pass/fail, not on scores.**~~ — **DONE 2026-09-10.** Ran as
   `probe_orchestrator_stability.py --runs 15` over all eight items:
   `results/20260910-123321_orchestrator_stability.json`, at `git_head 87b37cd`,
   clean tree, `model_deployment` and `judge_deployment` both `gpt-5-4`,
   `INSTRUCTIONS_V4`, temperature 0. An 8x1 smoke ran first
   (`20260910-104818`) and matched all eight rows.
   - **120 item-runs, zero crashes, zero `unmeasured`.** So `unmeasured()`
     STILL has no observation against a real crash — a clean run is not a test
     of the crash path. Unchanged in the Backlog.
   - **Text verdict layer: 117/120 matched the pre-registered rows, and 118/120
     is correct BEHAVIOUR** — item6's two misses are correct catches, not
     errors. Its topic asks for sizes, prices and turnaround the fact sheet
     lacks; the agent promised them, groundedness caught it at 2.0, the redraft
     passed. On those drafts relevance rose to 4.0 while groundedness fell to
     2.0 — the two evaluators traded off correctly without being told to.
   - **Audit rows: 117/120**, all three failures in one cell —
     `brand_consistent` on item3. Root-caused, clause rewritten, re-verified
     the same day (`results/20260910-142656_fixture_stability.json`,
     5 fixtures x 3 fields x 15 runs, `RUNS` raised from 7). **Reported at the
     time as 225/225; that figure is retired.** `text_legible` has been
     deterministic since Sep 3 — Read plus WCAG arithmetic — so 75 of those 225
     cells cannot vary, and counting them as model answers overstates the
     result. Restated in corrected units: **150/150 model-judged cells plus 75
     deterministic.** Sep 11's run reports the two separately by construction.
     The ROW figure above is unaffected: a row passes only if all three fields
     match, so an always-true conjunct cannot inflate a conjunction. What the
     old phrase "audit verdict layer" overstated was the LABEL — each row is
     two model judgments plus one deterministic measurement, not three
     verdicts. Reworded, not recounted. Note separately that `cells_correct()`
     DOES count deterministic cells alongside judged ones — Backlog.
     **And the perception behind those passes was NOT fixed — see the Sep 11
     entry, where it was partly fixed and fully diagnosed.**
   - **The one genuine defect is a SCORE defect.** item7 run 8 scored relevance
     3.0 and passed, while its own reason text says the draft "does not focus
     on the requested price-match guarantee and return policy" — the same
     judgment, in prose, as the run that scored 1.0. This is the observation the
     Sep 9 certify-verdicts-not-scores decision predicted, and it is why scores
     stay out of the claim.
   - **stop-on-pass: n=2 → n=4.** Fired on item6 runs 11 and 15.
   - **Report `first_text_passed`, not `final_text_passed`** — unchanged. The
     final figure is a function of the redraft cap.
   - **Budget, re-measured Sep 10:** 47s per item-run wall clock, ~16K tokens
     per item all-in (~11.6K agent-side plus the ~40% judge/vision undercount).
     A full 8x15 pass is ~1h35m — **serially latency-bound at ~20K TPM
     sustained, NOT throughput-bound.** See the quota entry in the Backlog.
   - **What certification does NOT cover:** the crash path, anything about
     scores, and `brand_consistent`'s reasoning as distinct from its verdict.

## Backlog — everything deferred, in one place (per Gerard's Aug 28 preference: no digging through STATUS.md scrollback for these)

Nothing here blocks anything else. Pulled together from scattered
"not urgent" mentions across past sessions plus new ones as they come up —
add new items here going forward instead of leaving them buried in a
session's narrative paragraph in `STATUS.md`.

- **`GroundednessEvaluator` does not measure responsiveness — the Sep 8 claim
  was RIGHT, and the correction written earlier on Sep 9 was wrong. Settled
  2026-09-09 PM on 60 judge calls.** Three readings of one finding in one day,
  kept in order because the sequence is the lesson:
  1. **Sep 8, n=5 on gpt-5-2:** groundedness scored 4.0 on drafts its own reason
     text called non-responsive. Concluded it measures *is what you said
     supported*, not *did you answer*, so `all_passed` is relevance-gated.
  2. **Sep 9 AM, n=30 on gpt-5-2:** groundedness ranged 1.0–4.0 on item7. Claude
     corrected (1) into "groundedness inconsistently imports relevance into its
     own score", and wrote that here as a property of the EVALUATOR.
  3. **Sep 9 PM, n=10 × three deployments on the same two fixed drafts:** the
     evaluator is fine; the judge model was not.

  | judge | item7 groundedness | item6 groundedness |
  |---|---|---|
  | gpt-5-2 | 1.0 ×8, 4.0 ×2 | 4.0 ×10 |
  | gpt-5-4-mini | 2.0 ×8, 4.0 ×2 | 4.0 ×10 |
  | **gpt-5-4** | **4.0 ×10** | 4.0 ×10 |

  Microsoft documents groundedness as measuring whether claims are SUPPORTED,
  not whether the response ANSWERS. **gpt-5-4 applies that definition on every
  call. gpt-5-2 usually lets off-topic-ness dominate and collapses to the
  floor.** So reading (1) describes the metric's actual contract; reading (2)
  attributed one model's failure to implement it to the SDK. Corrected here
  rather than deleted, because the error is instructive: an n=30 result on ONE
  model was generalised to a component shared by three.
  **item6 is the control that makes this readable** — all three judges returned
  groundedness 4.0 ×10 and relevance 3.0 ×10 on a well-posed draft, so the judge
  is not generally noisy. It is exact where the question is well-posed and
  divergent only where the question is ill-posed, which is where model capability
  shows.
  **What still holds from Sep 8:** `all_passed` is relevance-gated for any topic
  the fact sheet cannot cover, and individual scores are worth about ±1.
  **What it does NOT change:** the verdict layer. `all_passed` was 0/10 on item7
  and 10/10 on item6 for every judge — zero crossings in 60 calls. Pass/fail is
  judge-invariant, which is why certification on pass/fail was never blocked by
  any of this.
  Judge changed to gpt-5-4 the same day; see `m7_evaluator_tool.py`'s
  `judge_deployment()`.
- ~~**The redraft loop may be retry-until-lucky rather than remediation
  (Sep 8) — settle before certifying.**~~ — **SETTLED 2026-09-09. It re-rolls.**
  `probe_judge_isolation.py` called `evaluate_draft()` on run 15's recorded
  drafts with no agent in the loop, so every point of spread is judge-side by
  construction. **The failing draft passed 7 of 10 re-reads with its text
  unchanged** (relevance 3.0 ×7, 2.0 ×3); the passing draft was 3.0 ×10;
  groundedness was 4.0 on all 20 reads. Run 15's recorded failure was a minority
  draw — draft 1's modal score is a pass — so redrafting and re-scoring at 3.0 is
  what re-reading the ORIGINAL would have done 70% of the time.
  **The cap decision inverts, as predicted.** At 70% per read: one read 70%, a
  cap of 1 gives 91%, a cap of 2 gives 97.3%. A higher cap buys more dice, not
  better copy.
  **And it reaches past the cap.** A certification pass reporting
  `final_text_passed` measures the cap rather than the system — Sep 8's
  `final passed 21/21` is exactly what a 70% item with three rolls produces, and
  was never evidence of quality. **Report `first_text_passed` as the headline;**
  the probe already records both separately.
  **Left open deliberately:** draft 2's 10/10 against draft 1's 7/10 is Fisher
  p=0.21, so the redraft may have improved the text. Not chased — V4 was about to
  change redraft behavior, and measuring the quality of behavior you are
  replacing measures nothing.
- **Token budgets read off `run.usage` undercount by roughly 40% (Sep 8).** The
  agent's usage figures exclude the judge calls — `evaluate_draft` runs on a
  separate deployment through the Evaluation SDK — and exclude the CV audit's
  vision calls, which use their own client. Sep 8: 177,278 agent tokens recorded
  against 17 `evaluate_draft` calls worth roughly 66K more, plus 14 vision calls
  not counted at all. Every certification budget quoted so far is agent-only.
- ~~**The agent writes its grounding scaffolding into customer-facing copy when
  it has nothing to substitute (Sep 8) — now 3 for 3 on redrafts, and
  blocking.**~~ — **FIXED AND MEASURED 2026-09-09 by `INSTRUCTIONS_V4`.**
  `check_meta_commentary.py` made this a measured field rather than an eyeball
  count, and immediately found the defect was **not confined to redrafts**: 2 of
  21 FIRST drafts on Sep 8 (item6 runs 6 and 19) did it too, both PASSED with
  zero redrafts, and would have shipped — worse than the redraft case, where
  item7 at least ended FLAGGED. That number is what decided V4's prohibition
  belongs in clause 4 rather than only in clause 7: a clause-7 fix would have
  left those two uncaught while appearing to work.
  **Result over 30 runs, 113 drafts:** redrafts 5/5 → **0/53** (Fisher
  p=2.2e-07); first drafts 2/21 → **0/60** (Fisher p=0.065).
  **The redraft channel is settled; the first-draft channel is suggestive, not
  significant.** Claude predicted p≈0.0025 before the run by treating the 9.5%
  baseline as known rather than as two events; the honest test gives 0.065.
  Reaching p<0.05 needs roughly 50 runs, deliberately not spent.
  **Standing caveat: the detector is a phrase matcher, not a classifier.** A zero
  is meaningful only for the phrasings in its `PATTERNS` list. After any future
  wording change, sample the drafts by eye and confirm the copy is clean for the
  right reason rather than trusting the count.
- **`unmeasured()` is verified logic on an unexercised path (Sep 8).** Written
  after item1's `server_error`, unit-tested against a synthetic crashed record,
  and never run against a real crash because the next run completed cleanly.
  Same class of claim as any clause with zero observations — do not describe it
  as proven in the write-up.
- **Line endings differ between the bridge and Windows on files
  `.gitattributes` does not cover (Sep 8).** Git for Windows has
  `core.autocrlf=true` and checks `.txt`/`.md` out as CRLF; the bridge's Linux
  git has no such setting and reads CRLF-against-an-LF-blob as modified. Both
  are right about their own view. `q_a_pairs_sample.txt` burned most of an hour
  on this: Claude "fixed" it by stripping CRLF through the bridge, which is
  what made Windows' `git update-index --refresh` report "needs update" — the
  edit caused the problem it appeared to solve. **Consequence: do not rewrite
  whole tracked text files through the bridge.** Targeted edits, or prepare the
  change and let Gerard apply it. `.py`, `.json`, `.sh`, `.html`, `.yml` and
  `.bicep` are covered by `.gitattributes` and are safe.
- **VS Code's Source Control view under-reports bridge-side edits (Sep 8).**
  Its file watcher does not fire for writes arriving through the mount, so the
  panel shows fewer changed files than exist. **This is what dropped two doc
  files from commit `98158d0`** — the commit message described fixture work
  that was not in the commit. The failure is silent and points the wrong way,
  which is how partial work gets committed and then run against. Refresh forces
  it to catch up (the ⟳ icon, `Developer: Reload Window`, or clicking into the
  GitHub extension — confirmed working). **`git status` in PowerShell is the
  authority.** Standing consequence: every commit message Claude prepares now
  names the exact files to stage.

- ~~**item6's `expected_text` encodes a rare event as the expected one (Sep 9).**~~
  — **RESOLVED 2026-09-09 PM, and it was not the cosmetic issue it was filed as.**
  The field read `first_pass: False` because item6 was designed as the
  recoverable-failure fixture; the relevance step function retired that design and
  n=30 measured it passing first draft 29 times. Re-registered as a **well-posed
  control** in both `ITEMS` and `content-items-plan.md` — Gerard's call, and it is
  item6's own pre-registered branch 2 firing. Not the goalpost move rejected on
  item1: that was bending a key to excuse a defective fixture, this is a sound
  fixture doing something other than what it was built for, and doing it well —
  it is the control that made the Sep 9 judge comparison readable. **What is lost:
  no fixture now exercises fail-then-recover by design.** The remediation clauses
  remain observed, but by variance rather than construction.

- ~~**`run_provenance()` records agent fields for runs with no agent (Sep 9).**~~
  — **FIXED 2026-09-09 PM.** It now takes `script` and `include_agent`, both
  defaulting to the previous behavior so nothing that called it before changed.
  `probe_orchestrator_stability.py` passes its own name (it had been recording
  `m7_orchestrator.py`, since `Path(__file__).name` evaluates in the module that
  defines the function, not the caller), and `probe_judge_isolation.py` excludes
  the agent fields at the source instead of stripping them afterwards.

- ~~**A stale verdict string sits inside a committed results file (Sep 9).**~~
  — **RESOLVED 2026-09-09 PM by `probe_judge_isolation.py --reanalyze`.** It
  recomputes a results file's summary and comparison from the stored per-call
  scores, makes **no judge calls**, and does not import the evaluator module at
  all — so it needs no Azure credentials and still works if a deployment is gone.
  It writes `*_reanalyzed.json` and **never edits the original**: rewriting a
  committed artifact would make the wrong verdict disappear rather than be
  superseded, and the `STATUS.md` entry describing it would point at nothing.
  Corrected reading of `20260909-101238`: Q1 yes (7/10 unchanged passes), Q2
  cannot tell (Fisher p=0.211).

**Repo / security hygiene:**

- **Public-repo history purge — done, but never logged, and one tail end is
  still open (recovered 2026-09-06).** On Aug 20 an unrelated client folder
  (`youtube-channel-consulting/`, incl. a 28 KB internal status doc) was found
  tracked in the **public** `geostebovik/geoste-portfolio` repo's git history.
  HEAD was cleaned Aug 20; the Aug 21 prompt records the `git filter-repo`
  rewrite + force-push as **done**. Verified locally 2026-09-06: zero commits
  under any ref touch that path, which is what a successful rewrite looks like.
  **None of this appears anywhere in `STATUS.md`** — the only record was the
  Aug 21 session prompt, which was queued for deletion. Logged now so it stops
  depending on a disposable handoff doc.
  **Still open:** the **GitHub Support request to purge cached dangling
  commits** left behind by the rewrite was *drafted Aug 21 and never
  submitted* (restated Aug 26, then dropped out of every later doc). Until
  GitHub garbage-collects them, the old blobs can still be reachable by direct
  commit SHA on the remote, even though no branch or tag points at them.
  Optional, blocks nothing, but it is the one part of this that a local check
  cannot confirm — **verify against the remote, not the local clone.**

**M7 / current build:**

- **`probe_fixture_stability.py` records NO provenance.** Added Sep 10. No
  `git_head`, no `git_dirty`, no model deployment, no copy of the clause
  wording that was live — it writes the bare fixture results and nothing
  else. `m7_orchestrator.py`'s `run_provenance()` exists and takes
  `script=` / `include_agent=` precisely for this; the audit probe never
  adopted it. Deliberately NOT fixed on Sep 10: the clause change was already
  in flight and stacking a second edit before a measurement muddies
  attribution. **Fix it before the next audit-side measurement, not during
  one.** Note the JSON shape question that comes with it — the file is
  currently a bare `fixture -> runs` dict, and adding a `run` key changes the
  shape the Sep 1–3 baselines were eyeballed in.
- **`brand_consistent` — design constraint for future fixtures.** Added
  Sep 10 alongside the clause rewrite. The clause is total over the current
  five: True when the dominant scheme is orange, cream or both in any
  proportion; False only when materially different. A scheme that is
  **neither a brand family nor clearly different** — an off-orange, say —
  falls between the two branches and returns the model to unaided judgment.
  No current fixture sits there and `fact-sheet.md` leaves the same gap, so
  this is not a defect. It is a constraint on any *new* fixture: do not design
  one into that middle zone without settling the rule first. Same shape as the
  Sep 1 headline-exemption constraint in `content-items-plan.md`.
- **item6's topic is not fully well-posed, and its answer key is arguably
  wrong.** Added Sep 10. item6 was re-registered Sep 9 from a
  recoverable-failure fixture to a "well-posed control" with
  `first_pass: True`. Its topic string is "Propane Tank Refill: Sizes, Prices
  and Turnaround" and `fact-sheet.md` contains none of those three, so a
  first draft that promises them is ungroundable — which is exactly what
  happened on runs 11 and 15 of the Sep 10 certification pass. The checker
  caught it correctly both times. **Recorded, deliberately not fixed:** moving
  an answer key to match observed data is the goalpost move Sep 3's Thread 1
  refused, and the same refusal applies here. Decide it as a fixture question
  or leave it; do not let a green cell decide it.
- **item6's `expected_redrafts: None` is inert.** Added Sep 10. The match
  condition is `expected_redrafts is None or redrafts == expected_redrafts`,
  but item6 also expects `first_pass: True`, and any redraft implies the first
  draft failed — so the `first_pass` clause fails first and the `None` never
  distinguishes a case. Harmless; misleading to a future reader who thinks
  item6's redraft count is deliberately unconstrained.
- **`probe_orchestrator_stability.py`'s printed `agreement` counts passes,
  not matches.** Added Sep 10. For item7, whose pre-registered row is
  `first_pass: False`, the console reads "first draft passed: 1/15 (7%)" for a
  run that matched its answer key 14 times out of 15. The `stable` flag
  handles the inversion correctly (`agreement >= 0.8 or (1-agreement) >= 0.8`);
  the printed percentage does not, and a reader skimming console output would
  read a correct item as catastrophic. Display only, no effect on the JSON.
- **The built-in evaluator rubrics are customisable, and Microsoft recommends
  customising them.** Added Sep 10, new thread, M8-sized. The docs state the
  quality evaluators' prompts are open-sourced in the Evaluator Library and
  the Python SDK repo, and "we highly recommend that you customize the
  definitions and grading rubrics to your scenario specifics". M7 has treated
  `GroundednessEvaluator` and `RelevanceEvaluator` as fixed black boxes
  throughout — every finding about relevance's step function at 3.0 and
  groundedness's definition is a finding about a rubric that could have been
  edited. Not an M7 item: changing the rubric mid-certification would
  invalidate everything measured against it.
- **Quota is elastic and the probe loop is serial — the two go together.**
  Added Sep 10, tracked in Todoist `6hVCcxW6jWPmrMWq`. `gpt-5-4`'s 30K TPM is
  a deployment allocation, not a limit; 970K TPM sits unallocated in a 1M pool
  and the Edit dialog offers the full range. But raising it alone buys almost
  nothing: at 47s per item-run and ~16K tokens per item the certification pass
  draws ~20K TPM sustained, under the current ceiling, and is bound by serial
  latency rather than rate. **The quota raise is the precondition for
  parallelising the item loop, not a speedup on its own.** Eight items
  concurrently would draw ~160K TPM, which is where 30K binds. Parallelising
  across items is safe by construction — `m7_orchestrator.py` already runs
  every item on its own thread, for the contamination reason. Recommended
  value 300K, not "use all available": a ceiling is also the brake on a
  runaway loop, and whether the 1M pool is per-model or shared across the four
  deployments is unresolved.
- **The desktop shell has been unavailable two days running, and the cause is
  not the shell.** Added Sep 10. `device_list_dir` / `device_stage_files` /
  `device_commit_files` work; the shell cannot mount either folder (`no Plan9
  drive shares mounted under /mnt/.virtiofs-root/shared`). New on Sep 10:
  `echo hi` fails identically, so the failure is PRE-EXECUTION — the helper
  refuses to start any shell because the shares are absent, and the guest VM
  is up enough to report it. **Pre-registered test for the next session:
  attach ONLY `C:\Users\gerar\geoste-portfolio` and try the shell.** The
  leading hypothesis is that the two connected folders being nested causes the
  share set to be rejected whole (the error names both as failing, which is
  what publishing zero rather than one looks like). The root already contains
  `ai-103`, so the second share buys only a shorter path. If it still fails on
  one folder, nesting is ruled out and the next suspect is the desktop build
  (1.49585.0 / Electron 44.2.0). **Do not request access to
  `C:\Users\gerar\AppData\Roaming\Claude` to read the app's logs** — it is a
  protected location, cannot be granted, and one prompt was already spent on
  it.
- **`brand_consistent`'s verdict is fixed; its PERCEPTION is not.** Added
  Sep 10, found in the verification run that closed the verdict defect —
  which is why it is here rather than filed as resolved. After the clause
  rewrite the cell reads 15/15 correct on every fixture, and item3's `notes`
  still assert "the thumbnail uses an orange/cream palette" on **15 runs out
  of 15**. item3 contains no cream. The confabulation did not decrease when
  the verdict was fixed; it went from most-of-12 to all-of-15.
  **The mechanism is visible in item4.** There the model writes "dominated by
  blue and gray, which is materially different from the required orange/cream
  brand palette" — distinguishing the IMAGE's colours from the BRAND's
  palette exactly right. On item3, where the image is on-brand, it collapses
  the two and describes the thumbnail by reciting the brand guide. **When the
  answer is "consistent", the model stops observing and starts quoting.**
  Why it matters despite the green cell: `notes` is what a human reads when
  deciding whether to trust a flag, and here it is confidently wrong every
  time. The verdict is right because the rule is permissive enough that a
  mis-described image still lands correctly — not because the check sees what
  it claims to see.
  **This is a `notes`-instruction problem, not a verdict problem, and needs a
  different fix from the one that closed the verdict defect.** It is testable
  with the existing five fixtures on one 15-run pass: does item3 stop saying
  "cream"? Deferred from Sep 10 deliberately — a sixth wording change at
  14:35 would have traded the session's written record for it.
- **`brand_consistent` is palette-only, and nothing says so.** Added Sep 10.
  See the standing lesson on total rules. The clause's "Record as False only
  when..." scopes the check to the colour scheme, while `fact-sheet.md`'s
  brand guide also specifies the logo. No fixture tests a logo violation, so
  the gap is currently unobservable. **If logo consistency is ever to be
  checked, it is a `content-items-plan.md` fixture decision first and a clause
  extension second — in that order.**

- **The redraft path has ZERO observations (Sep 7).** `INSTRUCTIONS_V3`'s
  remediation clauses — cap of two, "replace unsupported claims with supported
  ones", stop-on-pass — have never run: both V3 runs passed every item on the
  first draft. Same gap Sep 4 recorded, from the opposite direction. Forcing a
  failure needs a topic `fact-sheet.md` cannot support, which is a
  `content-items-plan.md` change and therefore a plan decision, not just a run
  — the fixture-vs-answer-key distinction from Sep 3's Thread 1. **This is the
  current next action, and as of the Sep 7 check-in it is also item 6 of
  "What's actually left to build" above** — it was doing a build item's job
  from the Backlog, where an ordered list would not find it.
- **The redraft cap of 2 was set on judgement, not evidence (Sep 7).** Gerard's
  call, deliberately, with 10 (the `enable_auto_function_calls` default) ruled
  out as uncalled-for. The run record now counts `evaluate_draft` calls and
  redrafts per item, so the certification pass can replace the judgement with a
  number: if the second attempt is never used, drop to 1; if items routinely
  exhaust both and still fail, 3 is arguable.
- **The orchestrator's model was never chosen (Sep 7).** `gpt-5-4` entered in
  `8cb92aa` — the commit where Claude wrote `m7_orchestrator.py` — unremarked
  and undiscussed. Every tool-level result beneath it (`audit_thumbnail`, every
  fixture-stability run) was measured on `gpt-5-4-mini`, which M6 chose on
  parity plus ~3x cost. Measured cost as of Sep 7: ~11.6K tokens per item, ~58K
  per five-item run. **Do not decide this on token price alone** — before the
  quota change `gpt-5-4-mini` was provisioned at 3 RPM against `gpt-5-4`'s 30,
  and an argument for mini was made twice that morning without checking. Decide
  it with a paired run once the wording is stable.
- ~~**The judge deployment is inherited, not chosen (Sep 7).**~~ — **CLOSED
  2026-09-09. gpt-5-4, chosen on 60 measured judge calls.** It ran on `gpt-5-2`
  from M6, unchosen; `gpt-5-2` is the Content Understanding analyzer model.
  **What settled it:** on a draft whose claims are supported but which dodges the
  topic, gpt-5-2 returned groundedness 1.0 ×8 / 4.0 ×2 and gpt-5-4 returned
  4.0 ×10. On a well-posed draft all three deployments were identical. gpt-5-4 is
  the only one that applies the metric's documented definition every time.
  **The self-grading objection, answered with data rather than a hedge:** gpt-5-4
  is also the orchestrator's drafting model. Across the same six runs `all_passed`
  was 0/10 on item7 and 10/10 on item6 for ALL THREE judges, two of which are not
  the drafter — zero crossings in 60 calls. The coupling exists and is documented;
  it demonstrably is not buying the drafter a favorable verdict. Re-check if
  either model changes.
  **Two things ruled out on the way, both cheaply:** `reasoning_effort` is not
  reachable through the Evaluation SDK (accepted by `**kwargs`, retained nowhere,
  while `is_reasoning_model=True` lands visibly as `_is_reasoning_model`); and no
  deployment spends hidden reasoning tokens when it grades — `completion_tokens`
  matches the visible reason text to within a rounding error on all three
  (197/891 chars, 127/568, 202/998). Reasoning depth is not the mechanism.
  **Mechanism note:** `m7_evaluator_tool.judge_deployment()` reads
  `JUDGE_DEPLOYMENT` and falls back to `CHAT_DEPLOYMENT_GPT_5_4`. Probes take
  `--judge-deployment`, setting it before importing the evaluator module because
  the judge config is built at module scope.

- **The orchestrator's drafting cannot be made repeatable (Sep 7).**
  `temperature=0` is pinned, but the Agents SDK exposes no `seed` at all —
  verified by introspection, and unlike the chat-completions path the CV audit
  uses, where `seed=42` works. So run-to-run comparison at this layer is
  narrowed but never deterministic, which is why single runs are anecdotes here
  and the multi-run probe is the only instrument.
- **No multi-run harness exists for the orchestrator (Sep 7).**
  `probe_fixture_stability.py` covers the CV audit only. The certification pass
  needs its own, or an extension of that one.
- **`gpt-5-4-mini` showed 46% rate limiting in the portal (Sep 7), unexplained.**
  Mini is what `audit_thumbnail` runs on. Worth asking whether any of the
  historical CV-audit variance — the 0/7, 6/7, 5/7, 3/7 spread on `text_legible`
  before the check moved out of the model — had a rate-limit component. The old
  evidence cannot answer it; a fresh probe at the raised quota could.
- **`IIP-revised-project-plan.md` (July 15) is stale and is in the Claude
  Project (Sep 7).** It describes M6 as "responsible-AI instrumentation", M7 as
  a "light multi-agent pattern", and computer vision as explicitly out of scope
  — all superseded. It is one of three docs a fresh cloud session reads as
  current, and it is where the Monday punch-list task's wrong milestone list
  came from. Fix by adding a dated superseded header naming what still holds
  (phases 2/3, platform decision, naming) rather than by rewriting it.
- ~~**The Friday check-in task was moved to cloud and not reviewed (Sep 7).**~~
  — **partly closed by its own first run, same day.** The concern was that its
  job is updating this file, which requires Gerard's machine; run in the cloud
  without a device binding it could only summarise in chat, which *looks* like
  success. It did run on the local machine with both folders connected, edited
  this file, and committed — and "commit and push before closing" is now an
  explicit final step in the task, as this entry asked.
  **One thing its first run surfaced, still open.** Its brief's steps 2–4 —
  ask how the week went, what slipped, how it felt, which milestone — assume
  Gerard is present to answer. On a manual fire he was not, so the run derived
  everything from Todoist and git and left the Notion row's Reflection field
  as an explicit placeholder rather than inventing one. That was the right
  call; it also means the task needs to detect the difference. **Two prompt
  changes owed:** it must not add dated sections to this file (it added one on
  the first run — this doc is a current-state snapshot, and a weekly log
  section here is how `STATUS.md`'s `## Next action` absorbed 1,650 lines
  before the Sep 6 restructure), and it must say when it was fired manually
  rather than on schedule, so it does not record schedule conclusions from a
  test.
  **Correction, logged 2026-09-07:** that first run wrote "it fired on a
  Monday, not a Friday … the schedule needs checking" into this file. The
  schedule is fine — Gerard test-fired it deliberately. A confident wrong
  conclusion from an unattended task, committed to a doc: standing lesson 7,
  this time not from Claude.

- **Harness resolution: variance is a symptom of an undercalibrated
  fixture, not a flat tax on every measurement (established Sep 2, twice
  revised Sep 3).**
  **Correction 1:** this entry originally cited item1's `info_accurate`
  7/7 -> 5/7 as proof a cell moves 2/7 irreducibly. That movement turned out
  to have a *cause* -- a fixture defect, fixed Sep 3 -- and the variance went
  with it. **Treat unexplained movement as a hypothesis to chase first, and
  call it noise only after chasing it.**
  **Correction 2:** the floor is not a constant, it is a function of where
  the cell sits. On Sep 3, **13 of 15 cells showed zero variance across
  three runs**; only the cell near p=0.5 moved (item3's `text_legible`, at
  6/7, 5/7, 3/7 on the same image with `temperature=0`/`seed=42` pinned).
  Sampling theory says the same: at p=0.5 the standard error at n=7 is 0.19,
  so plus or minus 2/7 is ordinary variation, while at p near 0 or 1 the
  same n is rock solid -- item4 and item5 return 0/7 every single run.
  **Read every future run against this: a 1-2 run difference out of 7 is not
  an improvement or a regression, and on a contested cell even 3/7 may not
  be.** Big effects (the 7/7 -> 0/7 swings that drove the Sep 2 decisions)
  remain trustworthy.
  **On raising `RUNS` (analyzed Sep 3): not to investigate a wobbling
  cell.** Precision scales with the square root of n, so 4x the runs buys
  only half the error bar -- and a cell reading p=0.67 against a target of 0
  has a *location* problem, not a precision one. The one place more runs
  genuinely pay is **certification, once, at the end**: 0/7 bounds the true
  rate only below ~35% at 95% confidence, where 0/20 bounds it below ~14%
  and 0/30 below ~10%. Worth one high-n run on the final configuration
  before any stability claim goes on the portfolio site -- at 2x the calls
  now that the audit is split.
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
  **A failed `git commit --amend` strands `HEAD.lock` specifically, not
  `index.lock` (Sep 7).** The obvious cleanup command looks for the wrong
  file and reports "cannot find path", which reads like nothing is wrong.
  `Remove-Item .git\HEAD.lock` is the fix. Worth knowing because the amend's
  companion `git push` in the same block succeeded, so the failure was
  silent from the remote's side.
  **"Reads are fine" is too broad -- corrected Sep 8.** `git diff` on a file
  whose stat cache is stale refreshes the index, which is a write: it
  stranded an empty `.git/index.lock` even under `GIT_OPTIONAL_LOCKS=0 git
  --no-optional-locks`. Neither switch covers it. So the rule is not
  read-vs-write by command name; it is that **any git command which may
  touch the index can strand a lock through this shell.** `git log`,
  `git show` and `git rev-parse` remain safe. Cleanup: `Remove-Item
  .git\index.lock`.

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
- ~~**Ungrounded embellishment in `description-template.md`'s own worked
  example (flagged Aug 27).**~~ -- **FIXED Sep 4, and the Aug 27 framing of it
  was wrong on two counts.** The example included "matched to any swatch or
  sample you bring in" and "we'll mix it while you shop", neither in
  `fact-sheet.md`'s Services list.
  **Correction 1: it was not "cosmetic".** The example sits three lines below
  the template's own rule that any factual claim "must be traceable to
  `fact-sheet.md`" (line 28-30), under a heading calling it "Example (clean,
  no planted errors)", and is contradicted again by the tone rule at line 47.
  The reference document violated its own rule while asserting it did not.
  **Correction 2: a real drafted item DID inherit it.** `m7_evaluator_tool.py`'s
  `main()` copies the example verbatim, and that smoke test is the only place
  item1's text-side expected result is exercised. item1 is a *clean control*,
  so it was carrying an unplanted flaw -- the text-side twin of Sep 3's Thread
  1, and resolved the same way: correct the fixture, not the answer key.
  **Fixed in both files, kept byte-identical** (verified programmatically, not
  by eye). Claude found it and drafted the replacement wording; Gerard approved
  the wording and it was applied to both.
  **What the fix did NOT do: move either score.** Groundedness stayed 4.0,
  relevance stayed 3.0. The warrant is direct inspection against the fact
  sheet and the template's own rule -- not the numbers, which gave no evidence
  either way. Anyone writing this up as "improved groundedness" would be
  overclaiming.

- **The judge's `reason` field is not a reliable guide to what to fix (Sep 4).
  This is the one with a design consequence.** Across three runs of item1's
  smoke test: Aug 27 flagged the two genuinely ungrounded claims; Sep 4 pre-fix
  said "No clear factual errors relative to the context" and flagged nothing;
  Sep 4 post-fix flagged two *different* phrases -- "we show you how we
  custom-mix exterior paint right in store" and "held up outside" -- both of
  which were present and unflagged in the previous two runs. Score was 4.0 in
  all three, across two different texts.
  **Stronger than the cross-run drift: one run contradicts itself internally.**
  The Sep 4 post-fix reason calls the copy "implying an in-store service
  consistent with the listed 'Custom paint mixing'" and then lists "we show you
  how we custom-mix exterior paint right in store" as content "not explicitly
  in the fact sheet". Same clause, endorsed and flagged in one paragraph. That
  instance needs no cross-run comparison to stand up, and is the version worth
  citing.
  **Consequence for the orchestrator instructions text (item 4 above): branch
  on `passed`, not on `reason`.** "Redraft when a check fails" is safe.
  "Revise according to the evaluator's reasoning" is not -- an agent following
  it today would strip grounded copy the judge endorsed one sentence earlier.
  **Same reliability class as the `notes`-vs-boolean entry above**, different
  tool. Worth noting the CV side already found this failure, better evidenced,
  and *solved* it by moving judgment out of the model into WCAG arithmetic.
  Finding it a second time in a weaker form does not double its value, and for
  the portfolio the CV story is the stronger one to tell.

- **`RelevanceEvaluator` comments on grounding it cannot see (Sep 4).** Its
  Sep 4 reason says the draft "isn't grounded in any specific 'store fact
  sheet' details" -- about a draft that names the store and quotes the exact
  hours. It is never handed the fact sheet (no `context` parameter), so it is
  delivering a verdict it structurally cannot check. Probable cause: the query
  redesigned Aug 27 itself contains "grounded in the store's fact sheet", so
  the relevance judge treats grounding as part of its remit. Untested. Not
  chased, since testing a query variant is a second variable.

- **item1's at-home vs in-store topic tension, deliberately not fixed (Sep 4).**
  The item topic is "How to Mix Exterior Paint Colors at Home"; the copy sells
  an in-store service. Both evaluators docked a point for exactly this, in both
  Sep 4 runs -- it, not the embellishments, is what is actually costing the
  scores. Left byte-for-byte alone while the embellishments were removed, so
  the two changes stay attributable. Fixing it means either rewriting the copy
  or changing the item topic in `content-items-plan.md`, and the second is an
  answer-key change.

- **`m7_evaluator_tool.py` runs Azure calls at import (noted Sep 4).**
  `build_judge_config()` is called at module scope, so importing the module
  shells out to Azure CLI for endpoint and key. That happens whenever anything
  imports it -- including `m7_orchestrator.py` at tool-registration time, and
  any future unit test. It works today; it means the module cannot be imported
  without Azure auth. Not fixed, not blocking.

- **The orchestrator paraphrases tool output rather than quoting it (Sep 4,
  first run).** item3's summary quoted the real contrast figures; item1's
  read as tidy prose ("Brand styling matches the approved Riverside Hardware
  & Supply look") rather than the tool's actual notes. Same faithfulness
  class as the `notes`-vs-boolean and `reason` entries above, but at the
  layer a human actually reads. Matters most if any of this output is ever
  shown on the portfolio site as evidence of what the audit found.

- **Low-confidence OCR text is quoted in notes without being marked as such
  (Sep 4).** `m7_legibility_check.py` reported item3's headline as "Tool
  Rental 101 what tye Offer"; `build.py` line 156 renders "Tool Rental 101:
  What We Offer". Genuine Read output at 0.32 minimum confidence, not
  confabulation -- and corroborating, since the garbling is the illegibility
  showing itself. But it reads as a possible hallucination to anyone who has
  not seen the confidence number. A confidence tag on transcriptions below
  roughly 0.5 would make the notes self-explaining. Small.

- **`description-template.md` is not in the drafting loop (Sep 4).** The
  orchestrator drafts from its instructions alone; nothing supplies the
  title/description format, and nothing checks compliance -- `evaluate_draft`
  grades groundedness and relevance, not shape. Caught because item2's first
  run title dropped the required " - Riverside Hardware & Supply" suffix.
  Not a defect in any tool; a gap the instructions text (item 4) has to close
  deliberately, or the template stays decorative.

- **Two contrast margins recorded, deliberately not fixed (Sep 3).**
  (1) item2's title clears the 3:1 bar by 0.032 (3.032:1), and item5's badge
  sits at the same value for the same color pair -- clean controls on a knife
  edge. Any change to those fixtures, or any move to the 4.5:1 normal-text
  bar, flips them to false positives. Not fixed, because changing a control
  that returns the right answer is the goalpost move rejected on item1 the
  same day. (2) item3's brand line fails at 2.949:1 and was never planted;
  item3's verdict is still correct, but its notes name two failing elements
  where `content-items-plan.md` says the item "isolates one failure mode."
  Both are documentation, not defects.
- **A stability claim on the portfolio site needs one high-n run (Sep 3).**
  `text_legible` is now deterministic and needs none. `brand_consistent` and
  `info_accurate` are still model-judged, and 0/7 bounds a true failure rate
  only below ~35% at 95% confidence -- 0/20 gets to ~14%, 0/30 to ~10%. Worth
  one deliberate high-`RUNS` pass on the final configuration before any
  "stable" claim goes public. Not needed for development.

**CV-audit investigation threads (added Aug 31 -- the legibility ones below
are now MOOT: `text_legible` left the model entirely on Sep 3, so no wording
for it exists to tune. Kept as the record of what was ruled out and how):**

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

### `probe_fixture_stability.py` has no `__main__` guard

Its run loop is at module level, so IMPORTING it executes 75 audit calls. Found
2026-09-11 when a one-line import check was proposed as a smoke test and had to
be withdrawn. Harmless today because nothing imports it; a real hazard the
moment anything does — a test collector, an `__init__`, or someone reaching for
`observed_colors_of()` as a helper. Three lines to fix. Not done on Sep 11
because it would have been a second change inside a measurement.

### `cells_correct()` counts deterministic cells alongside judged ones

`m7_orchestrator.py`. It iterates all three fields per record, so any `N/225` or
`N/360` figure it produces credits the model with the deterministic
`text_legible` cells. Same defect the fixture probe had until Sep 11; same fix —
tally and report the two populations separately.

**This needs no Azure run.** It is a reporting function and can be verified by
re-running it against `results/20260910-123321_orchestrator_stability.json`.
Deferred from Sep 11 only to avoid a third edit to `m7_orchestrator.py` in a
session that was mid-certification.

Note the row-level figure actually quoted (117/120) is unaffected — see item 7.

### The remaining `brand_consistent` defect is a NAMING constraint, not a perception one

Supersedes the Sep 10 framing. After `observed_colors`, item3's confabulation
fell to 9/15, and the fifteen descriptions show the perception is IDENTICAL
every run — translucent lighter shapes over orange, correctly located. The
model flips between calling them "peach" (correct: `#f28a4f` is peach) and
"cream" (the brand guide leaking in as a synonym for *lighter*).

So the fix is a vocabulary constraint in the `observed_colors` field
description: name colours by what they are, never reuse a brand-palette colour
name for something that merely resembles it in lightness. Testable the same
way — one 15-run 5-fixture pass, does the count fall below 9/15.

**Do not touch `brand_consistent`'s verdict clause.** Still finished, still
225-cells-correct-across-two-configurations, still off limits.

Second-order, and worth deciding deliberately: the agent republishes `notes`
verbatim in its own prose output, so on ~60% of item3 runs the agent's visible
summary now carries the wrong colour word. The verdict is right; the
human-facing surface is wrong. That is a stronger argument for fixing the naming
than the count is.

### A full orchestrator pass at current HEAD is owed

M7's certification names `87b37cd`. The repo is now at `59f4ba3`, which includes
`observed_colors`, the `provenance.py` extraction and the transport retry. The
Sep 11 attempt produced 28 of 120 records before the undock killed it — clean on
the audit side (28/28), unresolvable on item7 at n=3.

**This is the first item of the next session.** ~95 minutes, unattended, docked.
The retry fix means a dropped connection now costs one row instead of the pass.
`--runs 1 --items item1` first as a smoke test; the retry wrapper's own correct
behaviour has never been observed against a real transport failure, so it
carries exactly the caveat `unmeasured()` used to.

### item7's answer key does not allow for the remediation clause succeeding

Observed 2026-09-11, run 1: item7's first draft failed, two redrafts ran, and
the final PASSED — stop-on-pass firing on item7 for the first time (n=4 → 5).
The key says `final_passed: False`, so a successful recovery scores as a miss.

**Same category as item6's two "failures" on Sep 10: the pipeline working
against a key that encodes an expectation the system can beat.** Recorded, NOT
fixed — moving an answer key to match the data is the goalpost move Thread 1
rejected on Sep 3. The right resolution is to decide deliberately, against a
full pass, whether item7 is a recoverable-failure fixture or a
persistent-failure one, the same way item6 was re-registered on Sep 9.

### `ABSENT_COLOR_CHECKS` is a regression detector, not a quality measure

Written into the probe already; recorded here so it is not rediscovered. It is a
substring test and scores a bare brand-guide recitation identically to a
detailed, correctly-located description containing one wrong word. Read alone it
would have logged Sep 11's large improvement as no change. Always read the
`[observed]` prose beside the count.

Same class as the standing caveat on `check_meta_commentary.py` being a phrase
matcher rather than a classifier.

## Which doc answers which question

| Question | Doc |
|---|---|
| What does the system look like right now, and where do I pick up? | **this file** |
| What is the single next thing to do? | `STATUS.md`'s `## Current next action` (one item; the *ordered* plan is this file's "What's actually left to build") |
| What happened last session, and why? | `STATUS.md`'s `## Session log` — newest first |
| What happened during M2–M6 (Jul 27 – Aug 7)? | `STATUS-archive-phase1.md` |
| What's the full multi-phase plan / business context behind M7? | `agent-system-project-plan.md` |
| How does a Foundry concept (agent/thread/tool/FunctionTool) actually work? | `agent-service-primer.md` |
| What's the ground truth for Riverside Hardware content? | `iip-docs/m7-riverside-hardware/fact-sheet.md` (the agent reads it at runtime via `scripts/m7_fact_sheet_tool.py`) |
| What does the orchestrator instruct the agent to do, and why? | the wording is `ACTIVE_INSTRUCTIONS` in `scripts/m7_orchestrator.py` — `INSTRUCTIONS_V4` as of 2026-09-09, and the only source of truth; `m7-instructions-draft.md` holds the rationale and version history only. **Never edit a version in place** — every past result is labelled with the version it ran under, so changing one relabels history (caught Sep 9 before it reached a commit) |
| What result should each test item produce? | `iip-docs/m7-riverside-hardware/content-items-plan.md` |
| What format must a drafted title/description follow? | `iip-docs/m7-riverside-hardware/description-template.md` |
| Have I hit this Python shape before? | `python-patterns.md` |
| What CLI command do I need for X? | `iip-cli-runbook.md` |

**Where a lesson goes — four buckets, no overlap.** Checked 2026-09-06; the
split holds, but it had never been written down in one place, so state it
here and route new lessons on the way in rather than sorting them later.

| Kind of lesson | Doc |
|---|---|
| General Python language patterns | `python-patterns.md` |
| Azure/SDK/infra gotchas — client shapes, service behavior, venv, paths | `STATUS.md`'s `## Key Lessons` |
| A CLI command or an `az` quirk | `iip-cli-runbook.md` |
| How to *work* — method, measurement, verification discipline | this file's "Standing lessons worth not relearning" |
