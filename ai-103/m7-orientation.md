# M7 Orientation — Where Things Stand (start here each session)

**Status:** current-state snapshot only — not a log (that's `STATUS.md`) and
not a plan (that's `agent-system-project-plan.md`). This page answers one
question: "what does the M7 build actually look like right now, and where
does the piece I'm about to touch fit in?" Update this page whenever a piece
of M7 moves from *designed* to *built*, or *built* to *verified* — otherwise
it goes stale and becomes one more untrustworthy doc, which defeats the point
of having it.

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
                                                      Latest 5-fixture run: 4/5.
                                                      item3 fails BOTH text_legible
                                                      AND brand_consistent -- open
                                                      regression, see item 2 below.
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
   **New regression, unresolved -- this is the actual next step.** A later
   full 5-item run under the corrected (and actually saved) wording again
   showed 4/5, but this time item3 failed on **both** `text_legible` and
   `brand_consistent` -- `brand_consistent` had never failed before this
   run. Not yet determined whether this is run-to-run noise (no
   `temperature` pinned anywhere in the client) or a real ripple effect from
   editing the `text_legible` section of a shared multi-field system prompt.
   Needs several plain reruns to characterize before touching the prompt
   again.
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
- **`temperature` is unpinned everywhere in `m7_cv_audit_tool.py` and its
  test scripts.** Given how much run-to-run variance has shown up across
  this investigation (diag-d's split result being the clearest case),
  pinning `temperature=0` is worth a deliberate decision once the
  brand_consistent regression is resolved -- may make reproducibility
  testing more meaningful, or may mask real model uncertainty worth
  knowing about.
- **General confabulation risk in vision-judgment `notes` fields, beyond
  text_legible.** Printing the model's actual `notes` reasoning (first done
  in the `probe_legibility_detail_level.py` run) is what surfaced the
  wordmark-only citation pattern that led to the root cause above -- worth
  the same scrutiny for `info_accurate` and `brand_consistent`, neither of
  which has had its own `notes` output examined this closely yet.
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
