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

**Status as of:** July 28, 2026 (end of day)

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
  **Blocked on M6** — deliberately sequenced after the evaluator so the Q&A model
  choice is evidence-based, not guessed.
- [ ] **M6:** Evaluator harness built, used to pick GPT-5.4 vs. GPT-5.4-mini for M5.
  **In progress** — design decisions locked (judge model, context strategy, SDK
  choice, see below); `.env`/`requirements.txt` config in place. Step 1 script
  (candidate generation) not yet started.
- [ ] **M7:** Light multi-agent pattern (extraction/verification agent → Q&A agent) →
  Phase 1 complete.

---

## Latest session (July 28, 2026)

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

Before more code: re-establish the end-to-end shape of M6 — how `.env` config,
the `AzureOpenAI` client, the two candidate deployments, and the eventual
evaluator step connect — by tracing one real question through the system
concretely (real values, one actual API call, one real response), not another
prose explanation.

Then continue M6 step 1 (candidate generation): construct the `AzureOpenAI`
client from the now-configured env vars, build the system/user message pair
(system: answer only from the provided document; user: full document text +
question), loop over the 10 Sample Q&A questions against both `gpt-5-4` and
`gpt-5-4-mini`, save real responses. Step 2 (assemble `data.jsonl`) and step 3
(run `evaluate()` with Groundedness/Relevance/Similarity/F1, judge = `gpt-5.2`)
follow after. Winner (actual evidence, not reasoning) becomes the model for
M5's RAG-grounded Q&A.
