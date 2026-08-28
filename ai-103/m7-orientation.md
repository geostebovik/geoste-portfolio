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
      STATUS: built + verified                        STATUS: designed, not coded
      (wraps m7_evaluator_tool.py)                     (will build on m7_vision_test.py's
                |                                        proven vision-call pattern)
      Uses GroundednessEvaluator +                      Will check 3 things:
      RelevanceEvaluator (Azure AI                        - text_legible
      Evaluation SDK)                                      - brand_consistent
                |                                           - info_accurate
      Checks drafted title/description                     (+ notes: reasoning)
      text against fact-sheet.md                                    |
                                                          Checks thumbnail images
                                                          against fact-sheet.md's
                                                          brand guide + posted hours
```

Both tools check a different *kind* of output against the same ground
truth — `fact-sheet.md` — the same role the loan agreement PDF played for
M5's RAG pipeline. `content-items-plan.md` is the answer key: 5 test items
(2 clean controls, 3 each carrying exactly one planted flaw) that a finished
CV-audit run should score exactly as documented there — that table is what
"done and working" gets measured against, not a vibe check.

## What's actually left to build, in order

1. **CV-audit tool wrapper** — turn `m7_vision_test.py`'s proven vision call
   into an actual `FunctionTool`-compatible function: JSON-string return,
   reST-style docstring (`:param:`/`:return:`/`:rtype:`), scored against the
   3-field rubric above. See the Aug 28 FunctionTool section in
   `agent-service-primer.md` for the mechanics.
2. **`evaluate_draft()` wrapper** — a thin function around the already-working
   evaluator that returns `json.dumps(...)` instead of a raw dict, with its
   own reST docstring. Small, but not done yet.
3. **Orchestrator instructions text** — the actual job description telling
   the agent when to draft, when to call each tool, and what to do with a
   failing result (redraft? flag for review?). Not yet written.
4. **Wire it together** — `AgentsClient` + `ToolSet` + `enable_auto_function_calls`,
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
