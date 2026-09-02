# M7 Orientation — Where Things Stand (start here each session)

**Status:** current-state snapshot only — not a log (that's `STATUS.md`) and
not a plan (that's `agent-system-project-plan.md`). This page answers one
question: "what does the M7 build actually look like right now, and where
does the piece I'm about to touch fit in?" Update this page whenever a piece
of M7 moves from *designed* to *built*, or *built* to *verified* — otherwise
it goes stale and becomes one more untrustworthy doc, which defeats the point
of having it.

**End-of-session checklist (added 2026-09-02):** before closing for the day,
reconcile the Todoist "IIP — AI-103 Punch List" against what this session
actually resolved — close or update any task a doc here already documents as
done. Added after the `brand_consistent` regression task sat open in Todoist
a full day past `m7-orientation.md` already recording it as resolved (Sep 1
resolution, caught and fixed Sep 2).

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
                                                      Sep 2: two wording edits, each
                                                      fixed its target and broke a
                                                      different check (14/15 both
                                                      times, different cell). Cross-
                                                      check contamination proven
                                                      bidirectional. DECIDED: split
                                                      into 2 calls -- text_legible
                                                      alone; brand+info together.
                                                      See item 2 below.
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

   **Next step: implement the split with both clauses' wording FROZEN as-is.**
   Do not tune wording and split in the same step. Each clause has been
   proven correct in some configuration; the split's first probe run tests
   whether both can be correct simultaneously. Open design question to
   decide deliberately: two calls produce two reasoning strings and the
   schema has one `notes` field -- concatenate, lose per-call attribution,
   or restructure `notes` into per-check keys and change the tool's return
   shape? `audit_thumbnail()` should still merge into a single
   `ThumbnailAudit` so the orchestrator's tool contract doesn't change.
   Cause (c) is unaffected by the split and stays in the backlog.
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
