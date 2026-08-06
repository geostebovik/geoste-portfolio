# IIP — Current Status

**This is a living document.** No date in the filename — it gets edited in
place each session, not re-copied. If you're looking for full historical
narrative (the "why" behind past decisions, session-by-session), that lives
in the frozen archive `MASTER-REFERENCE-0724.md` in the Drive IIP folder —
closed, not touched or re-read during normal sessions. This file is the only
thing that should need reading/updating at the start of a normal session.

Commands/CLI reference lives separately: `iip-cli-runbook.md` in this same
`ai-103/` folder — that page already works well as the "code samples"
reference and didn't need rebuilding.

A gotchas/tips-and-tricks page and a master index page (once there's enough
split across pages to justify one) are deferred until real material
accumulates for them — no point building empty structure now.

**Status as of:** August 6, 2026

---

## Milestones (Phase 1)

- [x] **M0:** Tear down West US 3 RG and all resources — zero carryover. Complete.
- [x] **M1:** Redeploy Foundry fresh in West US, quota re-verified. Complete (July 23, 2026).
- [x] **M2:** Custom document analyzer (`iip_loan_agreement_analyzer`) built and validated
  against the clean-PDF loan agreement. Complete (rebuilt July 23, 2026 after a
  collateral-damage purge; original build dated July 17/20).
- [x] **M3:** `m3_analyze.py` (submit-and-poll pipeline) written, fixed, and validated
  end-to-end. **Complete July 27, 2026.**
- [x] **M4:** Extraction validated across all 3 image conditions (clean PDF, flatbed
  scan, angled photo). **Complete July 27, 2026.**
- [ ] **M5:** RAG-grounded Q&A working (real vector search/index, not context-stuffing).
  **Unblocked (Aug 6)** — M6 picked `gpt-5-4-mini` as the Q&A model. Not started.
- [x] **M6:** Evaluator harness built, used to pick GPT-5.4 vs. GPT-5.4-mini for M5.
  **Complete (Aug 6).** Full pipeline (`m6_generate.py` → `m6_assemble.py` →
  `m6_evaluate.py`) built, debugged, and run twice — once against the original
  10-question rubric (Aug 5), once against a 14-question set stress-tested with
  4 harder questions probing cross-clause reasoning, arithmetic synthesis, and
  abstention (Aug 6). Decision: **`gpt-5-4-mini`**, on confirmed quality parity
  across both runs plus a real ~3x per-token cost advantage. Full evidence
  trail, including a real cross-session reproducibility finding that overturned
  the Aug 5 run's apparent `gpt-5-4` edge, in the Aug 6 session notes below.
  Small infra items remain (see Next action) but don't block M5.
- [ ] **M7:** Build a single orchestrator agent (Generative AI/agentic exam
  domain) over a neutral, synthetic small-business content-review scenario —
  decoupled from the YouTube-cleanup business thesis as of August 4, see
  `agent-system-project-plan.md`'s "Decoupling note." Same technical shape
  as originally planned: drafts content against a template, reuses M6's
  evaluation-harness pattern (Groundedness/Relevance/F1) to QA drafted
  output against grounding data, and adds a computer-vision module
  (thumbnail-style brand/legibility/info-accuracy audit) — the one AI-103
  exam domain not otherwise touched through M6. No longer tied to Anne's
  engagement or any specific unvalidated business premise; "is this a real
  business" is now a separate, evidence-gated question, not assumed live.
  Not started. → Phase 1 (of IIP labs) complete.

---

## Latest session (August 6, 2026)

- Before adding new evaluator evidence, re-examined the Aug 5 F1 result with
  real skepticism instead of accepting the raw number: is the near-tie an
  artifact of comparing two close variants of the same model family, or of
  the test document/questions being too simple to discriminate on? The
  original 10 questions are single-fact lookups with no cross-clause
  reasoning — a limitation already flagged July 28 but never actually tested
  against. Decision: stress-test the *same* document and pipeline with harder
  questions rather than swap models or documents — narrower and cheaper, and
  it directly tests which explanation (task difficulty vs. real model-quality
  difference) is doing the work, instead of guessing.
- Checked whether pricing alone could resolve the tie if quality really is
  even. Confirmed via Microsoft Learn / Microsoft Q&A (citing the official
  GPT-5.4 launch blog): `gpt-5.4` (<272K context) runs $2.50/M input tokens,
  $15.00/M output tokens on Standard Global. `gpt-5.4-mini`'s $0.75/M input,
  $4.50/M output came from a secondary aggregator, not independently
  confirmed against the primary Microsoft blog (JS-rendered, didn't return
  usable text via fetch) — worth a portal spot-check before treating the
  exact cents as final, but the ~30%-of-base ratio on both input and output
  is internally consistent and plausible. No latency data exists anywhere in
  this project to weigh alongside it; `m6_generate.py` never captured request
  timing.
- 4 new Q&A pairs added to `iip-docs/q_a_pairs_sample.txt` (now 14 rows
  total), each targeting a distinct failure mode the original 10 never
  touched: payment-allocation ordering (a 3-item sequence from Section V),
  an arithmetic-synthesis question ($958.12 × 72, hand-checked = $68,984.64),
  a multi-clause combination question (needs both Section IV *and* Section VI
  for a complete answer), and an abstention question (late-fee grace period
  in days — genuinely not stated anywhere in the document, testing whether
  the system prompt's "say so if it's not in the document" instruction is
  actually followed rather than assumed).
- Naming-convention rework across the M6 pipeline, prompted by realizing
  `m6_assemble.py`'s hardcoded results filename would need a manual edit
  every single run. Settled on `{timestamp}_{script}_results.json` per
  producing script, not incrementing IDs — incrementing IDs were considered
  and rejected: they don't remove the "which file is current" lookup problem,
  they just relabel it, and they carry less information than a timestamp does
  for free (a timestamp says *when* for free; a counter needs its own lookup
  logic to find the highest existing value). `m6_generate.py`'s output
  renamed `{ts}_results.json` → `{ts}_generate_results.json`. `data.jsonl`
  renamed to `m6_eval_input.jsonl` — a real, six-months-from-now-legible name
  instead of a generic one — updated in all three places it's referenced
  (`m6_assemble.py`'s write, `m6_evaluate.py`'s read, `.gitignore`).
- `m6_assemble.py` rewritten to auto-discover the latest generate-results
  file instead of reading a hardcoded filename, built collaboratively in
  rounds rather than handed over finished — same working style as every
  other script this project. Confirmed by direct test, not assumed:
  `Path.glob()` on a nonexistent directory returns `[]` rather than raising
  on this Python/OS combination, which meant the originally-planned separate
  `mkdir` guard wasn't actually needed — one empty-list check covers both the
  missing-directory and empty-directory first-run cases. Two real bugs caught
  in review, not just style nits: `from anyio import Path` (an async I/O
  library, not `pathlib.Path` — same species of mistake as July 29's stray
  `xmlrpc.client` import, VS Code autocomplete offering the wrong match),
  swapped for the real import; and the first working draft looped over
  *every* matched file and merged their rows together rather than selecting
  only the newest one with `[-1]` — would have silently blended every
  historical generate-run into `m6_eval_input.jsonl` the moment a second
  `*_generate_results.json` file existed, which is exactly what this
  session's rerun would have triggered if it had shipped unfixed.
- Re-hit the `nltk`/`venv1`-nested-in-`scripts/` CWD-import block from Aug 5,
  exactly as predicted — the first real recurrence since it was flagged as
  something that "will recur on every future script that imports
  `azure.ai.evaluation` from `scripts/`." Unblocked for this session the same
  way (`$env:NLTK_DISABLE_IMPORT_SECURITY = "1"` in PowerShell before
  running), but the deferred decision is now made: relocate `venv1` outside
  the `ai-103` tree rather than keep setting the env var per session. Not yet
  executed — deliberately deferred to the start of the next session instead
  of squeezed in at the tail end of this one, since it's a real structural
  change worth doing with a clear head. Plan: recreate fresh via
  `python -m venv` + `pip install -r requirements.txt` rather than move the
  folder wholesale, since venvs bake absolute paths into `pyvenv.cfg` and
  their activation scripts at creation time. Real verification step for that
  session, not to be skipped: confirm `sys.executable` resolves correctly
  afterward, and confirm importing `azure.ai.evaluation` no longer needs the
  env var at all — proof the fix addressed the actual root cause, not an
  assumption that it did.
- `m6_generate.py` rerun against the full 14-question set (28 rows: 14
  questions × 2 models). Both models' arithmetic answer checked and correct
  ($68,984.64, matching the hand-computed ground truth). Both correctly
  abstained on the grace-period question rather than inventing a day count —
  no hallucination on either candidate. `m6_assemble.py`'s new discovery
  logic exercised for real for the first time: correctly found and read the
  new `20260806-132129_generate_results.json`, the only file in `results/`
  matching the new `_generate_results.json` pattern.
- `m6_evaluate.py` run against the 14-question set
  (`NLTK_DISABLE_IMPORT_SECURITY=1` set per-session, `PF_WORKER_COUNT=2`
  still in effect from `.env`; sustained 429s during the run, expected given
  the account's per-deployment capacity limits, same in kind as Aug 5).
  Results saved to `results/20260806-135742_eval_results.json`.

  | metric | gpt-5-4 | gpt-5-4-mini |
  |---|---|---|
  | groundedness | 4.214 | 4.429 |
  | relevance | 4.000 | 4.071 |
  | similarity | 4.857 | 4.929 |
  | f1_score | 0.320 | 0.382 |

  `gpt-5-4-mini` now leads or ties on every metric, across both the original
  10 questions (re-asked fresh today, not reused from Aug 5) and the 4 new
  stress questions — a materially different picture than Aug 5's "three tied,
  one thin edge to `gpt-5-4`."
- Real, significant finding, bigger than the stress-question results
  themselves: `gpt-5-4`'s answer to "What state's law governs this
  agreement?" changed between the two evaluation runs. Aug 5: "Arizona."
  (F1=1.000). Today, same model, same deployment, same `temperature=0`: "This
  agreement is governed by the laws of the State of Arizona." (F1=0.182) —
  identical in substance to `gpt-5-4-mini`'s answer both times. That single
  question drove essentially the entire Aug 5 F1 gap (+0.818 of the +0.459
  total sum of per-question differences); it evaporated on rerun, which
  directly confirms — with a real repeated observation, not just a
  small-sample-size argument — that Aug 5's apparent `gpt-5-4` F1 edge was
  noise. Worth flagging plainly against the July 29 finding that
  `temperature=0` gives "byte-identical output" on reruns: that was verified
  back-to-back, in immediate succession, on a single question. Today is the
  first time it's been tested across a multi-day gap on a full question set,
  and it did not hold. Root cause not established — could be floating-point
  non-associativity in batched inference, a silent model-version rotation
  behind a stable deployment name, or something else — worth knowing this is
  unconfirmed rather than assuming a mechanism.
- Stress-question results reviewed individually, not just as an aggregate
  average, matching the discipline of checking real per-row content rather
  than trusting a summary number:
  - Arithmetic and abstention questions: near-parity between the two models,
    both correct.
  - Multi-clause synthesis question (default consequences): both models made
    the same partial-answer mistake — neither surfaced Section IV's
    interest-escalation clause, both caught only Section VI's acceleration
    clause. Doesn't discriminate between candidates; flags a shared
    limitation (likely a prompting gap, not a model-selection lever) worth
    remembering if M5's real Q&A needs multi-clause synthesis.
  - Payment-ordering question: the one real per-question gap (F1 0.643 mini
    vs. 0.333 `gpt-5-4`) — but traced to response format, not substance:
    `gpt-5-4` answered with a numbered Markdown list plus a citation, mini
    with one plain sentence closer to the ground truth's shape. Both
    correctly identified the actual order.
  - Overall conclusion on the original open question (was the Aug 5 tie a
    ceiling effect from an easy document, or a real model-quality artifact):
    making the test harder did not surface a latent capability gap between
    the two models. They converged on the same successes and the same shared
    blind spot; the one place they differed was formatting, not correctness.
    Strengthens rather than weakens the case that this is a genuine
    characteristic of this model pair on this task type within what's been
    tested, not a test-design artifact.
- M6 model decision made: **`gpt-5-4-mini`**, for M5's RAG-grounded Q&A.
  Basis: quality parity confirmed across two independent evaluation runs (14
  questions total, including 4 designed specifically to stress harder
  reasoning than the original set), reinforced rather than undercut by the
  harder questions; a real, though not fully primary-sourced, ~3x per-token
  cost advantage; no latency data to weigh either way, since none was ever
  captured. M6 marked complete above — M5 is unblocked.

---

## Session — August 5, 2026

- Picked up Step 2 (`data.jsonl` assembly) where July 31 left off. Before
  writing code, re-verified the Aug 4 correction's central claim — that
  `evaluate()`'s `_rename_columns_conditionally()` unconditionally prefixes
  unmapped columns with `inputs.`, so a passthrough `model` column survives
  as `inputs.model` — against real installed source rather than trusting the
  prior note secondhand.
- That re-verification surfaced a real gap: `azure-ai-evaluation` was not
  installed in `venv1` and not in `requirements.txt` at all — the prior
  session's claim of having checked "the pinned version" described a pin
  that didn't exist anywhere in the repo. Installed it fresh (resolved to
  `1.18.3`, not the `1.18.1`/`1.18.2` cited in earlier sessions — unpinned
  installs just grab current latest, so the discrepancy was expected once
  the missing pin was found). Pinned `azure-ai-evaluation==1.18.3` in
  `requirements.txt` with a dated comment explaining why, so future
  source-level claims stay reproducible instead of silently drifting.
- Read the actual installed source
  (`venv1/Lib/site-packages/azure/ai/evaluation/_evaluate/_evaluate.py:797`)
  directly. Confirmed real, not assumed: every input column without a
  target-generated-output prefix gets renamed to `inputs.{col}` — `model`
  will reliably show up as `inputs.model` in `evaluate()`'s row-level output,
  which is what lets Step 3 split results by candidate model after the fact.
- Separate real gap found while fixing the above: `.gitignore`'s `venv/`
  pattern never matched the actual folder name, `venv1/` — same species of
  mid-string-slash miss as July 27's `results/` bug, different mechanism.
  Confirmed via `git check-ignore` (no match) and `git ls-files` (zero
  tracked, so nothing committed yet, but it was one `git add .` away from
  pulling in the full installed package tree). Changed to `venv*/` to also
  cover future numbered venvs. Also added `ai-103/scripts/data.jsonl` to the
  same "generated, not source" section as `results/`.
- `m6_assemble.py` built from scratch, working style unchanged from prior
  sessions — first pass written independently, checked and corrected in
  rounds rather than written wholesale. Real mistakes caught and fixed along
  the way, not glossed over: a relative path missing `../` (same
  `scripts/`-vs-sibling-directory gotcha `m6_generate.py` had already
  solved, just not checked against before running); four dead
  self-assignment lines (`result["x"] = result["x"]`) left over after
  removing an earlier, unnecessary newline-stripping step; unused
  `pathlib`/`os`/`datetime`/`Path` imports copied from `m6_generate.py`'s
  timestamp-naming logic that this script doesn't need, since `data.jsonl`
  is a disposable, overwritten-every-run file rather than a preserved
  history like `results/`.
- Final script: reads `results/20260730-131154_results.json` and the loan
  agreement markdown once, builds one dict per result with
  `question`→`query`, `answer`→`response`, `expected_answer`→`ground_truth`,
  a constant `context` field, and `model` passed through unchanged, then
  writes one `json.dumps()` object per line (no array brackets, no indent —
  real JSONL, not pretty-printed JSON) to `data.jsonl`.
- Verified programmatically after running it, not just by eye: `wc -l`
  confirms 20 lines; a small validation pass confirmed all 20 parse as valid
  JSON with exactly the five expected keys (`model`, `query`, `response`,
  `ground_truth`, `context`) and no blank lines.
- Step 3 (`evaluate()` run) talked through conceptually before writing
  anything — judge model `gpt-5.2`, four evaluators
  (`Groundedness`/`Relevance`/`Similarity`/`F1Score`), no `column_mapping`
  needed since `data.jsonl`'s fields already match the SDK's native names.
  Real point worth remembering going in: `evaluate()`'s aggregate metrics
  blend both candidate models together — picking an actual winner requires
  a second pass grouping the row-level output by `inputs.model` afterward,
  not just reading the top-line summary.
- Before writing `m6_evaluate.py`, re-verified three specific things against
  real source rather than assumption: `azure-ai-evaluation==1.18.3` actually
  importable in `venv1` (confirmed via installed dist-info); the judge
  deployment name, since `gpt-5.2` only appeared anywhere in the repo inside
  the Content Understanding analyzer JSON (`"completion": "gpt-5.2"`, a
  different API surface, not a chat-completions deployment reference) —
  resolved by running `az cognitiveservices account deployment list` against
  `aif-dev-wus-01`, confirming a real deployment named `gpt-5-2` (hyphenated,
  matching the existing convention) exists in the same account as the two
  candidates; and the `../iip-docs` relative-path gotcha, which turned out
  not to apply to this script at all, since `context` is already baked into
  `data.jsonl` — Step 3 never touches `iip-docs/` directly.
- `m6_evaluate.py` written (first pass independently, corrected in rounds —
  same working style as `m6_assemble.py`), and debugged through a real chain
  of distinct failures, each traced to a root cause rather than patched
  blind:
  - Six names (`evaluate`, `AzureOpenAIModelConfiguration`, and the four
    evaluator classes) were never imported from `azure.ai.evaluation` —
    caught immediately as `NameError`/`ModuleNotFoundError`-adjacent
    failures.
  - `AzureOpenAIModelConfiguration(...)` was missing `azure_deployment`
    entirely — had `azure_endpoint`/`api_key`/`api_version` but not the
    judge's actual deployment name.
  - First draft called `evaluate()` once per candidate model in a loop; real
    misunderstanding, not a typo — `evaluate()` runs once over the whole
    `data.jsonl` (both models' rows together), and the model-vs-model split
    happens after, on the output, not via repeated calls.
  - `model_config()` was being invoked three separate times (once per
    AI-assisted evaluator), each call re-fetching a live Azure key
    unnecessarily — fixed to call once and reuse the result.
  - `ModuleNotFoundError: No module named 'azure'` despite confirmed
    installation — root cause was the active terminal not actually running
    `venv1`'s Python (same species of bug as July 29's `pip`-vs-`venv1`
    mismatch); confirmed via `sys.executable`, fixed by properly activating
    `venv1` in that shell.
  - `nltk` (pulled in transitively by `azure-ai-evaluation`) blocked its own
    `regex` import with `ImportError: Blocked import ... from current
    working directory for security reasons`. Real, structural cause, not a
    stray file: `venv1` lives nested inside `scripts/`, so when a script
    runs with cwd = `scripts/`, `regex`'s real, legitimately-installed
    location resolves to a path *underneath* cwd, and nltk's new CWE-427
    defense (`venv1/Lib/site-packages/nltk/inisec.py`, added this nltk
    version) can't tell that apart from an attacker's planted file. The
    error's own suggested fix (`-P`/`PYTHONSAFEPATH`) does **not** work here
    — confirmed by reading `inisec.py`'s own docstring, which states that
    flag only isolates spawned worker processes, not the main synchronous
    process this script runs in. Real fix: the module's own documented
    escape hatch, `NLTK_DISABLE_IMPORT_SECURITY=1`, set as a real shell
    environment variable *before* Python starts — `.env` is too late, since
    `load_dotenv()` doesn't run until after the blocked import already
    fired. **Unresolved, worth a deliberate decision, not re-discovering
    each session:** this will recur on every future script that imports
    `azure.ai.evaluation` from inside `scripts/`, since it's the venv's
    location causing it, not this one script. Either keep setting the env
    var per terminal session, or relocate `venv1` outside the `ai-103` tree
    entirely. Not decided.
  - `evaluate()` was called with `input_file=`/`output_file=` — wrong
    keyword names. Real trap: `evaluate()` accepts `**kwargs`, so wrong
    keyword names don't error, they're silently absorbed and ignored.
    Python only complained about the one genuinely required argument
    (`data`) that was missing entirely; `output_file` failed silently and
    would have produced no output file at all if not caught. Fixed to
    `data=`/`output_path=`, confirmed against real installed source
    (`evaluate()`'s actual signature), not assumed.
  - `openai.BadRequestError`: `max_tokens` unsupported, "Use
    'max_completion_tokens' instead." Root cause, confirmed by reading
    `azure/ai/evaluation/_legacy/prompty/_prompty.py`: `gpt-5.2` is a
    reasoning-family model (same class as o1/o3), which rejects `max_tokens`
    and also `temperature`/`top_p`/etc. The SDK already supports this via an
    `is_reasoning_model` flag (documented on `GroundednessEvaluator`,
    `RelevanceEvaluator`, `SimilarityEvaluator`; defaults to `False`) — fixed
    by passing `is_reasoning_model=True` to all three (not `F1ScoreEvaluator`,
    which never calls a model). Real side-finding, not incidental: this also
    confirms `gpt-5-4`/`gpt-5-4-mini` are **not** reasoning-family models,
    since `m6_generate.py`'s `temperature=0` call worked fine on both — a
    reasoning model would have rejected that the same way it rejected
    `max_tokens`. Strengthens the July 28 same-family-bias reasoning for the
    judge choice: `gpt-5.2` isn't just an older generation, it's a
    structurally different model class from both candidates.
  - `openai.RateLimitError` (429), sustained and heavy, once the reasoning-
    model fix let real traffic through. Root cause, confirmed via
    `azure/ai/evaluation/_legacy/_batch_engine/_config.py` and
    `_run_submitter_client.py`: `evaluate()` runs each of the three
    AI-assisted evaluators as separate, concurrent batch jobs, each
    defaulting to up to 10 concurrent requests (`max_concurrency`,
    overridable via the `PF_WORKER_COUNT` env var) — meaning up to 30
    concurrent requests could hit the single `gpt-5-2` deployment at once,
    despite it nominally having more capacity (10) than either candidate (3
    each) per the July 27 resource table. It's not under-provisioned in
    isolation, it's getting hit by three evaluators simultaneously. Fixed
    for this run via `$env:PF_WORKER_COUNT = "2"` set in the terminal before
    running. Worth noting as a contrast to the nltk fix above: this variable
    *would* work from `.env`, since it's read at runtime inside `evaluate()`
    — well after the script's own `load_dotenv()` call — unlike
    `NLTK_DISABLE_IMPORT_SECURITY`, which has to be set before Python starts.
    Not yet moved into `.env` permanently.
- Run completed end-to-end despite the heavy 429 retries during the run.
  Verified, not assumed, that nothing silently degraded: all 60 AI-judged
  calls (3 evaluators × 20 rows) show `status: completed` in the row-level
  output; `F1ScoreEvaluator`'s `status: None` on every row is expected, not
  an error — it never calls a model, so it never has a "completed" API
  lifecycle to report in the first place.
- Real, not-yet-fixed bug in the output path: `output_path=` was written as
  a plain string, `"results/{timestamp}_eval_results.json"`, not an
  f-string — so `{timestamp}` was never substituted, and the actual file on
  disk is literally named `{timestamp}_eval_results.json`. Fix is the same
  `datetime.now().strftime(...)` + f-string pattern `m6_generate.py` already
  uses — not yet applied.
- Results reviewed programmatically (structure confirmed as
  `{rows, metrics, studio_url}`, matching `evaluate()`'s real return type —
  not assumed from the docstring alone). 20 rows confirmed, split 10/10
  between `gpt-5-4` and `gpt-5-4-mini`. Per-model grouped averages (the
  actual comparison, since `evaluate()`'s own aggregate blends both models):

  | metric | gpt-5-4 | gpt-5-4-mini |
  |---|---|---|
  | groundedness | 4.00 | 4.10 |
  | relevance | 4.00 | 4.00 |
  | similarity | 5.00 | 5.00 |
  | f1_score | 0.475 | 0.429 |

  Honest read, not a declared winner: three of four metrics are effectively
  tied (identical or within 0.1 on a 5-point scale) at only 10 questions per
  model — too small a sample to treat a 0.1 gap as a real signal. The one
  real gap is `f1_score`, favoring `gpt-5-4`. Plausibly connected to the
  July 30 finding that `gpt-5-4-mini` sometimes emits raw Markdown syntax in
  its answers (literal punctuation fused onto real words would hurt a pure
  token-overlap metric specifically, without necessarily moving an LLM
  judge's opinion) — but this is a lead, not a confirmed explanation. Real
  spot-check to run next session, not yet done: filter `gpt-5-4-mini`'s rows
  to the lowest `f1_score` values, read `inputs.response` for stray
  Markdown, and cross-check against `gpt-5-4`'s answers to the *same*
  questions (matched by `inputs.query`, not row position) to see if the
  theory actually holds or if something else explains the gap.

---

## Session — August 4, 2026

- Anne Collins engagement ended: client balked at cost — price too high for
  perceived value, not a misunderstanding or timing issue. She understood
  the offer and still declined at the already-discounted, friend-rate price.
  Taken seriously as a real signal, not explained away: no referrals
  expected from this engagement.
- Real question raised and answered today, not deferred: was M7 (re-scoped
  Aug 3 around this specific business thesis) becoming busywork — automating
  delivery of a service that just failed its first real pricing test, rather
  than solving a validated problem. Concern judged legitimate, not
  overthinking.
- Two things cleanly separated that got bundled together on Aug 3:
  1. The cert-track argument for M7 (Generative AI/agentic exam domain,
     largest weight; computer-vision gap-filling) never actually depended
     on Anne's engagement surviving — still holds.
  2. The "this is also a real business tool" argument took a genuine hit
     and doesn't get to ride along on the cert argument's coattails anymore.
- Decision: M7 decoupled from the YouTube-cleanup business thesis entirely.
  Goes back to a neutral, synthetic small-business content-review scenario
  — same technical shape (orchestrator agent, M6 eval-harness reuse, vision
  module), no longer justified by or tied to a specific unvalidated premise.
  "Is this a real business" is now an open question requiring real evidence
  (a paying, non-discounted client) before more build effort goes toward it
  specifically — not something to keep building toward on assumption.
- `rg-ycc-dev-wus-01` / `kv-ycc-dev-wus-01` left in place, not torn down —
  the governance principle behind them (real client data/credentials never
  touch the IIP lab RG/Key Vault) is reusable regardless of which business
  thesis, if any, eventually gets validated. Currently unused, not wasted.
- Anne Collins' Notion profile updated to reflect the engagement's actual
  outcome, so it doesn't sit stale.

---

## Session — August 3, 2026

- No M6/M7 code this session — this was a scope/planning session, prompted
  by a separate, real engagement (YouTube channel cleanup consulting for a
  Scottsdale realtor) starting to converge with IIP's own trajectory.
- Reviewed `agent-system-project-plan.md` (committed into this repo this
  session, previously an upload only) against this file's M0–M7 arc.
  Confirmed real convergence, not just cert-checkbox overlap: M7 was already
  a generic "light multi-agent pattern" placeholder before this business
  need existed; M6's evaluation-harness concepts (Groundedness/Relevance/F1)
  transfer directly to "is this drafted output grounded in real data,"
  regardless of domain; computer vision was a real, unfilled exam-domain gap
  in IIP through M6, and the business's thumbnail-audit need closes it.
- Three real decisions made, not assumed:
  1. Only two efforts exist (IIP + the Anne engagement) — no third,
     separate "agent-development" project to reconcile.
  2. Real client data/credentials get their own resource boundary
     (`rg-ycc-dev-wus-01` / `kv-ycc-dev-wus-01`, placeholder naming, not yet
     created) — never the IIP lab RG/Key Vault, decided ahead of need rather
     than after a boundary violation.
  3. M7 proceeds on synthetic/simulated data rather than gating on a second
     real client engagement (which the business plan's own Phase 1 requires
     before Phase 2 touches a live second client, but isn't fully
     controllable on a cert timeline). Real Phase 1 evidence still governs
     when this touches an actual second client — only the cert milestone's
     dependency on that timing was relaxed.
- M7 milestone description rewritten below to reflect this. Full reasoning
  kept in `agent-system-project-plan.md`'s own "Merge note," not duplicated
  here — this file stays the tracker, that file stays the reference.
- Nothing else in M0–M6 touched or renegotiated this session.
- `rg-ycc-dev-wus-01` / `kv-ycc-dev-wus-01` created and confirmed (`az resource
  list -g rg-ycc-dev-wus-01` returned the vault) — purge protection enabled
  at creation, not added after the fact. No longer "not yet created" as
  written earlier in this entry's M7 description.
- Anne Collins' client profile (YouTube `@LifeInArizonaRE`, website,
  Instagram, Facebook, Calendly, email, phone) logged in Notion
  ("YCC — Client Profiles" > "Anne Collins") — informal placeholder ahead of
  the real intake questionnaire (Phase 0), not in the ai-103 repo or the
  Key Vault, per this session's own reasoning above.

---

## Session — July 31, 2026

- Step 2 groundwork only — no code written this session (time went to another
  project). Research sub-step (confirm `evaluate()`'s real row schema before
  writing anything, per the same discipline as July 28's SDK-name/evaluator-class
  verification) is done and settled, not open for re-litigation.
- Verified directly against Microsoft Learn — the `evaluate-sdk` how-to page's
  data-format section, plus the individual class pages for
  `GroundednessEvaluator`, `RelevanceEvaluator`, `SimilarityEvaluator`, and
  `F1ScoreEvaluator` (full constructor + call-signature detail, not just the
  evaluator-support table). Confirmed real, not guessed:
  - `GroundednessEvaluator` (AI-assisted, needs `model_config`): `response`,
    `context` required; `query` optional.
  - `RelevanceEvaluator` (AI-assisted, needs `model_config`): `query`,
    `response` only — no `context`, no `ground_truth`.
  - `SimilarityEvaluator` (AI-assisted, needs `model_config`): `query`,
    `response`, `ground_truth`.
  - `F1ScoreEvaluator` (pure token-overlap, no `model_config`): `response`,
    `ground_truth` only — no `query`.
  - Union across all four → one `data.jsonl` row needs four flat, top-level
    fields: `query`, `context`, `response`, `ground_truth`. Confirmed against
    the how-to page's own sample row, not inferred.
- Caveat worth keeping, not glossing over: these are Learn's general API
  reference pages (most recently updated June 2026), not something pinned to
  the exact SDK version (v1.18.2) confirmed July 28. No evidence of drift
  found, but this wasn't cross-checked against a changelog — "current and
  consistent," not "pinned-version-exact."
- Real gap surfaced against the already-saved `results/{timestamp}_results.json`:
  its fields are `question` / `answer` / `expected_answer`, not
  `query` / `response` / `ground_truth`, and it has no `context` field at all
  (the loan-agreement markdown, same value every row per the July 28 context-
  strategy decision, was never saved alongside the Q&A pairs — it lives in
  `iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json`).
- Decision locked: rename the saved fields to the SDK's native names
  (`question`→`query`, `answer`→`response`, `expected_answer`→`ground_truth`)
  when assembling `data.jsonl`, rather than keeping the original names and
  using `evaluator_config`'s `column_mapping` to remap them. Reasoning: one
  less moving part, and the `column_mapping` string-template syntax
  (`"${data.column}"`) is exactly the kind of unnecessary cleverness that
  caused this session's earlier f-string bug — plain field renames are
  simpler and were the intended naming all along (questioned at the time,
  not pushed back on, since these fields were still assumed possibly
  temporary/for something else — now confirmed they're the real schema).
- Session ended here. `data.jsonl` assembly logic (read
  `results/{timestamp}_results.json`, rename the three fields, add `context`
  from the analyzer JSON) not yet started — next real step, not done today.

---

## Session — July 30, 2026

- `m6_generate.py` created, merging the three previously-separate working
  pieces: `load_qa_pairs()` (from `scratch.py`, now wrapped as a function
  rather than left as loose top-level code — deliberate, so a future importer
  of this file, e.g. an M7 multi-agent script pulling in `build_client()`,
  doesn't trigger a file read as a side effect of import, and so the parse
  can be re-called or re-pointed at a different file later without editing
  the module), plus `build_client()` and the `temperature=0` chat-completions
  call (from `m6_probe.py`, unchanged).
- One real bug caught before the merge was proven: the first draft of the
  chat call referenced `qa_pairs[0]["question"]` directly inside an f-string
  already delimited by double quotes. This only parses on Python 3.12+
  (PEP 701's relaxed f-string grammar) — tested and confirmed `SyntaxError`
  on 3.10. Works today because `venv1` runs 3.14, but was fragile and
  non-portable. Fixed by using the already-assigned `question` variable
  instead, which also removed a redundancy (that variable had been assigned
  one line earlier and gone unused).
- Single-item proof (this doc's own Next Action step 2) passed: ran
  `m6_generate.py` against `qa_pairs[0]` ("Who is the borrower?"), got "The
  borrower is Harry Sample of 321 Central Ave, Phoenix, Arizona, 85012." back
  — contains the rubric's exact expected string ("Harry Sample"), and
  reproducible: two consecutive runs, identical output.
- Real finding, not yet resolved: the model's answer is a full sentence with
  the borrower's address appended, not the rubric's terse "Harry Sample."
  Traced to a verified cause, not model quirkiness — checked the actual
  markdown fed to the model
  (`iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json`,
  `result.contents[0].markdown`) and the source document itself presents
  borrower name and address as one grammatical unit: "Harry Sample of 321
  Central Ave, Phoenix, Arizona, 85012 (\"Borrower\")." The model is quoting
  the full identifying phrase it found, not embellishing. Two contributing
  factors, both by design, not accident: (1) M6's July 28 context-strategy
  decision deliberately feeds the model raw prose markdown, not Content
  Understanding's already-separated `Borrower.FullName` /
  `Borrower.MailingAddress` fields from the same JSON, so the model never
  sees name and address as distinct; (2) the system prompt ("Answer the
  question using only information from the provided document...") gives no
  length/format constraint, so the model defaults to a complete,
  natural-language answer rather than an isolated entity. `temperature=0`
  explains the *reproducibility* of this behavior, not the *verbosity* —
  those are separate properties, worth not conflating going forward.
  Open question, not decided: whether to add a format constraint to the
  system prompt (e.g. "answer as concisely as possible, with no extra
  detail") before generalizing to the full loop, or leave it as-is and let
  step 3's evaluator (`F1ScoreEvaluator` is pure token-overlap — a correct
  but verbose answer likely scores worse on precision than a terse one)
  surface the effect as real evidence rather than pre-guessing it. Applies
  equally to both candidate models if left alone, so it may be a fair fixed
  condition rather than a confound — worth deciding deliberately, not by
  default.
- Full 10×2 loop run (`m6_generate.py`) produced 20/20 factually correct
  answers — validates the merge end-to-end, not just the single-item proof.
  Real finding: the verbosity finding above generalizes, but narrowly, not
  broadly. GPT-5.4 only appends unrequested detail (address) on the borrower
  and lender questions — the two spots where the source markdown fuses name
  and address into one clause — and stays terse everywhere else ("Arizona."
  for governing law). Consistent with "the model quotes the fused phrase it
  found," not general chattiness; true chattiness would over-add everywhere,
  not selectively. Same mechanism shows up a third time: GPT-5.4-mini's
  late-fee answer includes "(U.S. Dollars)," quoting the source's "$50 (U.S.
  Dollars)" clause verbatim, where GPT-5.4 trimmed to "$50" — inclusion of
  fused detail is inconsistent per model and per question, not a fixed rule.
- Real finding: GPT-5.4-mini is not consistently terser than GPT-5.4 — it's
  inconsistent with itself. It answers the borrower question tersely ("Harry
  Sample") but the lender question verbosely, address included, even though
  the source document phrases both parties identically ("known as [Name] of
  [Address]"). Same model, same document structure, two different behaviors
  on structurally parallel questions.
- Related but distinct finding, logged separately per its own mechanism:
  GPT-5.4-mini emits literal Markdown bold syntax (`**Scrooge McDuck**`)
  inside several answers; GPT-5.4 never does, in this sample. Verified this
  is real returned text, not a display artifact — `json.dumps()` doesn't
  escape `*` characters, so what prints is exactly what the model returned.
  Nothing in the system prompt requests formatting; likely an inherited
  default from chat-UI-style training, surfacing here even though this
  pipeline (script → plain-text field → JSON → terminal) never renders it.
  Matters for evaluation: this fuses literal punctuation onto real words
  (e.g. `**Scrooge`), a harsher mismatch against a plain-text rubric than
  ordinary verbose phrasing — compounds, rather than just adds to, the
  verbosity finding's expected effect on `F1ScoreEvaluator`.
- Minor, likely-benign finding: both models answer the late-fee question
  with "$50," not the rubric's "$50.00" — same value, different string
  formatting. Appears to affect both candidates equally, so probably not a
  model-quality signal, but worth knowing before an exact-match-style score
  reads as worse than the answer actually is.

---

## Session — July 29, 2026

- Started by tracing one real question ("Who is the lender?") end-to-end
  through the system before writing more code, per last session's own note
  that the architecture wasn't clicking. Confirmed real, not theoretical:
  `.env` → `get_endpoint()` / `get_subscription_key()` (reused directly from
  `m3_analyze.py`, not rewritten) → `AzureOpenAI` client → document text
  pulled straight from `iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json`'s
  `result.contents[0].markdown` (no fresh extraction, per July 28's context
  strategy decision) → one real chat completions call → real answer, matched
  the rubric ("Scrooge McDuck").
- Real gotcha, not part of the July 28 locked decisions: `chat.completions.create()`
  defaults to non-zero temperature — same question, same model, same document
  produced two different (both individually correct) answers across
  back-to-back runs. Fixed by setting `temperature=0` on the candidate-generation
  call, with an inline comment explaining why. Verified fixed, not assumed —
  two consecutive runs now produce byte-identical output. Matters because M6's
  premise is evidence over guessing; a model's own results need to be
  reproducible run-to-run before comparing it fairly against the other
  candidate.
- `pip install -r requirements.txt` had actually installed `openai` into a
  different Python (`AppData\Local\Python\pythoncore-3.14-64`) than `venv1`,
  because plain `pip`/`python` resolved differently across shell sessions.
  Fixed with `python -m pip install -r requirements.txt` while `venv1` was
  active, confirmed via `python -m pip show openai` pointing at
  `venv1\Lib\site-packages`. Lesson: prefer `python -m pip` over bare `pip`
  whenever more than one Python install is on the machine.
- `build_client()` extracted as a reusable function in `m6_probe.py`, wrapping
  the endpoint-fetch/key-fetch/client-construction sequence — needed since the
  eventual loop builds the client once, not per question/model. Caught and
  removed a stray `from xmlrpc import client` import (VS Code IntelliSense
  auto-add; harmless since it was immediately overwritten by the real `client`
  variable, but dead and misleading — unrelated stdlib XML-RPC module).
- The 10 Sample Q&A pairs copied out of `loan-agreement-expected-output.md`'s
  table into a new file, `iip-docs/q_a_pairs_sample.txt` (pipe-delimited:
  `query | response`), and parsed in `scratch.py` into a list of
  `{"question": ..., "answer": ...}` dicts — verified all 10 match the rubric
  exactly. Not yet merged into the client-construction script.
- Naming convention question raised and resolved: the `m{phase}_` filename
  prefix (`m3_analyze.py`, etc.) is internal milestone-tracking shorthand, not
  portfolio-clear naming for an outside reader — a real tradeoff, not
  "amateur." Decision: don't rename mid-M6; defer a full rename (every script
  + every reference in `STATUS.md`/`iip-cli-runbook.md`/imports) to one
  deliberate commit at a phase boundary, not a piecemeal change now.
- Tentative name picked for the M6 step 1 script: `m6_generate.py` — not yet
  created. Working pieces currently split across `m6_probe.py` (client +
  single-question proof) and `scratch.py` (Q&A parsing), still need merging.

---

## Session — July 28, 2026

- Confirmed `azure-ai-evaluation` SDK is still current under that exact package
  name (v1.18.2 per Microsoft Learn, page last updated July 22, 2026). Evaluator
  classes needed: `GroundednessEvaluator`, `RelevanceEvaluator`, `SimilarityEvaluator`
  (AI-assisted, need a judge model deployment), `F1ScoreEvaluator` (pure token-overlap,
  no judge needed). The Foundry/Foundry-classic doc split doesn't affect the SDK
  itself, only which portal-side reference page matches this project's resources.
- M6 design decisions locked in:
  - **Judge model:** `gpt-5.2` (already deployed). Chosen because it isn't one of
    the two candidates being compared — avoids a model (or its sibling) grading
    itself, a documented self-preference/same-family bias risk in LLM-as-judge
    setups. Known tradeoff: two generations behind the candidates, so judge skill
    may lag. Cheaply reversible if scores look off on manual spot-check — swapping
    the judge deployment is a one-line `model_config` change, not a rebuild.
  - **Context strategy:** full loan agreement text, same for every question, fed
    to both candidates — not hand-picked excerpts. Text is already available as
    plain markdown in `iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json`
    (`result.contents[0].markdown`, from the M2 Content Understanding run) — no
    fresh extraction needed. Reasoning: isolates model quality as the only variable
    under test; hand-picked excerpts would risk a second confound (bad excerpt vs.
    weak model) and could reproduce M4's legitimate "page 2 not visible" finding
    as an evaluation artifact instead of a real result.
  - **Chat call method:** `openai` package's `AzureOpenAI` client, not raw
    `requests` (unlike M3). `azure-ai-evaluation` already pulls in `openai`
    transitively for the evaluation step, so there's no dependency-avoidance
    argument left, and the SDK doesn't change the security posture — key is
    still fetched live via `az` each run, never persisted, same as M3.
- Real gotcha: Content Understanding and Chat Completions are different Azure
  OpenAI API surfaces with different `api-version` strings (`2025-11-01` vs.
  `2024-06-01`, confirmed against Microsoft Learn). Kept as two separate `.env`
  variables — `API_VERSION` (Content Understanding, unchanged from M3) and new
  `CHAT_API_VERSION` — rather than renaming, since a rename would have silently
  broken `m3_analyze.py`'s `os.environ.get("API_VERSION", "2025-11-01")` fallback.
- `.env` and `.env.example` both updated with `CHAT_API_VERSION`,
  `CHAT_DEPLOYMENT_GPT_5_4`, `CHAT_DEPLOYMENT_GPT_5_4_MINI`. `openai` added to
  `requirements.txt` — not yet installed in `venv1`, run
  `pip install -r requirements.txt` before the next script attempts to import it.
- Noted limitation, not yet addressed: the existing Sample Q&A Pairs table
  (`iip-docs/loan-agreement-expected-output.md`) is 10 simple factual-lookup
  questions only — none test cross-clause reasoning or page-2-dependent answers.
  M6 as scoped measures "which model is better at easy factual QA," not general
  robustness. Worth flagging if M6's results ever get used beyond picking M5's model.
- Session ended with config groundwork done but the step 1 script (client
  construction, prompt/message building, candidate-generation loop) not yet
  written. Also ended with the overall architecture — how `.env` config, the
  chat client, the analyzer, and the eventual evaluator actually connect
  end-to-end — not clicking yet. Worth addressing directly at the start of next
  session rather than assuming more code will resolve it on its own.

---

## Session — July 27, 2026

- GitKraken GitHub connector confirmed working after a clean PC restart (prior
  session's "sign into GitKraken" loop resolved itself) — verified against a real
  file fetch, not just a reconnect message.
- `iip-cli-runbook.md` committed into the AI-103 repo (previously Drive-only).
- `.gitignore` fixes: `venv/`, `__pycache__/` (scripts/ now has a Python venv),
  and `ai-103/scripts/results/` (generated run outputs — took two tries; the
  first pattern (`scripts/results/`) had a mid-string slash and was silently
  anchored to the repo root instead of `ai-103/`, so it never matched. Corrected
  to `ai-103/scripts/results/`).
- `m3_analyze.py` committed to GitHub along with `requirements.txt` and `.env.example`.
  One real bug fixed en route: on Windows, `az` installs as `az.cmd`, and
  `subprocess.run(["az", ...])` with default `shell=False` calls `CreateProcess`
  directly, which doesn't resolve `.cmd` via `PATHEXT` the way an interactive shell
  does — fails with `FileNotFoundError: [WinError 2]`. Fixed via `shutil.which("az")`
  in `run_az()`.
- M3 validated against the real deployed blob (`stiipdevwus01/docs/loan-agreement-promissory-note.pdf`,
  confirmed via `az storage blob list`) — every field matched the July 24 manual-verification
  baseline.
- M4 validated: flatbed scan and both angled-photo takes (7.9° and 10.4° skew) all
  extracted every rubric-graded field correctly.
  - Real finding: flatbed scan introduced one genuine OCR character error
    ("II." → "IⅡ.", a stray Unicode Roman-numeral glyph) in a section heading —
    doesn't touch any graded field, but is a real discrepancy per the rubric's
    own instruction to treat these as findings, not noise.
  - Real finding: confidence scores do **not** track document/image quality
    reliably on this analyzer — the flatbed scan often scored *higher* confidence
    than the clean PDF, and `PrincipalAmount`'s confidence went *up* slightly on
    the more-skewed photo, not down. Worth designing the M6 evaluator around this
    rather than assuming confidence ≈ quality.
  - Good validation, not a bug: `GoverningLawState` and all 4 signature fields
    came back empty on both single-page angled photos, because that data is
    genuinely only on page 2, which isn't in the photo. The model did not
    hallucinate a value it couldn't see.
  - The rubric's predicted failure mode ("character substitution errors in dollar
    figures/section numbers" from perspective skew) did **not** show up on either
    photo — worth noting as a non-confirmation, not proof it can't happen.
- GPT-5.4 and GPT-5.4-mini deployed in `aif-dev-wus-01` (West US) — GlobalStandard,
  capacity 3 each (much lower ceiling than `gpt-5-2`'s 10 — newer/high-demand models
  get tighter per-account caps right after release). Deployment names `gpt-5-4` /
  `gpt-5-4-mini`, matching the existing hyphenated convention. Model versions:
  `gpt-5.4` → `2026-03-05`, `gpt-5.4-mini` → `2026-03-17`. Both `GenerallyAvailable`,
  confirmed live via `az cognitiveservices account list-models` (not just docs —
  one web search result claimed West US wasn't supported for `gpt-5.4-mini`
  GlobalStandard; that turned out to be stale/wrong for this account).
- Full `gpt-5.x` catalog snapshot for this account (July 27, 2026), for reference:
  `gpt-5.4` (2026-03-05, default), `gpt-5.4-pro` (2026-03-05), `gpt-5.4-mini`
  (2026-03-17), `gpt-5.4-nano` (2026-03-17), `gpt-5.5` (2026-04-24, default),
  `gpt-chat-latest` (2026-05-05, Preview), `gpt-5.6-terra`/`gpt-5.6-luna`/`gpt-5.6-sol`
  (all 2026-07-09). All `MaxCapacity: 3` except where noted. Not evaluated for
  this project's model choice yet — shortlist stays GPT-5.4 vs. GPT-5.4-mini
  per the original scope decision.
- STATUS.md moved from Google Drive into this repo (`ai-103/STATUS.md`) — Drive
  has no in-place-edit tool, so every "update" there created a new dated file
  (see the five `MASTER-REFERENCE-0715.md` through `-0724.md` copies). GitHub
  doesn't have that limitation, so this file replaces the Drive copy as the
  living status doc going forward. Edited in place each session from here on.

---

## Key resources (current, live)

| Item | Value |
|---|---|
| Resource Group | `rg-iip-dev-wus-01` (West US) |
| Foundry account | `aif-dev-wus-01` (custom subdomain `aif-iip-dev-wus-01`) |
| Foundry project | `proj-iip-dev-wus-01` |
| Storage account | `stiipdevwus01` |
| Sample doc location | container `docs`, blob `loan-agreement-promissory-note.pdf` |
| Key Vault | `kv-iip-dev-wus-01` |
| Chat deployments | `gpt-5-2` (Content Understanding analyzer), `gpt-5-4`, `gpt-5-4-mini` (RAG/Q&A candidates) |
| Embedding deployment | `text-embedding-3-small` |
| Analyzer | `iip_loan_agreement_analyzer` (`ai-103/infrastructure/content-understanding/loan-agreement-analyzer.json`) |

---

## Next action

M6 is done and M5 is unblocked. Before starting M5, four small infra items
carried forward from Aug 6, none of which block M5 but all real and worth
closing out rather than re-discovering:

1. **`m6_assemble.py` confirmation output.** It prints which generate-results
   file it read but nothing confirms `m6_eval_input.jsonl` actually got
   written — add a "Saved: ..." print matching `m6_generate.py`'s existing
   pattern. Worth going one step further and writing the source
   generate-results filename into `m6_eval_input.jsonl` itself (or a
   sidecar), since there's currently no way to trace which generate-run
   produced a given eval input after the fact without checking timestamps by
   hand.
2. **`m6_evaluate.py`'s hardcoded judge deployment.**
   `azure_deployment="gpt-5-2"` is still hardcoded directly in
   `model_config()`, unlike the two candidate deployments, which are read
   from `.env`. Add a matching `.env` variable for consistency.
3. **cwd-relative paths in `m6_generate.py` and `m6_assemble.py`.** Both use
   paths relative to the terminal's current directory (`"../iip-docs/..."`),
   which only work when launched from exactly `scripts/` — hit directly on
   Aug 6 as a `FileNotFoundError` when run from the wrong folder. Fix: base
   paths on `Path(__file__).parent` instead, so the scripts work regardless
   of cwd.
4. **Relocate `venv1` outside the `ai-103` tree.** Decision made Aug 6, not
   yet executed — deliberately deferred to a session start rather than done
   at the tail end of one. Recreate fresh via `python -m venv` +
   `pip install -r requirements.txt` rather than moving the folder (avoids
   stale absolute paths baked into `pyvenv.cfg`/activation scripts at
   creation time). This is what actually removes the need for
   `NLTK_DISABLE_IMPORT_SECURITY=1` per session, rather than continuing to
   work around it — verify by confirming `sys.executable` resolves correctly
   afterward and that importing `azure.ai.evaluation` no longer needs the env
   var set at all, not by assuming the relocation fixed it.

Once those are clear (or deliberately skipped for now), M5 starts: real
vector search/index over the loan agreement, using `gpt-5-4-mini` as the Q&A
model per M6's decision — not context-stuffing, which was M6's deliberate
simplification to isolate model quality as the only variable under test.
