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

Current-state map lives separately too: `m7-orientation.md` in this same
folder (added Aug 28) — a one-page "what does M7 look like right now, what's
built vs. designed vs. still open" snapshot, kept current on purpose. This
file stays the chronological log; that one is the "you are here" pointer.

A gotchas/tips-and-tricks page and a master index page (once there's enough
split across pages to justify one) are deferred until real material
accumulates for them — no point building empty structure now.

**Status as of:** September 2, 2026

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
- [x] **M5:** RAG-grounded Q&A working (real vector search/index, not context-stuffing).
  **Complete (Aug 20).** `m5_index.py` (chunking, Search index creation,
  embedding, upload) built and verified end-to-end Aug 18 — 16/16 chunks
  embedded and indexed. `m5_retrieve.py` (embed query → vector search →
  assemble context from *all* retrieved chunks, not just the top-ranked
  one → grounded chat completion) built and verified end-to-end Aug
  19-20 — real live run against `loan-agreement-index`, correct answer
  ($50,000.00) despite the top-ranked chunk being the wrong one, proving
  the `top_k≥2`/join-all-chunks design actually does what it was meant
  to. Full detail, including two live-only bugs caught before the first
  run and a real retrieval-ranking finding, in the Aug 19/Aug 20 session
  notes above. One deliberate, non-blocking scope item left open: the
  test question is still hardcoded, generalizing to a CLI arg deferred
  per `main()`'s own docstring plan until a clean run happened — which
  it now has.
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
  Not built yet — scaffolding complete and design decision made (Aug 21),
  see Next action below. → Phase 1 (of IIP labs) complete once built.

---

## Latest session (August 7, 2026)

- `venv1` relocated outside the `ai-103` tree, per the Aug 6 decision —
  first item off the Next Action list. Recreated fresh at
  `C:\Users\gerar\venvs\ai-103` via `python -m venv` + `python -m pip
  install -r requirements.txt`, not moved (avoids stale absolute paths
  baked into `pyvenv.cfg`/activation scripts at creation time, per the
  Aug 6 plan). Chose a location outside *any* git repo, not just outside
  `ai-103` — `geoste-portfolio` (the actual git root, one level up) also
  holds the unrelated YCC client files, so a venv anywhere inside that
  tree stays one `git add .` away from the same near-miss already caught
  twice on Aug 6.
- Verified, not assumed, that this actually fixed the root cause: `python
  -c "import sys; print(sys.executable)"` resolved to the new venv path,
  and `python -c "import azure.ai.evaluation; print('OK')"` succeeded
  with **no** `NLTK_DISABLE_IMPORT_SECURITY` env var set in that shell —
  the real proof, per Aug 6's own note, that relocating the venv (not
  just working around the symptom per-session) was the correct fix. Old
  `scripts/venv1` deleted and confirmed gone via directory listing.
- `iip-cli-runbook.md` updated with an activation section (both
  PowerShell and Bash/Cloud Shell forms, since they differ significantly)
  so the new venv location isn't tribal knowledge next session. Real gap
  surfaced while writing it: Cloud Shell has no persistent `~/clouddrive`
  (existing lesson, see Key Lessons below), so a Cloud-Shell-side venv
  would need recreating every Cloud Shell session regardless of where
  it's relocated — not yet set up there, flagged in the runbook rather
  than assumed solved. Not a blocker for M5, which runs from the Windows
  PowerShell side per current working style.
- Next Action item 4 marked complete below. Items 1, 2, 3, 5 (confirmation
  prints/provenance, hardcoded judge deployment, cwd-relative paths,
  line-ending renormalize) deliberately left for a later session, per
  today's session-scope decision — none block M5.
- M5 started. Vector-store decision made deliberately, not defaulted:
  Azure AI Search, not a local library (FAISS or similar) — chosen because
  it's the actual AI-103 exam skill and the more resume-relevant artifact,
  even though the loan agreement is small enough that chunking isn't
  solving a real context-window problem here. Honest tradeoff, not
  hidden: the payoff is skill demonstration, not necessity, on a document
  this size.
- `srch-iip-dev-wus-01` provisioned in `rg-iip-dev-wus-01` (Free tier,
  West US). Checked first, not assumed: only one Free-tier Search service
  is allowed per subscription, and `az resource list --resource-type
  Microsoft.Search/searchServices` returned empty across the whole
  subscription before provisioning, confirming Free tier was actually
  available. `provisioningState: Succeeded`. Endpoint
  `https://srch-iip-dev-wus-01.search.windows.net`, added to Key resources
  below. Admin-key retrieval documented in `iip-cli-runbook.md`, same
  live-fetch-never-persist convention as the Foundry/storage keys —
  deliberately not stored in `kv-iip-dev-wus-01`, for consistency with the
  existing pattern rather than introducing a new one.
- `azure-search-documents` added to `requirements.txt`, unpinned (matches
  `requests`/`python-dotenv`/`openai` — only `azure-ai-evaluation` is
  pinned, for a specific verified-behavior reason, not as a default
  policy). Not yet installed in the relocated venv.
- Chunking design settled by reading the actual source markdown (the same
  file M6 used), not assumed: 15 roman-numeral sections (I–XV), each a
  clean self-contained paragraph, plus an unnumbered signature block —
  confirms chunk-by-section over fixed-token windows. Real design
  implication carried forward from Aug 6: the multi-clause synthesis
  question (needs both Section IV and Section VI) is where M6 found both
  candidate models missed Section IV's interest-escalation clause even
  with the *full* document as context. M5's retrieval top-k needs to be
  set to ≥2 deliberately — top-1 would structurally guarantee the same
  miss rather than test whether chunked retrieval does better or worse on
  it. Proposed index: `loan-agreement-index`, fields `id`/`section`
  (for citation)/`content`/`contentVector`, 16 documents total (15
  sections + signature block).
- Two ideas surfaced in discussion but deliberately not started, logged
  here so they don't get rediscovered from scratch later: (1) M7's
  orchestrator agent is a natural fit for Azure AI Foundry's AI Red
  Teaming Agent, built on Microsoft's own open-source PyRIT and invoked
  through the same `azure-ai-evaluation` SDK already pinned for M6 —
  adversarial-robustness testing reusing the M6 evaluator-harness pattern
  instead of just quality metrics. (2) Azure AI Content Safety's Prompt
  Shields as an actual defensive layer in front of M5's chat-completion
  call, not just a detector — a real, exam-relevant Azure product, not a
  new track. Neither scoped or started; both are additions to consider
  when M7 planning starts or if M5 needs a security pass, not commitments
  made today.
- Session ended before any `m5_*.py` code was written. Index schema and
  chunking approach agreed conceptually — same pattern as Aug 5's Step 3
  discussion before `m6_evaluate.py` existed — script itself not started.
  `venv1`-relocation doc updates and the Search-service/`requirements.txt`
  changes from this session not yet committed as of this writing (separate
  from the venv1 commit, which already went out as `ca3f6f1`).

---

## Session — August 10, 2026

- `m5_index.py` framework built collaboratively, not drafted blind — the
  file combines two genuinely different kinds of unfamiliar territory:
  Azure Search SDK object construction (`VectorSearch`,
  `HnswAlgorithmConfiguration`, `VectorSearchProfile` — reference-lookup
  work; nobody has this memorized, cert-track or veteran) and real
  chunking logic (regex + boundary-pairing — a genuine core-Python gap,
  not SDK-related at all). Framework: function stubs (all raising
  `NotImplementedError`), imports, `.env` var names, and `main()`'s call
  order decided; the chunking regex, index schema fields, and
  embedding-call shape left as TODOs.
- `SEARCH_SERVICE`, `SEARCH_INDEX_NAME`, `EMBEDDING_DEPLOYMENT` added to
  `.env`/`.env.example`, matching the existing `CHAT_DEPLOYMENT_*`
  commenting convention. `azure-search-documents` still needs
  `pip install -r requirements.txt` in the relocated venv — not yet
  confirmed installed.
- `chunk_by_section()` built in real rounds, same working style as every
  `m6_*.py` file — Gerard's first pass, reviewed with root-cause
  pushback, not handed a finished answer. Two real bugs caught, not
  glossed over:
  - First draft never appended the built dict anywhere inside the loop —
    rebuilt it fresh every iteration and discarded it, so nothing was
    ever actually collected into the return value.
  - Second, more fundamental bug: content was sliced as
    `text[last_end:match.start()]` (later `match.end()`), paired with the
    *current* match's id/title — but a section's content boundary is only
    knowable once the *next* heading has been seen, so the current
    match's id/title always described the wrong content block. Verified
    directly, not just reasoned about: ran the actual draft against a toy
    string and confirmed both the mislabeling and a fully dropped first
    section.
  - Real fix: two-pass approach — `list(re.finditer(...))` first, then
    `enumerate()` with a `headings[i + 1]` lookahead for each section's
    end boundary. Re-verified against the toy string post-fix: correct
    pairing, nothing dropped. Logged as a new pattern in
    `python-patterns.md` (see below) rather than left to be re-derived
    next time this shape of problem shows up.
  - Separately caught: two stray IntelliSense auto-imports
    (`from pydoc import text`, `import match` — the latter a nonexistent
    module, confirmed via a direct `ModuleNotFoundError` test) that would
    have blocked the file from running at all. Same species as the
    July 29 (`xmlrpc.client`) and Aug 6 (`anyio.Path`) stray-import bugs —
    third confirmed instance, now logged as a recurring pattern rather
    than treated as a one-off each time.
- New file `python-patterns.md` created (`ai-103` root, same
  living-document convention as this file) — a lookup for general Python
  language patterns specifically, kept separate from this file's
  Azure/git-focused Key Lessons so the two don't overlap. Seeded with
  three entries: today's two-pass lookahead-pairing pattern, the
  recurring stray-IntelliSense-import gotcha (3 confirmed instances now),
  and `**kwargs` silently swallowing wrong keyword names (generalized
  from the Aug 5 `m6_evaluate.py` bug). Meant to be added to as new
  patterns come up, not written once and left static.
- Real working-style finding, worth carrying forward rather than
  re-learning next session: Gerard's honest post-session read was that
  `m5_index.py` blended two different kinds of difficulty together in the
  moment — genuine Azure SDK reference-lookup work (not a skill gap) and
  a real core-Python gap (the lookahead-pairing pattern) that took two
  guessed-and-verified rounds plus a shown solution to land. The failure
  mode wasn't struggling — it was not recognizing quickly enough which
  kind of difficulty was in play, which led to over an hour of unaided
  guessing per instance before asking for help. Decision, not yet tested
  in practice: cap unaided attempts on core-Python-shaped problems at
  roughly 15-20 minutes before asking for a guided hint, not an hour; and
  treat SDK-object-construction-shaped problems (unfamiliar class names
  named directly in a docstring TODO) as reference-lookup from the
  start — ask for a walkthrough immediately rather than attempting to
  derive unfamiliar SDK shapes from first principles.
- `chunk_by_section()` is done and correct. Remaining `m5_index.py`
  stubs, still `NotImplementedError`, not yet attempted: three small ones
  that are pattern-matched copies of functions already written elsewhere
  in this repo (`get_search_admin_key()` — same shape as
  `get_subscription_key()` in `m3_analyze.py`, different `az` command;
  `load_document_markdown()` — same shape as the file-read already in
  `m6_generate.py`; `build_embedding_client()` — same shape as
  `build_client()` in `m6_generate.py`, open question not yet checked:
  does embeddings need a different `api_version` than
  `CHAT_API_VERSION`?), and three genuinely new-SDK-surface ones
  (`ensure_index_exists()` — vector index/field construction;
  `embed_chunks()` — `client.embeddings.create()`; `upload_chunks()` —
  `search_client.upload_documents()` plus per-item success verification,
  same silent-failure-checking discipline as `m6_evaluate.py`'s Aug 5
  lesson).

---

## Session — August 11, 2026

- `get_search_admin_key()` fixed and verified: the draft used `--name`
  (copied from `get_subscription_key()`'s `cognitiveservices` command
  shape), but `az search admin-key show` actually takes `--service-name` —
  a different flag on a same-sounding but different `az` command family.
  Same species of gotcha already logged for `get_storage_key()`'s
  differing response shape (July 27). Working correctly against
  `srch-iip-dev-wus-01` now.
- `load_document_markdown()` fixed and verified: the draft dropped the
  `["result"]` key that `m6_generate.py`'s proven read
  (`json.load(f)["result"]["contents"][0]["markdown"]`) actually uses —
  edited by feel against a copied line ("`[\"result\"]` looked redundant")
  rather than checked against the real file's shape. Root cause and habit
  logged as a new `python-patterns.md` entry, "Trusting a copied access
  chain over checking the real data" — a genuinely new category, distinct
  from the Aug 10 core-Python/SDK split: not a language gap, not an
  unfamiliar API surface, but not having looked at the actual external
  data before trusting an indexing chain into it.
- `STATUS.md`'s `## Key Lessons` section created — referenced from the Aug
  7 and Aug 10 session notes above as if it already existed; it didn't.
  Seeded with one entry: `run_az()`'s mechanics (list-args-not-shell-string
  subprocess pattern, the Windows `az.cmd`/`PATHEXT` `shutil.which()` fix
  already hit once on July 27, the live-fetch-never-persist convention it
  enables, and the `--query`-shape-varies-by-command-family gotcha behind
  today's `get_search_admin_key()` bug).
- `build_embedding_client()` real, unresolved finding — full technical
  detail and the decision to defer the rebuild in Next Action below. Short
  version: what looked like the third small pattern-matched stub turned
  into a genuine SDK-surface question once `EMBEDDING_DEPLOYMENT` was
  confirmed correct via `az cognitiveservices account deployment list`
  (exact live match, `text-embedding-3-small` — ruling out the deployment
  name as the cause) and the classic `AzureOpenAI` client still 404'd
  regardless of which api-version value was tried (`CHAT_API_VERSION`'s
  `2024-06-01`, then `v1`). Traced to Microsoft's own v1 GA migration
  guidance: Azure's current API surface for embeddings needs a
  structurally different client (`OpenAI` + `base_url`, not `AzureOpenAI`
  + `api_version`) — not just a different string passed to the existing
  one.
- Real finding worth remembering on its own: a stub that reads as "small,
  pattern-matched" from its docstring can still turn out to be genuinely
  new SDK-surface territory once actually attempted — the Aug 10
  categorization was a reasonable prediction going in, not a guarantee.
  Worth re-checking in real time as a stub develops, not just trusting the
  upfront label.
- Session paused deliberately here, not from being stuck — real progress
  made (2 of 6 stubs closed), but the `build_embedding_client()` rebuild is
  exactly the kind of work the Aug 10 rule says deserves a guided
  walkthrough with a clear head, not a tired push. `ensure_index_exists()`,
  `embed_chunks()`, `upload_chunks()` still untouched, already flagged Aug
  10 for the same guided treatment.

---

## Session — August 12, 2026

- `build_embedding_client()` rebuilt and verified, closing the stub
  deferred Aug 11. Guided walkthrough (SDK-object-construction category
  per the Aug 10/11 working-style rule): swapped
  `AzureOpenAI(azure_endpoint=..., api_version=...)` for plain
  `OpenAI(api_key=..., base_url=f"{endpoint}/openai/v1/")` — the v1 GA
  client shape identified Aug 11, not a parameter-value fix.
  `EMBEDDING_API_VERSION` removed from `.env`, since nothing reads it once
  the client stopped taking an `api_version` argument at all.
- Verified live, not just "ran without erroring" (same discipline as the
  `**kwargs`-silent-failure `python-patterns.md` entry):
  `client.embeddings.create(model=EMBEDDING_DEPLOYMENT, input="test")`
  returned a 1536-dim vector, matching `EMBEDDING_DIMENSIONS`.
- New `## Key Lessons` entry added below: classic `AzureOpenAI` vs. v1 GA
  `OpenAI` + `base_url` client shapes — generalizes past this one stub in
  case another Azure OpenAI-family client on this account hits the same
  404-regardless-of-api-version symptom.
- Three stubs remain, same guided-walkthrough category as before:
  `ensure_index_exists()`, `embed_chunks()`, `upload_chunks()`. Flagged so
  it isn't missed: `embed_chunks()`'s stub still type-hints its `client`
  param as `AzureOpenAI` — needs updating to `OpenAI` when that stub gets
  built.
- Boundary crossed starting next session, named explicitly rather than
  discovered partway through: the three remaining stubs are real Azure SDK
  for Python (`azure-search-documents`), a different, more standardized
  ecosystem than the `openai` package `build_embedding_client()` sat in.
- `ensure_index_exists()` built and verified — first stub in the
  `azure-search-documents` half of M5, boundary held as expected (see
  above). Check-first pattern: `SearchIndexClient.get_index()` on a
  `try`, `ResourceNotFoundError` on the `except` signals "doesn't exist
  yet, create it." Schema: `SimpleField` for the `id` key, `SearchableField`
  for `section`/`content` (no `type=` kwarg on `SearchableField` — it
  hardcodes `Edm.String` and silently drops anything else passed, same
  `**kwargs`-swallow shape as the existing `python-patterns.md` entry),
  `SearchField` for `contentVector` wired to a `VectorSearch` config
  (`HnswAlgorithmConfiguration` + `VectorSearchProfile`, connected by
  matching name strings, not object references).
- Two real bugs hit and fixed during typing, both self-diagnosing (loud
  errors, not silent-failure traps): `from azure.core.exception import
  ResourceNotFoundError` — missing the `s` on `exceptions`, a plain typo;
  and `type=SearchFieldDataType.Collection(SearchFieldDataType.Single(
  SearchFieldDataType.Double))` — over-extended the `.Collection(...)`
  wrapper pattern onto `.Single`, which is a plain enum member (`Edm.Single`,
  32-bit float), not a callable. Correct form:
  `SearchFieldDataType.Collection(SearchFieldDataType.SINGLE)` — one
  wrapper, one element type, no nesting `Double` inside it.
- Verified live: ran `ensure_index_exists()` twice back-to-back in one
  command against `srch-iip-dev-wus-01`. First call printed "created
  successfully" (index didn't exist yet); second call printed "already
  exists, skipping creation" (`get_index()` succeeded this time, since
  call #1 had just created it) — confirms the check-first logic is
  actually idempotent, not just written to look idempotent.
- IntelliSense comparison worth recording separately (see new
  `python-patterns.md` entry below): a full autocomplete suggestion for
  this same function offered `VectorField`/`VectorSearchConfiguration` —
  real class names, but from the original Nov 2023 vector-search preview
  (`11.4.0b6`–`11.4.0b11`), not the installed `azure-search-documents==12.0.0`.
  Confirmed via direct import check and the SDK's own changelog, not
  assumed.
- Two stubs remain, same guided-walkthrough category: `embed_chunks()`,
  `upload_chunks()`. Session paused here deliberately — deciding to sit
  with what's landed today rather than stack a third stub on top and
  risk losing it, same discipline as the Aug 11 pause before this
  function.

---

## Session — August 14, 2026

- `embed_chunks()` built and verified — closed, not a guided walkthrough
  handed over wholesale: batch call decided deliberately over per-chunk
  (`client.embeddings.create()` accepts a list `input=`, and the failure
  mode is loud either way — an exception on the whole call, no silent
  partial-success trap like `upload_documents()` has — so batching cost
  nothing in safety and saved 15 round-trips). Vectors matched back to
  chunks via each response item's `.index`, not list position/`zip()` —
  Gerard's own call, reasoned as "cheap insurance" even though `zip()`
  would also have worked here (order is contractually guaranteed by the
  batch endpoint) — right instinct for the wrong-but-harmless reason,
  worth remembering as a good default going forward regardless. Verified
  live: 16 chunks in, 16 vectors of length 1536 out (at the time, before
  the chunk-count bug below was found). Stub's stale `AzureOpenAI` type
  hint fixed to `OpenAI`; the now-dead `AzureOpenAI` import removed from
  the top of the file too.
- Real, live-only bug found and fixed, not a hypothetical: `chunk_by_section()`
  was returning **13** chunks against the real document, not the 16 always
  assumed since Aug 10 — that assumption had only ever been checked
  against a toy string, never the actual markdown, until today's live test
  on `embed_chunks()` surfaced the real count by accident. Root cause:
  the heading regex's title character class, `[A-Z\s]*`, doesn't allow
  punctuation — silently dropped `VII. ATTORNEYS' FEES AND COSTS.`
  (apostrophe) and `IX. NON-WAIVER.` (hyphen) entirely, not partially,
  since the class breaking mid-match meant no full heading match was ever
  found at those positions. Fixed to `[\-\'A-Z\s]*`, taking two real wrong
  turns first: two guessed edits that looked syntactically right but
  "didn't change the result," which turned out to be because a separate,
  hand-typed duplicate regex in the tester scratch file (left over from
  an earlier diagnostic snippet) was what kept getting tested, not the
  real function in `m5_index.py` — the actual fix had been correct the
  whole time. New `python-patterns.md` entries from today: list
  comprehensions (first genuinely new Python syntax hit this project,
  logged with the long-form/shorthand mapping that finally landed it) and
  testing a hand-copied duplicate instead of the real function (the
  tester-file trap above). Verified live post-fix: regex now finds all 15
  of I–XV correctly, including both previously-dropped headings.
- Chunk count now correctly 15, not yet 16 — the trailing signature block
  is still folded into section XV's content rather than split out as its
  own chunk, exactly as the code's own pre-existing comment already
  flagged ("folds the signature block into the final section for now —
  separate, deferred problem"). Decision made explicitly, not defaulted
  past: close this gap now rather than ship short of the docstring's and
  the index schema's stated 16-document design. Real, correctly-raised
  concern surfaced during this discussion and deliberately not solved
  today, logged so it isn't lost: today's planned fix keys off the literal
  string `"With my signature below"` (confirmed appearing exactly once in
  the real document) — document-specific, and would not generalize to a
  differently-worded loan agreement. A general solution would need to
  detect the signature block *structurally* rather than by exact wording
  — real, harder parsing problem, consciously out of scope for this lab
  per the same skill-demonstration-over-necessity tradeoff already named
  July 30, not forgotten.
- **Session paused here deliberately, not from being stuck** — real,
  legitimate fatigue (end of day Friday, an unrelated Monday interview
  weighing on attention), not a comprehension gap. Worth being explicit
  about the difference for next time: everything actually blocking
  progress today was already understood and solved (the regex bug, the
  design for the signature-block split) — what ran out was the attention
  needed to translate a fully-understood plan into typed code, not
  understanding itself. Same category of pause as Aug 11/Aug 12, just a
  different cause.

**Next action, picking back up:** in `chunk_by_section()`, after the
existing `for` loop finishes (`chunks` now holds 15 dicts) and before
`return chunks`: find `"With my signature below"` inside
`chunks[-1]["content"]`, split that string there, keep the part before it
as XV's real content, and `chunks.append(...)` a new 16th dict (same
`id`/`section`/`content` shape as the others) for the signature block
using the part from the marker onward. Then re-verify live: expect 16
chunks, `chunks[-1]["section"]` holding the signature-block text, XV's
content no longer including it. After that: `upload_chunks()` (still
untouched, same guided-walkthrough category as `embed_chunks()` was), then
`main()` end-to-end as M5's real closing verification, per the standing
plan from the start of today's session.

---

## Session — August 17, 2026

- **`chunk_by_section()` closed — the last piece of the design from Aug
  14.** Signature-block split written independently (core-Python-shaped,
  per the standing rule), through several real iterations rather than
  landed on the first attempt:
  - First draft found the split point and built the new 16th chunk
    correctly, but never wrote the "before" half back into
    `chunks[-1]["content"]` — the old full text (signature block
    included) was still sitting there, duplicated into two chunks
    instead of divided between them.
  - Second draft tried to fix that via `new_XV_content = chunks[-1]` /
    `chunks[-1] = new_XV_content`, intending the second line to save the
    edit back. Traced through live: both lines were no-ops with respect
    to that goal — `new_XV_content` was never a copy, just a second name
    for the same dict `chunks[-1]` already pointed at, so the mutation
    in between had already taken effect and the reassignment did
    nothing. Code was functionally correct, but for a different reason
    than the draft assumed. Collapsed to one line once the aliasing was
    understood: `chunks[-1]["content"] = chunks[-1]["content"][:split_point]`.
  - New `python-patterns.md` entries from today, both hit as genuinely
    new idioms rather than repeats of a known shape: slice bounds (an
    omitted `start`/`stop` runs to the sequence's boundary, not to the
    other bound — direction depends on which side of the colon the index
    sits on) and assignment aliasing a mutable object instead of copying
    it.
  - Verified live against the real document (not a toy string): 16
    chunks, section XV ending cleanly with no trace of the marker,
    `chunks[-1]` holding the full signature block through both
    signature lines and printed-name fields.
- **Real, live-only false alarm, diagnosed and closed, not a code bug:**
  after saving the working fix, `tester2.py` still printed the marker
  text as part of XV's content — looked exactly like the fix had failed.
  Root cause: `tester2.py` was being re-run in a persistent session that
  had already imported `m5_index` before the fix was saved; editing and
  saving the file doesn't make an already-running interpreter re-import
  it. Settled by extracting the actual saved function's source and
  running it fresh, independent of that session, against a real copy of
  the document — correct result confirmed the code, not the environment,
  restarting the session and re-running matched it. New
  `python-patterns.md` entry logged so this doesn't get re-diagnosed as
  a logic bug next time it happens.
- Session closed here for the day (~4pm) rather than starting
  `upload_chunks()` — a new guided-walkthrough SDK topic on the tail end
  of a day that already included the signature-block work and the
  stale-import chase is exactly the kind of thing that doesn't land well
  started late. Clean stopping point: `chunk_by_section()` fully done and
  verified, nothing left half-finished.

---

## Session — August 18, 2026

- **`upload_chunks()` written and closed — first attempt was already
  correct.** `search_client.upload_documents(documents=chunks)` plus a
  filtering list comprehension (`[result for result in results if not
  result.succeeded]`) to surface any partial failures, sourced from
  IntelliSense but understood, not just accepted — long-form mapping
  logged in `python-patterns.md` as a follow-on to the existing list-
  comprehension entry (this one adds a filter clause, the earlier one
  didn't). One naming note flagged, not required: the variable holding
  failed results was named `failed_chunks`, but it actually holds
  `IndexingResult` objects, not chunk dicts — a more accurate name was
  suggested (`failed_results`), left as the author's call.
- **Real, live bug on the first `main()` end-to-end run — a genuine
  Azure Search characteristic, not a code defect.** `upload_chunks()`
  reported all 16 succeeded; `main()`'s closing `get_document_count()`
  check, run immediately after, reported 0. Researched rather than
  guessed: Azure AI Search's push API (`upload_documents()`) is
  documented as "closest to real-time," not instantaneous, and
  `get_document_count()` reads a separately-consistent path that can lag
  behind writes by a few seconds — corroborated by an open Azure SDK for
  Python GitHub issue reporting the identical symptom (stale count
  immediately after a push write). No official published number for the
  lag. Confirmed empirically before changing anything (per Gerard's own
  call — "changing prior to confirming just smells wrong"): a standalone
  recheck of `get_document_count()` a few seconds after `main()` finished
  returned 16, proving the writes had landed and the immediate check was
  just too early, not wrong. New `STATUS.md` "Key Lessons" entry logged
  below so this doesn't get re-diagnosed as a bug next time.
- **Closing verification rebuilt as a bounded, tolerant retry loop, not
  a single immediate check.** First draft (`while elapsed < timeout:` +
  `break` on match) had a real edge case, caught before running it: the
  final `time.sleep()` before the loop's natural exit was never followed
  by a recheck, so a count that resolved right at the timeout boundary
  would still report a false warning. A proposed alternative — resetting
  the timeout indefinitely instead of ever giving up — was considered and
  rejected: it would trade away the one thing a timeout provides (a
  guaranteed stopping point that reports *something*) for no evidence-
  based benefit, reintroducing exactly the silent-hang risk this whole
  session's `upload_chunks()` work was designed against. Settled on a
  "loop and a half" restructure (`while True:` with `break` on `count ==
  len(chunks) or elapsed >= timeout`) — written independently once the
  concept was understood, correct on the first pass. New
  `python-patterns.md` entry for the pattern itself, plus a related note
  on why referencing `count` after the loop is safe here specifically
  because the loop is guaranteed to run at least once, not as a general
  Python guarantee.
- **M5's indexing half fully verified live, end-to-end, via `tester.py`
  (`from m5_index import main; main()`):** `Chunked into 16 sections` →
  index already existed, skipped recreation → `All 16 chunks uploaded
  successfully` → `Indexed: 16 documents in 'loan-agreement-index'`, no
  warning. First clean, non-stale run of the full pipeline.
- Real process note, not a Python bug: my own read of `m5_index.py`
  momentarily lagged Gerard's actual saved edit mid-session — the local
  cache used to check the `while` loop hadn't been re-fetched after his
  latest save. Caught because he pushed back on the read rather than
  assuming it was right ("I think you might have cached data"),
  confirmed by re-fetching, corrected immediately. Same species of trap
  as Aug 17's stale-import issue, worth naming as a general lesson: a
  claim about "what the file currently says" is only as fresh as the
  last fetch, on either side of the conversation.

---

## Session — August 19, 2026

- M5's retrieval half started: `m5_retrieve.py` created. `build_chat_client()`,
  `embed_query()`, and `search_chunks()` all written and code-reviewed —
  matched against the actually-installed `azure-search-documents==12.0.0`
  signatures via `help()`, not memory. `inspect.signature()` turned out
  useless against `VectorizedQuery.__init__`'s `**kwargs`-based
  construction (returns a generic `(*args, **kwargs)` signature, no real
  parameter names); the real params — `vector`, `k_nearest_neighbors`,
  `fields` — were confirmed live via `help(VectorizedQuery)` instead.
  None of the three functions has actually been executed against the
  real Azure resources yet — code-reviewed, not verified live.
- `build_context()`, `answer_question()`, and `main()` left as bare
  `TODO` stubs — genuinely unstarted, not just unwritten in the
  docstring sense.
- Real, self-caught bug, unrelated to `m5_retrieve.py` itself:
  `embed_chunks()` in `m5_index.py` had a correct `#` comment (explaining
  the `.index`-not-`zip()` choice) rewritten as a `"""..."""` block,
  under the mistaken belief that triple-quoting a string is comment
  syntax generically. It isn't — Python only treats a triple-quoted
  string as a real docstring (`__doc__`) when it's the *first statement*
  inside a `def`/`class`/module body; anywhere else it's an ordinary
  expression, evaluated and silently discarded. Caught via an ast-based
  scan of the whole `scripts/` folder for stray string-literal statements
  outside first-statement position; one other hit, in `tester.py`, turned
  out to be intentional (a saved REPL demo, not a mistake). Self-corrected
  before the session ended. New `python-patterns.md` entry drafted for
  this, to be added at the start of the next session.
- Real working-style finding, named directly at session's end rather than
  left implicit: rising confidence has been correlating with skipping
  verification, not with actually needing less of it — the docstring
  mistake above is the concrete instance. Worth treating "I'm pretty sure
  now" as a prompt to double-check once, not a signal to stop asking.
- Session ended with a stated plan, not just a stopping point: test
  `build_chat_client()`, `embed_query()`, and `search_chunks()`
  independently — same "verify against real output, don't assume it
  works because it reads correctly" discipline used throughout
  `m5_index.py`'s build — before writing `build_context()`,
  `answer_question()`, or `main()` on top of an unverified foundation.

---

## Session — August 20, 2026

- Picked up exactly where Aug 19 left off, per that session's stated
  plan. `python-patterns.md` updated with the triple-quoted-string
  finding drafted Aug 19 (see that session's notes above), including the
  confidence/verification meta-note, as a new dated entry.
- `search_chunks()`'s inline comment on `search_text=None` fixed — it
  previously overstated the parameter's effect ("it will search for all
  documents in the index"). Corrected: leaving it `None` just skips the
  separate full-text ranking component; `vector_queries`' own
  `k_nearest_neighbors` still restricts results to the top_k
  nearest-neighbor matches, not literally every document. Low-priority
  doc fix, not a behavior change.
- `scripts/tester3.py` framework built, then finished and run by Gerard
  (imports/env/`search_client` construction were the framework; the three
  test calls and their prints were his own work, including a
  `"Chat client built successfully."` confirmation print on Test 1 and,
  after a first review round, expanding the Test 3 print from just
  `results[0]` to a loop over all returned chunks).
- **All three functions verified live against the real Azure resources —
  the open gap from Aug 19 is closed.**
  - `build_chat_client()`: constructed with no exception against
    `aif-dev-wus-01`.
  - `embed_query()`: real question ("What is the loan amount?") embedded,
    returned a 1536-dim vector — matches `EMBEDDING_DIMENSIONS`.
  - `search_chunks()`: returned exactly 3 ranked chunks against
    `loan-agreement-index`:
    `III. SECURITY.` (0.6589), `I. THE PARTIES.` (0.6501),
    `II. PAYMENTS.` (0.6323).
- **Real, live finding, not a code defect — confirms a risk named before
  any of this code existed.** The top-ranked chunk (`III. SECURITY.`,
  score 0.6589) does *not* contain the answer to the test question — its
  entire content is "The loan is unsecured." (confirmed by reading the
  real source document directly, not assumed). The actual answer
  ($50,000.00) is in `I. THE PARTIES.`, which ranked **second**, 0.009
  behind the wrong top result — a near-tie, not a clean miss. `II.
  PAYMENTS.` (monthly payment detail, also genuinely relevant) ranked
  third. This is the exact scenario the Aug 7 design note predicted
  before `search_chunks()` was written: *"top-1 would structurally
  guarantee the same miss rather than test whether chunked retrieval does
  better or worse."* With `top_k=3`, both truly relevant chunks made it
  into the returned set despite neither ranking first — real evidence
  that the `top_k≥2` (here, 3) decision was correct, not just cautious.
  New `## Key Lessons` entry logged below (Azure-Search/RAG-specific
  behavior, not a Python language pattern, so it lives here rather than
  in `python-patterns.md`).
- `build_context()` built independently (core-Python-shaped, per the
  standing rule) — correct on first attempt, verified by extracting and
  running the real saved function (not retyped) against a synthetic
  3-chunk input. Docstring updated afterward with an explicit
  REQUIREMENT to join every retrieved chunk, not just the top-ranked
  one, citing the real Aug 20 test result as evidence. Along the way,
  self-taught the list-comprehension conversion of the same logic
  (`[f"[{chunk['section']}]\n{chunk['content']}" for chunk in chunks]`),
  verified identical output against the loop version before adopting it.
- `answer_question()` built independently, then two real bugs caught and
  fixed on review, neither by reading the code — both by testing the
  actual built output:
  - A double-backslash escaping bug: `f"{context}\\n\\nQuestion:
    {question}"` (copied from the TODO docstring's own instructional
    text, where the extra backslash was needed for *display*) sent
    literal `\n\n` as visible text in the prompt instead of a real blank
    line. New `python-patterns.md` entry logged for this — escaping
    that's correct inside a docstring meant for a human to read isn't
    automatically correct once copied into real, executable code.
  - The system prompt's own docstring said explicitly to swap
    "document" for "context" (since this path gets retrieved chunks, not
    the whole markdown) — the first implementation kept `m6_generate.py`'s
    original wording unchanged. Fixed to say "context" in both spots.
- `main()` built independently — three genuine bugs, all found before
  the first live run, none glossed over:
  - `get_search_admin_key()` called with three positional arguments
    (`account, rg, search_service`) against a real two-parameter
    signature (`service, resource_group`) — an IntelliSense-inserted
    extra parameter that went uncaught on review. Confirmed via a real
    `TypeError` reproduction against the actual function signature
    before the fix; would have crashed instantly on any live run.
  - `chat_deployment` read `CHAT_DEPLOYMENT_GPT_5_4` — quietly reusing
    the model M6's Aug 6 evaluation explicitly *didn't* pick
    (`gpt-5-4-mini` was the deliberate decision: quality parity + ~3x
    cost advantage). Real process finding, not just a code fix: the
    `## Key resources` table still listed both deployments as
    "candidates" months after the decision was actually made, which
    directly contributed to the model choice not being front-of-mind
    while writing this function. Table corrected (see below) alongside
    the code fix, specifically so the current, decided model is
    fast-recallable rather than requiring a re-read of the Aug 6
    narrative next time it matters.
  - Minor: one blank line instead of two before `if __name__ ==
    "__main__":`, inconsistent with the rest of the file's spacing.
- **`main()` run live for real, for the first time — clean, correct
  result, no code changes needed after the three bugs above were fixed:**

  ```
  Retrieved chunks:
  Section: III. SECURITY., Score: 0.65894884
  Section: I. THE PARTIES., Score: 0.65007085
  Section: II. PAYMENTS., Score: 0.6322609

  Answer:
  The loan amount is **$50,000.00**.
  ```

  Ranking matches the Aug 20 `tester3.py` result almost exactly (score
  deltas in the fifth decimal place, consistent with normal embedding-call
  variance, not a different retrieval). Correct — and this is the real,
  live proof of the whole day's central finding: `III. SECURITY.` still
  ranked first and still doesn't contain the answer, but because
  `build_context()` joins all three retrieved chunks rather than just the
  top one, `answer_question()` had `I. THE PARTIES.`'s actual
  `$50,000.00` figure available and used it correctly. The `top_k≥2`
  design decision from Aug 7, the Aug 20 Key Lessons entry on vector
  search's top-1 result not being guaranteed correct, and today's
  REQUIREMENT note in `build_context()`'s docstring were not
  precautionary — this is the concrete case they were written to prevent,
  and the fix held on a real end-to-end run.
- **M5 complete.** Both halves — indexing (`m5_index.py`, Aug 18) and
  retrieval/Q&A (`m5_retrieve.py`, Aug 19-20) — built, code-reviewed, and
  verified live end-to-end. One deliberate scope item left open, per
  `main()`'s own docstring plan, not forgotten: the test question is
  still hardcoded (`"What is the loan amount?"`); generalizing to a CLI
  arg or interactive prompt was explicitly deferred until "this runs
  clean once" — which it now has. Optional polish, not a blocker; M6
  precedent (small non-blocking infra items tracked separately, not
  gating milestone completion) applies the same way here.

---

## Session — August 6, 2026

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
- Committed and pushed today's work via manual `git status`/`add`/`commit`/
  `push` (GitKraken uninstalled, per current working style). Real process
  worth recording, not just the outcome: `git status` surfaced a much bigger
  working tree than expected — this repo also holds unrelated, already-
  modified YouTube Channel Consulting client files (`custom-instructions.md`,
  `living-status-doc.md`, plus several untracked ones including apparent
  client data) sitting alongside `ai-103`. Staged only today's six actual
  files by explicit path rather than `git add .`, specifically to avoid
  bundling that unrelated work into an M6 commit.
- Separately, review of the `m6_evaluate.py` diff surfaced a stray CRLF line
  ending (a `^M` git diff marks on the `data.jsonl`→`m6_eval_input.jsonl`
  rename line) — same species of issue as the existing "CRLF→LF" lesson,
  just in a `.py` file, which the existing `.gitattributes` (`*.sh eol=lf`
  only) didn't cover. Added `*.py`, `*.bicep`, `*.bicepparam` rules (all
  written as `<pattern> text eol=lf`, the complete form — `text` marks the
  file as text at all, `eol=lf` forces the ending, matching but more explicit
  than the existing `.sh` line). Real gotcha hit applying it: `.gitattributes`
  changes don't retroactively fix already-tracked file content —
  `git add --renormalize` is needed to re-stage existing files against the
  new rules. First attempt used `git add --renormalize :/` (whole-repo
  pathspec), which turned out to behave like a full `git add` across the
  entire repo, not a scoped line-ending-only fix — it staged the two
  unrelated YCC files' real pending edits right alongside the intended fix,
  the same failure mode as `git add .` moments earlier in the same session.
  Caught before committing by reviewing the staged list, not after. Fixed by
  `git reset` (unstages only, doesn't touch working-tree content) and
  re-running `--renormalize` against explicit file paths
  (`.gitattributes`, `m6_evaluate.py`) instead of a repo-wide pathspec.
  `m6_assemble.py` and `m6_generate.py` surfaced the same latent CRLF issue
  once `.gitattributes` covered `.py` files — deliberately left unfixed
  tonight rather than re-broadening scope again right after catching that
  exact mistake; queued for next session (see Next action).

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

## Key Lessons

**This is a lookup, not a manual.** Azure/infra/git-specific gotchas live
here; general Python language patterns (control flow, data structures,
stray imports) live in `python-patterns.md` instead, so the two don't
overlap — same split `python-patterns.md`'s own header already describes.
Referenced from the Aug 7 and Aug 10 session notes above as if it already
existed; it didn't. Created Aug 11 to close that gap.

### `run_az()` — the subprocess wrapper every script's Azure calls go through

**What it does:** takes a list of CLI arguments (e.g. `["cognitiveservices",
"account", "keys", "list", "--name", account, ...]`), prepends the resolved
`az` executable path, appends `-o tsv`, and runs the result via
`subprocess.run()`. Returns stripped stdout as a plain string; raises
`RuntimeError` with the real stderr on nonzero exit.

**Why args are a list, not a shell string:** `subprocess.run()` with a list
bypasses shell parsing entirely — each flag and its value must be a
separate list element (`"--name", account`, not `"--name " + account` or an
f-string). Side benefit: no shell-injection risk from a resource name
containing spaces or special characters, since nothing passes through a
shell.

**Windows-specific gotcha, already hit once (July 27):** `az` installs as
`az.cmd` on Windows. `subprocess.run(["az", ...])` with the default
`shell=False` calls `CreateProcess` directly, which doesn't resolve `.cmd`
via `PATHEXT` the way an interactive shell does — fails with
`FileNotFoundError: [WinError 2]`. Fixed by resolving the executable
explicitly via `shutil.which("az")` first, then passing that resolved path
into `subprocess.run()`.

**Convention this enables:** every credential (`get_subscription_key()`,
`get_storage_key()`, `get_search_admin_key()`, etc.) is fetched live
through this one function on every run and never written to disk or
cached — the "live-fetch-never-persist" pattern used throughout
`m3_analyze.py` and `m5_index.py`.

**`--query` shape varies by command family, not just by convenience:**
`cognitiveservices account keys list` and `search admin-key show` both
return flat objects (`--query key1` / `--query primaryKey`), but `storage
account keys list` returns a *list* of `{keyName, value}` objects (`--query
[0].value`). Same-sounding command families don't share flag names or
response shapes — check the actual command's real output shape each time,
don't assume it matches a sibling command. Same species of mistake as
`get_search_admin_key()`'s `--name` vs. `--service-name` bug, caught and
fixed Aug 11.

### Azure AI Search's push API is eventually consistent for counts/stats

**What happens:** `SearchClient.upload_documents()` returning
`succeeded=True` for every document means the service accepted the
writes — it does not mean every read path reflects them yet.
`get_document_count()` in particular can report a stale (lower, even
zero) number for a few seconds after a successful upload. Microsoft
describes the push API as "closest to real-time," not instantaneous;
there's no published guaranteed latency, and an open Azure SDK for
Python GitHub issue (#40644) reports the identical symptom — a stale
count immediately after a push write, worked around with a manual
`time.sleep()`.

**Why it's easy to misdiagnose as a bug:** the per-item upload result
(the authoritative signal that a write was accepted) and the aggregate
count (a separately-consistent read) can genuinely disagree for a short
window even when nothing is wrong. A verification check written to run
once, immediately after upload, will intermittently report a false
failure — indistinguishable at a glance from a real one.

**Fix used here:** `main()`'s closing verification (`m5_index.py`) is a
bounded, tolerant loop — recheck `get_document_count()` a few times
with a short pause between attempts (`while True:` / `break` on match or
timeout), rather than a single immediate check. A single retry with a
fixed sleep would also work; the loop just avoids hardcoding a specific
wait time that isn't documented anywhere as sufficient.

**Real instance:** `m5_index.py`'s `main()`, Aug 18 — first end-to-end
run reported `Indexed: 0 documents` immediately after `upload_chunks()`
confirmed all 16 succeeded. Confirmed as lag, not a real failure, via a
standalone recheck a few seconds later (returned 16) before any code was
changed.

### Classic `AzureOpenAI` client vs. v1 GA `OpenAI` + `base_url`

**What happens:** `AzureOpenAI(azure_endpoint=..., api_key=..., api_version=...)`
404s against a deployment (embeddings, here) no matter which `api_version`
string gets passed — including `"v1"`, which looks like it should be the
fix and isn't.

**Why:** `api_version` is a real, required parameter on the classic
client, but `"v1"`/`"preview"` were never valid values for it. Azure's v1
GA surface is a structurally different API contract, not a new version
string on the old one — it requires the plain `OpenAI` client (the same
class used against the public OpenAI API) pointed at
`base_url=f"{endpoint}/openai/v1/"`, with `api_version` dropped from the
constructor entirely, since the parameter doesn't exist on this class.

**Where this showed up:** `m5_index.py`'s `build_embedding_client()` —
found and root-caused against Microsoft's own v1 GA migration guidance
Aug 11, rebuilt and verified live (1536-dim vector returned) Aug 12.

**Habit worth building:** if changing an `api_version` value doesn't fix a
404 no matter what's tried, stop guessing at values — check whether the
API surface itself expects a structurally different client, not just a
different string passed to the one already in hand.

### Vector search's top-1 result is not guaranteed to be the right chunk

**What happens:** a single vector-search query can return its closest
match by cosine score with the actually-relevant chunk ranked second (or
lower) and a superficially-similar-but-substantively-wrong chunk ranked
first — sometimes by a very thin margin. Nothing errors; the search
"succeeds" and returns a real, valid top-1 result, it's just not the
chunk that answers the question.

**Why it's easy to miss:** a manual spot-check that only looks at
`results[0]` (the natural first instinct — "here's the top hit, is it
right?") can look convincingly wrong even when the retrieval step is
functioning exactly as designed. The fix isn't in `search_chunks()`
itself; it's in not asking a single top-1 result to carry more certainty
than vector similarity actually provides.

**Real instance:** `search_chunks()` (`m5_retrieve.py`), first live test,
Aug 20 — query "What is the loan amount?" ranked `III. SECURITY.`
("The loan is unsecured.") first (score 0.6589), with `I. THE PARTIES.`
(contains the actual $50,000.00 figure) second at 0.6501 — a 0.009 gap.
`II. PAYMENTS.` (also genuinely relevant — monthly payment amount)
ranked third at 0.6323. All three came back within `top_k=3`.

**Why this isn't a bug to fix:** the Aug 7 M5 design note deliberately
set `top_k≥2` for exactly this reason, before `search_chunks()` was
written — "top-1 would structurally guarantee the same miss rather than
test whether chunked retrieval does better or worse on it." This test
run is that reasoning confirmed against a real query, not a hypothetical
one: retrieval with `top_k=3` still surfaced both relevant chunks despite
neither ranking first.

**Habit worth building:** when spot-checking retrieval quality, always
look at the full returned set for the configured `top_k`, not just the
top-ranked result — a "wrong" top-1 doesn't mean retrieval failed if the
right chunk still made the cut lower down. Downstream, this is also the
reason `build_context()` should join *all* retrieved chunks into the
prompt, not just the highest-scored one — the chat model gets a chance to
pick the right fact out of several candidates, the same job humans do
scanning a page of search results.

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
| Chat deployments | `gpt-5-2` (Content Understanding analyzer) · **`gpt-5-4-mini` — decided M5 RAG/Q&A model** (Aug 6: quality parity + ~3x cost advantage over `gpt-5-4`, full evidence in Aug 6 session notes) · `gpt-5-4` — evaluated, not chosen, kept deployed in case a future comparison run wants it |
| Embedding deployment | `text-embedding-3-small` |
| Analyzer | `iip_loan_agreement_analyzer` (`ai-103/infrastructure/content-understanding/loan-agreement-analyzer.json`) |
| AI Search service | `srch-iip-dev-wus-01` (Free tier, West US) — `https://srch-iip-dev-wus-01.search.windows.net`, provisioned Aug 7 for M5 |

---

## Next action

**`m5_index.py` is fully complete and verified end-to-end (Aug 18).**
Every function — `chunk_by_section()` (Aug 10, regex bug fixed Aug 14,
signature-block split closed Aug 17), `get_search_admin_key()`,
`load_document_markdown()` (both Aug 11), `build_embedding_client()`,
`ensure_index_exists()`, `embed_chunks()` (Aug 12/Aug 14), and
`upload_chunks()` (Aug 18) — is built and verified, and `main()` has run
clean start to finish against the real document: 16 chunks → embedded →
uploaded → indexed, confirmed live via `tester.py`
(`from m5_index import main; main()`).

**This closes the indexing half of M5, not all of M5.** Per the
Milestones table above, M5 also requires a retrieval/query script — the
actual Q&A half — which is now started but not yet verified live; see
"Immediate next step" below.

`build_embedding_client()` closed Aug 12: rebuilt around the `OpenAI` +
`base_url` v1 GA pattern identified Aug 11 (full detail in `## Key
Lessons` — classic `AzureOpenAI` vs. v1 GA `OpenAI` + `base_url`),
verified live via `client.embeddings.create()` returning a 1536-dim
vector against `text-embedding-3-small`, matching `EMBEDDING_DIMENSIONS`.
`EMBEDDING_API_VERSION` removed from `.env` — no longer read anywhere
once the client stopped taking an `api_version` argument.

`ensure_index_exists()` also closed Aug 12: check-first against
`SearchIndexClient.get_index()` / `ResourceNotFoundError`, schema built
from `SimpleField`/`SearchableField`/`SearchField` plus a `VectorSearch`
config (`HnswAlgorithmConfiguration` + `VectorSearchProfile`), verified
idempotent via two live back-to-back calls against
`srch-iip-dev-wus-01`. Full detail, including the
`SearchFieldDataType.Collection()`-vs-`.Single()` mixup and the stale-
IntelliSense-suggestion comparison, in today's session notes above.

**Boundary now crossed, as named going in:** remaining stubs are real
Azure SDK for Python (`azure-search-documents`), a different, more
standardized ecosystem than the `openai` package `build_embedding_client()`
sat in — held true through `ensure_index_exists()`, expect the same for
`embed_chunks()`/`upload_chunks()`.

**Working-style rule, effective since Aug 10 (reconfirmed Aug 11):** for
SDK-object-construction-shaped work — unfamiliar class names or client
shapes, whether flagged as such upfront or only discovered partway into a
stub — skip independent guessing once it's recognized as that category;
treat it as reference-lookup/investigation territory and get a guided
walkthrough instead. For core-Python-shaped work (control flow, data
structures, regex), keep attempting independently first, capped at 15-20
minutes before asking for a hint. Check `python-patterns.md` before
guessing on anything that feels like a repeat of a prior shape — real
instance today: `load_document_markdown()`'s missing `["result"]` key,
now logged there.

Refinement to the guided-walkthrough format itself, surfaced during
`embed_chunks()` (Aug 14): explaining an SDK call by narrating its syntax
first (what each argument/method does) wasn't landing — too much of the
answer's shape got handed over at once, indistinguishable from what
IntelliSense also dumped unprompted, leaving nothing to actually reason
through. What worked instead, per Gerard's own diagnosis: narrate the
*data flow* first, in plain English, naming which already-built object
is being fed into which call and why ("we're taking the client object
`build_embedding_client()` built, and using its `.embeddings.create()`
method to send it every chunk's content") — *then* show the syntax. And
for any genuinely new Python idiom (not a repeat of a known shape), show
the long-form/manual version side by side with the shorthand, mapped
piece by piece, rather than asserting "this is shorthand for that" and
moving on. Apply this format going forward for both remaining
`azure-search-documents` stubs and any future guided walkthrough, not
just this one instance.

`embed_chunks()` closed Aug 14, plus a real live-only bug found and fixed
in `chunk_by_section()` the same day — full detail, including the
tester-file trap that made two correct regex fixes look like they'd
failed, in the Aug 14 session notes above.

`chunk_by_section()` fully closed Aug 17 — signature-block split written,
debugged through two real iterations (a missed write-back, then a dict-
aliasing misunderstanding that happened to be harmless), and verified
live against the real document: 16 chunks, XV clean, signature block
intact in its own chunk. A same-day stale-import false alarm (fix looked
broken, wasn't — a persistent session hadn't re-imported the edited
module) is logged in full in the Aug 17 session notes above, with a new
`python-patterns.md` entry so it's recognized faster next time.

`upload_chunks()` and `main()`'s closing verification both closed Aug
18 — full detail, including the eventual-consistency false alarm and
the "loop and a half" retry-loop design, in today's session notes above
and the new "Key Lessons" entry on Azure Search's push-API consistency
model.

**M5 is done — both halves built and verified live.** Full history in
the Aug 18 through Aug 20 session notes above; short version: `m5_index.py`
builds and populates `loan-agreement-index` (Aug 18), `m5_retrieve.py`
queries it end to end and answers correctly, with a real, live-confirmed
finding that vector search's top-ranked result isn't guaranteed to be
the right chunk — and that joining all `top_k` retrieved chunks into
context (not just the top one) is what actually protects against that
(Aug 20).

**Immediate next step:** M7 — the single orchestrator agent milestone
(see the Milestones table at the top of this file for the full scope).
Design conversation started Aug 21. Scaffolding built: a fictional
business (Riverside Hardware & Supply, orange/cream brand), a fact sheet,
a description template, and a content-item rubric with two clean control
items plus one planted flaw per audit dimension (legibility, brand
consistency, info accuracy) — all under `iip-docs/m7-riverside-hardware/`,
plus the five synthetic thumbnails themselves, deterministically rendered
via `build.py` (HTML/CSS -> Playwright screenshot, not a generative image
model — exact control over color/contrast/text mattered more than
photorealism for planted test fixtures). A Foundry Agent Service primer
was written (`agent-service-primer.md`), since M2-M6 never touched that
SDK surface (`azure-ai-agents`, distinct from the `openai`-package client
used through M6 — and distinct from the retiring Assistants API pattern,
hard retirement Aug 26, 2026).

**Real design decision made and logged (Aug 21):** the orchestrator agent
will hold the M6 evaluator and the computer-vision audit as *tools it
decides to call* (agentic/tool-calling pattern via `ToolSet`/`FunctionTool`,
auto function-calling enabled), not a fixed procedural pipeline calling
each step in order. Chosen deliberately, accepting the added complexity,
for closer alignment with AI-103's agentic exam domain and for career
relevance — not a default, a real choice.

Not yet built. First step next session: design the agent's instructions
text and the tool function signatures/wrappers — same "state what it
needs to do before typing" discipline used throughout M5 and M6, talk
through the shape before writing anything.

Two small, non-blocking items available whenever convenient, neither
gating M7:

1. **Generalize `m5_retrieve.py`'s hardcoded test question.** Currently a
   fixed string in `main()`; a CLI arg (`sys.argv`) or an interactive
   `input()` prompt would make it usable for more than one question
   without editing the file. Deferred deliberately per the original plan
   — "generalize... only after this runs clean once," which it now has —
   not forgotten, just not urgent.
2. **Consider whether M5's retrieval quality needs systematic evaluation.**
   Today's one-question spot check was manual (a human reading printed
   scores against a document they'd already read). If M5 ever needs more
   rigor than that, M6's evaluator-harness pattern (`Groundedness`/
   `Relevance`/`F1Score` via `azure-ai-evaluation`) is the proven template
   to reuse — not proposed as work to do now, just flagged as a known,
   real gap rather than an assumed non-issue.

Separately, five small M6 infra items carried forward from Aug 6, none of
which block M5 but all real and worth closing out rather than re-discovering:

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
4. ~~**Relocate `venv1` outside the `ai-103` tree.**~~ **Done (Aug 7).**
   Recreated fresh at `C:\Users\gerar\venvs\ai-103`, outside the actual git
   root (`geoste-portfolio`, not just outside `ai-103`). Verified, not
   assumed: `sys.executable` resolves into the new venv, and
   `azure.ai.evaluation` imports clean with no `NLTK_DISABLE_IMPORT_SECURITY`
   set. Old `scripts/venv1` deleted. Activation steps (PowerShell + Bash/
   Cloud Shell) added to `iip-cli-runbook.md`. Cloud-Shell-side venv not yet
   set up — separate, non-blocking gap, see Aug 7 session notes.
5. **Renormalize line endings in `m6_assemble.py` and `m6_generate.py`.**
   `.gitattributes` now covers `*.py` (added Aug 6 after a stray CRLF turned
   up in `m6_evaluate.py`, already fixed and committed), and these two
   surfaced the same latent issue once the rule existed. Fix per-file with
   `git add --renormalize <file>` — explicit paths, not a repo-wide pathspec,
   since that scope mistake already bundled unrelated files into a staging
   area once this session (caught before committing, not after).

These are independent of M5's progress — clear them whenever convenient, not
a gate on the indexing script above.

---

**Real design decision made and logged (Aug 25):** M7's orchestrator is
intended to eventually run public-facing on ostebovik.net — reachable by
real site visitors submitting their own images, not just the fixed
five-thumbnail rubric it's being built against right now. Decided in
conversation, not defaulted into: nothing in this file, the M7 handoff
docs, or `agent-service-primer.md` had committed to a deployment model
before this. The scaffolding as built — fixed rubric, known inputs and
outputs, same discipline as M5/M6 — still reads like a local evaluation
harness, and stays that way for the current build. This is a statement of
intent for later, not a change to what's being coded this week.

**Not yet designed, real gap, do not skip when this becomes live:** a
public endpoint that accepts arbitrary images from anonymous visitors and
feeds them into a billed Azure AI resource needs its own security/cost
pass before it exists — content moderation on submitted images, rate
limiting, file size/type validation, probably an auth or CAPTCHA gate, and
a hard cost ceiling. None of this is designed yet, not even loosely. Do
not wire the M7 orchestrator to a live public route until this list has
an actual design behind it, not just this flag.

**One concrete near-term consequence, already applied:** `build_vision_
messages()` in `m7_vision_test.py` takes `mime_type` as a parameter
(default `"image/png"`) instead of hardcoding it into the data URL,
specifically because visitor-submitted images down the road won't all be
PNGs. Small change made now while the cost of doing so is near zero — not
scope creep, just not closing a door for free.

---

**Vision capability confirmed live (Aug 25).** `m7_vision_test.py` run
clean, first attempt: `build_client()`, `encode_image()`,
`build_vision_messages()`, and `main()` all written and working end to
end — `gpt-5-4-mini` accepted the base64-embedded PNG via the vision
content-array format and returned an accurate, specific description
(correctly caught the two-line headline with its dash break, the brand
text, and the actual color palette, not a generic scene description).
Result saved to `scripts/results/20260825-120404_vision_test.json`.

This closes the "first concrete step" named in the Aug 21 plan. Vision
support was strongly indicated going in by two independent signals (MS
docs' family-level claim, the Foundry Toolkit catalog's per-model Image
Attachment tag) — it's now live-verified against the actual deployment,
not just documented secondhand.

**Immediate next step, unchanged from Aug 21:** design the orchestrator
agent's instructions text and the tool function signatures/wrappers for
the M6 evaluator and the CV-audit tool it will call — same "state what it
needs to do before typing" discipline used throughout M5/M6, talk through
the shape before writing anything. Today's session was the prerequisite
check, not the design work itself; that's still fully ahead.

---

**M7 evaluator-tool session (Aug 26).** Design conversation for
`m7_evaluator_tool.py` resolved the open fork from Aug 21/25: confirmed via
Microsoft's own docs (`GroundednessEvaluator`/`RelevanceEvaluator` class
references, cross-checked against the SDK source on GitHub -- not guessed)
that each evaluator object is independently callable on a single item and
returns a dict of scores immediately, no `evaluate()`/batch-JSONL-file
machinery required. `RelevanceEvaluator.__call__(*, query: str, response: str)`
-- no `context` param in the single-eval form; `GroundednessEvaluator.__call__(
*, response: str, context: str, query: Optional[str] = None)`.

**Real design decision made and logged (Aug 26):** `m7_evaluator_tool.py`'s
tool is scoped to Groundedness + Relevance only, not all four evaluators
`m6_evaluate.py` uses. `SimilarityEvaluator`/`F1ScoreEvaluator` both require a
`ground_truth` to score against, and M7's drafted marketing copy has no
defined "correct answer" -- a fabricated ground truth would produce a number
that looks like a real quality signal without being one. `m6_evaluate.py`
itself is untouched; this scoping is specific to the new tool. Also decided:
`response` passed to the tool is the drafted title *and* description
combined, not description alone (a false claim could land in either); and
`context` (the fact sheet) is deliberately **not** a parameter the agent
supplies at call time -- it's loaded once from `fact-sheet.md` at module
level, so the agent can never substitute its own version of "ground truth"
for the groundedness check.

**Infra: `CHAT_DEPLOYMENT_GPT_5_2` added to `.env` and `.env.example` (Aug
26).** Value `gpt-5-2`, matching `m6_evaluate.py`'s existing hardcoded judge
deployment -- this doesn't change `m6_evaluate.py`'s behavior, it just makes
the value available under a proper env var name for the new tool to read.
Closes half of the Aug 6 infra item #2 ("`m6_evaluate.py`'s hardcoded judge
deployment"); migrating `m6_evaluate.py` itself off the hardcode is still
optional, not done.

**`scripts/m7_evaluator_tool.py` build started (Aug 26).** `build_judge_config()`
written and verified correct -- mirrors `m6_evaluate.py`'s `model_config()`
shape. Three real bugs hit and fixed during the build, each caught by
comparing against the working `m6_evaluate.py`/`m7_vision_test.py` examples
rather than guessed: `get_endpoint()` called with no arguments (needs
`account, rg`); `AzureOpenAIModelConfiguration`'s endpoint param misnamed
`endpoint` instead of `azure_endpoint`; and a nonexistent env var name
(`AIF_AZURE_DEPLOYMENT`) instead of the real `CHAT_DEPLOYMENT_GPT_5_2`.
`FACT_SHEET_PATH` built correctly off `Path(__file__).parent`, avoiding the
known cwd gotcha. Module-level `context` load (`fact-sheet.md`'s text, read
once) is functional but doesn't yet match the codebase's `with open(...) as
f:` convention used everywhere else -- flagged, not urgent.

**Not yet written -- the actual next step:** `evaluate_draft(query: str,
response: str) -> dict` is currently an empty stub (`return
evaluation_results` with `evaluation_results` never defined). Left this way
deliberately -- the fix-and-verify loop on `build_judge_config()` worked well
enough as a teaching pattern that the next piece is being attempted
independently first, same as always. Body needs: call
`groundedness_eval(response=response, context=context, query=query)` and
`relevance_eval(query=query, response=response)`, merge both dicts, return
the result -- and the two evaluator objects themselves (`groundedness_eval`,
`relevance_eval`) still need to be constructed once, module-level, from
`build_judge_config()`'s result; that's not written yet either.

**Housekeeping note:** this STATUS.md update was itself missed at the actual
end of the Aug 26 session -- caught and backfilled here on Aug 27, at the
start of the next session, rather than losing the day's detail to memory.
Full point-by-point handoff for this same work also lives in the Claude
project as `claude/2026-08-27-m7-session-prompt.md`.

**Immediate next step, unchanged in substance:** finish `evaluate_draft()` and
the module-level evaluator objects in `m7_evaluator_tool.py`, add a small
`if __name__ == "__main__":` smoke test (same discipline `m7_vision_test.py`
used before anything got built on top of it), confirm live. After that, the
two design items flagged since Aug 21/25 are still ahead: the orchestrator
agent's instructions text, and the CV-audit tool wrapper built on
`m7_vision_test.py`'s proven vision-call pattern.


---

**`evaluate_draft()` finished and verified live (Aug 27).** The two evaluator
objects (`evaluators["groundedness"]`, `evaluators["relevance"]`) got built
module-level from `build_judge_config()`'s result, matching `m6_evaluate.py`'s
own `evaluators` dict pattern rather than the two-flat-variables shape first
sketched — a better fit since it reuses the same key names the merge step
needs anyway. One real bug caught before the first run: IntelliSense
suggested calling `.evaluate(...)` on the evaluator objects, which doesn't
match what got confirmed via MS docs on Aug 26 (the objects are directly
callable, no `.evaluate()` method) — caught by checking against the
documented signature rather than trusting the suggestion, fixed before
running anything. `evaluation_results` ends up nested (`{"groundedness":
{...}, "relevance": {...}}`), a deliberate choice over a flat merge to avoid
a key collision between the two evaluators' own output dicts.

**Smoke test built and run against real fixture data, not invented text
(Aug 27).** `main()` / `if __name__ == "__main__":` uses Item 1 ("How to Mix
Exterior Paint Colors at Home") — the clean-control item from
`content-items-plan.md` — with the title and description already written as
the worked example in `description-template.md`, so the test checks against
a documented expected result instead of just confirming the code doesn't
throw.

**Real design decision made and logged (Aug 27): what `query` represents for
M7.** First run used the bare item topic as `query`
("How to Mix Exterior Paint Colors at Home") and `RelevanceEvaluator` failed
it (2.0, threshold 3) — reasoning: the response is promotional copy for an
in-store service, not literal at-home mixing instructions, so it didn't
"answer" the topic read as a how-to question. Root cause: `RelevanceEvaluator`
is shaped for RAG Q&A (query = a real question, response = the answer to
it); feeding it a bare topic title as if it were a question was a mismatch
with what the description is actually for (hook/body/CTA marketing copy, per
`description-template.md`'s own format spec) — not a defect in the drafted
text or the evaluator. Fix: reframed `query` as the actual drafting
instruction the orchestrator agent will eventually be given —
`"Draft a video title and description for a piece of content about:
'<topic>,' grounded in the store's fact sheet."` — closer to what
`RelevanceEvaluator` is meant to grade against. Rerun: relevance passed
(3.0, right at threshold — reasoning still notes some at-home/in-store
tension, just not enough to fail). Confirmed live, not just predicted.

**Side finding from the same rerun:** groundedness's score didn't move (4.0,
still pass) but its *reasoning* did — this run's judge specifically flagged
that "matched to any swatch or sample you bring in" and "we'll mix it while
you shop" aren't stated in `fact-sheet.md`'s Services list, just plausible
marketing embellishment. Checked against the fact sheet directly: correct,
those two claims aren't there. Worth understanding why the reasoning changed
between runs even though `response`/`context` didn't: `evaluate_draft()`
passes `query` into *both* evaluator calls (`GroundednessEvaluator.__call__`
takes `query` as an optional param, confirmed Aug 26), so the relevance fix
also shifted what the groundedness judge scrutinized. Not a bug — documented
behavior, just easy to miss since only the relevance side was the intended
target. The embellishment itself is a pre-existing minor nit in
`description-template.md`'s own reference example, not something introduced
by this test — flagged here, not fixed, not urgent.

**`m7_evaluator_tool.py` considered done and verified.** Both evaluators now
pass against Item 1's real fixture data, matching `content-items-plan.md`'s
documented expectation ("description drafts clean and grounded") for the
first time, with defensible, non-rubber-stamp reasoning behind both scores
rather than a suspiciously clean pass.

**Immediate next step, unchanged:** the orchestrator agent's instructions
text and the CV-audit tool wrapper (built on `m7_vision_test.py`'s proven
vision-call pattern) — both flagged since Aug 21/25, talk through shape
before writing anything, same discipline as always.


---

**Repo housekeeping and site work (Aug 27, second half of session).** Pushed
today's M7 commit (`4f8d62d` — `m7_evaluator_tool.py`, the Riverside Hardware
rubric, `m7_vision_test.py`, `agent-service-primer.md`) to `origin/main`.
While confirming the push, found a real gap in `.gitattributes`: it only
forced `eol=lf` on `*.sh`/`*.py`/`*.bicep`/`*.bicepparam`, never on HTML or
YAML — so `az-104/networking/index.html` and the SWA GitHub Actions workflow
file had both silently drifted to CRLF locally (100% line-ending noise, zero
real content difference from what's committed, confirmed byte-for-byte
before touching anything). Closed both gaps: `*.html text eol=lf` added and
`az-104/networking/index.html` renormalized (`8be60e5`); `*.yml`/`*.yaml
text eol=lf` added and the workflow file renormalized (`70c5880`) after
confirming directly against github.com that
`azure-static-web-apps-polite-beach-008d6f51e.yml` is in fact the only and
active deploy workflow, not an orphaned one. Both fixes used the same
scoped-path `git add --renormalize` pattern already established for the M6
CRLF fix, not a repo-wide pathspec.

**`gh` CLI installed and authenticated on the Windows machine (Aug 27).**
Real capability gained for direct use in PowerShell/terminal — but does not
extend to Claude's `device_bash` sandbox, which runs in its own isolated
Linux VM with access only to the mounted folders, not to programs installed
on Windows. Same is true of `az`: neither CLI is reachable from that sandbox
even when installed and authenticated on the actual machine. Worth
remembering next time this comes up rather than re-discovering it.

**Application Insights web tracking added to the live portfolio site (Aug
27).** `appi-prod-wus3-01` was already fully provisioned (workspace-based,
correctly linked to `law-prod-wus3-01`, 30-day retention) and its own bicep
module comment already said "Captures page views, browser performance, and
custom events" — but nothing in `index.html` actually loaded the
client-side SDK before now; the connection string was only ever wired
server-side as an SWA app setting. Fetched the current, official
Application Insights JS SDK loader snippet live from Microsoft's docs
(deliberately not reconstructed from memory, given how easy a long minified
loader is to get subtly wrong) and inserted it at the top of `<head>` with
the real connection string. Confirmed the connection string is meant to be
public in client-side code (a write-only ingestion identifier, not a
security token) before treating it as safe to commit in plain text.
Verified before committing: LF line endings preserved, file parses clean
under Python's HTML parser, `git diff` shows a purely additive 10-line
change with nothing else in the file touched. Committed as `7ec477f`.
Live-verification method flagged for next check: Application Insights' own
dashboards lag a few minutes on ingestion, but the Portal's Live Metrics
pane under `appi-prod-wus3-01` → Investigate updates in near real time —
better first check than waiting on the normal charts.

**End of session: all pushed, `origin/main` clean at `7ec477f`.** Confirmed
directly (`git fetch` + compare, not assumed) — nothing outstanding on the
git side going into the next session.

**Immediate next step, unchanged from today's housekeeping:** the
orchestrator agent's instructions text and the CV-audit tool wrapper (built
on `m7_vision_test.py`'s proven vision-call pattern) -- both flagged since
Aug 21/25, talk through shape before writing anything, same discipline as
always. Today's work was infra/site hygiene, not M7 build progress — M7
itself is exactly where the last entry left it.

---

**Application Insights Live Metrics limitation identified, page-view tracking confirmed working (Aug 28).**
Live Metrics blade for `appi-prod-wus3-01` shows "Not available: couldn't connect to your application"
— checked Microsoft's own docs (`live-stream` article): Live Metrics is a **server-side-SDK-only**
feature (.NET, ASP.NET Core, Java, Node.js, Python server SDKs). It does not work with the
client-side/browser JavaScript SDK under any configuration, because it requires a continuous
open connection between a running app process and the portal so the portal can push filters —
a static site with no backend process has nothing to hold that connection open. This is a
structural mismatch with `ostebovik.net`'s architecture (Azure Static Web App, no server API),
not a misconfiguration. Live Metrics will never work here and should not be used to verify this
integration going forward.

Real confirmation instead came from Monitoring > Metrics: "Page views (Count)" for
`appi-prod-wus3-01` showed 2 recorded page views from testing the day after the Aug 27 change
(`7ec477f`). That's the correct verification path for a static-site client-side AI SDK
integration — **Application Insights web tracking is confirmed working.**

---

**M7 session (Aug 28): orientation doc, FunctionTool mechanics, CV-audit tool
framework built and first-drafted.** Full detail lives in this session's
history above (Live Metrics finding) and in the new files themselves; this
entry is the session-close summary.

- Confirmed Aug 27's unpushed commit (`63aa616`) is now pushed — `origin/main`
  even with local `main` as of tonight. A stale `.git/index.lock` (left by a
  `device_bash`-run `git fetch` that couldn't clean up after itself, since
  that sandbox can't delete files without explicit permission) sat unresolved
  most of the session; cleared tonight with Gerard's explicit delete-permission
  grant, immediately before this commit.
- Application Insights Live Metrics investigated and resolved as a
  non-issue — see the dedicated entry above (Live Metrics is server-side-SDK
  only, confirmed against Microsoft's docs; real tracking confirmation came
  from the Metrics blade instead, which showed real page views).
- **New file: `m7-orientation.md`.** A current-state-only architecture map
  (not a log, not a plan) built after Gerard flagged genuine difficulty
  tracking where each session's work fit into the whole, across the growing
  pile of docs/scripts. Also now holds a consolidated backlog section pulling
  together every scattered "not urgent" item from past sessions into one
  place, per Gerard's stated preference — check there first for deferred
  work, not STATUS.md scrollback.
- **`agent-service-primer.md` extended** with a verified section on how
  `FunctionTool` actually reads a Python function (docstring format is
  reST-style `:param:`/`:return:`/`:rtype:`, not free-form; functions should
  return JSON strings, not raw dicts) — checked against the real
  `azure-ai-agents` SDK source after an initial search surfaced a different,
  not-applicable function-calling pattern.
- **New file: `scripts/m7_cv_audit_tool.py`.** Framework built (client with
  its own bumped `STRUCTURED_OUTPUT_API_VERSION`, since the shared
  `CHAT_API_VERSION` predates structured-outputs support — logged in the
  orientation doc's backlog, not fixed now), `ThumbnailAudit` pydantic
  schema (text_legible/brand_consistent/info_accurate/notes), and
  `audit_thumbnail()`'s full signature/docstring. Gerard wrote the actual
  `system_prompt`/`user_prompt` himself as a deliberate prompt-engineering
  exercise — hit a real Python syntax error (a plain-quoted string can't
  span multiple lines; needed a triple-quote), fixed together, then
  incorporated real fact-sheet interpolation, a brand-consistency carve-out,
  and trimmed a redundant JSON-shape instruction now that structured outputs
  handles that. Verified live (not just read-through): ran
  `build_audit_messages()` directly and confirmed the real fact sheet content
  interpolates correctly with no leaked placeholder text.
- **Not yet run against real Azure at all.** `audit_thumbnail()` itself
  (the actual `response_format=ThumbnailAudit` call) has never executed —
  whether structured outputs actually works against the `gpt-5.4-mini`
  deployment on the bumped API version is a genuine unknown, not assumed
  either way.

**Next action:** write `main()`'s test loop in `m7_cv_audit_tool.py` —
run `audit_thumbnail()` against all 5 `content-items-plan.md` fixtures,
compare actual output to that file's expected-results table, same discipline
as `m7_evaluator_tool.py`'s own `main()`. This is also the first real test of
whether structured outputs works on this deployment at all.

---

**M7 session (Aug 29-31): CV-audit `main()` written and run live for the
first time; text_legible root-caused via staged reliability/generalization
testing; new brand_consistent regression found, unresolved.**

- **`main()` written (by Gerard, reviewed together)** in
  `m7_cv_audit_tool.py`: loops the five `content-items-plan.md` fixtures,
  calls `audit_thumbnail()` on each, diffs actual vs. expected across all
  three fields, prints a pass/fail summary. Fixed a handful of typos before
  the first run (missing space, `/n` vs `\n`, "Aditing") plus one real bug
  on my side -- an f-string double-brace (`f"{{k: actual[k] for k in
  expected}}"`) that never evaluates the dict comprehension, since double
  braces escape to literal text; Gerard fixed it correctly with single-brace
  spacing.
- **`EXPECTED_RESULTS` discussed and deliberately kept hardcoded** in
  `m7_cv_audit_tool.py` rather than externalized to a separate file -- a
  real best-practice tradeoff talked through, not a default: at this
  project's size a separate file is one more thing to keep in sync for no
  real benefit. Verified the dict's values against `content-items-plan.md`
  directly before the first run.
- **First live run: structured outputs confirmed working.**
  `response_format=ThumbnailAudit` against `gpt-5.4-mini` on the bumped
  `STRUCTURED_OUTPUT_API_VERSION` worked with no fallback needed -- the last
  genuine unknown from Aug 28's framework build, now resolved. Result: 4/5,
  item3 (`item3-tool-rental-FLAW-legibility.png`) failed `text_legible`
  only.
- **Confirmed reproducibility before drawing any conclusion**, per Gerard's
  explicit call that one failure isn't evidence. Reran item3 alone 5x
  against the *original* wording (`tester2.py`, reused rather than adding a
  new file) -- 5/5 `True`, i.e. the original single failure didn't
  reproduce as a stable pattern on its own. That result was ambiguous
  (noise? boundary condition?), so testing moved to controlled variants
  rather than guessing.
- **Built four controlled diagnostic thumbnail variants** to isolate one
  variable at a time (`iip-docs/m7-riverside-hardware/
  build_legibility_diagnostics.py`, kept deliberately separate from the
  official `build.py`/`ITEMS`): diag-a (heavy visual clutter), diag-b
  (near-zero title/background contrast), diag-c (title color pushed as
  close to background as CSS allows), diag-d (3px title font). Hit and
  fixed a real cross-platform bug along the way -- see the new
  `python-patterns.md` entry. All four variants under the *original*
  wording came back `text_legible: True` at 5/5 (`probe_legibility_
  variants.py`, renamed from `tester4.py`), ruling out clutter and gradual
  contrast loss as the cause entirely -- even zero-contrast and 3px-font
  images were reported legible.
- **Printed the model's full `notes` reasoning for the first time**
  (`probe_legibility_detail_level.py`) instead of just the boolean, at both
  default and `"detail": "high"` -- detail level made no difference. The
  notes revealed the actual mechanism: every response cited only the
  ever-present "RIVERSIDE HARDWARE & SUPPLY" business-name wordmark as
  evidence of legibility, never the manipulated title text. **Root cause:
  an existential-vs-universal quantifier bug.** The original wording asked
  whether *any* text was legible -- trivially satisfied by the wordmark
  regardless of what happened to the title, and not a vision-perception
  limitation at all.
- **Rewrote `text_legible`'s wording** (Gerard drafted, I critiqued each
  draft -- flagged one real regression risk in an earlier draft that would
  have told the model to assume unverifiable "invisible" text exists,
  reinforcing the confabulation pattern rather than fixing it) to require
  each distinct text element to be judged on its own, with an explicit "do
  not weight any single element more heavily than another" instruction.
  **Confirmed saved in the live file as of tonight** (`m7_cv_audit_tool.py`,
  the `text_legible` line in `build_audit_messages()`).
- **Reran diag-c/d under the corrected wording:** diag-c stable at 5/5
  `True`; diag-d showed genuine run-to-run variance, 1 `False` / 4 `True`
  -- a real signal that the corrected wording sits near a genuine boundary
  for very small fonts, not settled either way yet.
- **New regression found on the final full run.** A complete 5-fixture run
  under the corrected (and, this time, actually-saved) wording again
  produced 4/5 -- but item3 now fails on **both** `text_legible` and
  `brand_consistent`, which had never failed before. Gerard caught his own
  process error here: an earlier "full run" that appeared to show all-pass
  was actually rerun on an unsaved edit and isn't valid data. Not yet
  determined whether the regression is run-to-run noise (no `temperature`
  pinned anywhere in the client) or a real ripple effect from editing
  `text_legible`'s section of a shared multi-field system prompt --
  **this is tomorrow's first priority.**
- **New file:** `iip-docs/m7-riverside-hardware/build_legibility_
  diagnostics.py` (diagnostic variant builder, separate from official
  content).
- **New files:** `scripts/probe_legibility_variants.py` (renamed from
  `tester4.py`) and `scripts/probe_legibility_detail_level.py` -- both
  under a new `probe_<what-it-tests>.py` naming convention adopted for
  descriptive test/QA scripts going forward (existing `tester.py` /
  `tester2.py` / `tester3.py` intentionally not renamed -- no retroactive
  doc-churn on closed artifacts).
- **`scripts/requirements.txt`:** added `pydantic` and `playwright` (both
  real, previously-uncaptured dependencies). Playwright also needed a
  separate `playwright install chromium` step to fetch the browser binary
  -- `pip install` alone doesn't do that.
- **Full backlog additions** (diagnostic-thread details, `temperature`
  pinning consideration, `build.py`'s own latent path bug, a general
  confabulation-risk note) filed in `m7-orientation.md`'s backlog rather
  than here -- check there, not this entry, for the full list.

**Next action:** resolve the `brand_consistent` regression on item3 first --
several plain reruns under the current saved wording, no prompt changes
yet, to characterize whether it's noise or a real ripple effect. Then
confirm diag-c/d stability with more runs, decide on the untested
"expected-but-absent" wording for diag-c, and do one more full 1-5
regression pass before considering `text_legible` closed.

**M7 session (Sep 1): brand_consistent regression resolved (was noise), temperature/seed pinned, info_accurate wording fixed and verified on item2.**

**Confirmed the working folder fresh (`ai-103`) and read `m7-orientation.md`
first, per standing rule, before touching anything.** Git state going in
matched the Aug 31 write-up exactly (`HEAD` `a7085c7`, three days of
uncommitted work) -- but by the time this session picked it up live, that
work had already landed as `540a6fb`/`7924df2` (from a separate thread of
work this same day), so nothing was actually uncommitted. Worth noting for
next time: the "next session prompt" doc can go stale between being written
and being picked up if other work touches the same repo in between --
`git status`/`git log` fresh at session start, don't just trust the doc's
git-state section.

**`temperature=0`/`seed=42` pinned on the audit call (`m7_cv_audit_tool.py`,
`audit_thumbnail()`), ahead of the brand_consistent reruns rather than
after.** Deliberate reordering from the plan Aug 31 left off on: pinning
first turns "run it a few times and eyeball stability" into a clean
noise-vs-ripple-effect test instead of conflating two unknowns in one
unpinned signal. Dated comment left on the `.parse()` call explaining the
reasoning and noting neither param guarantees bit-exact determinism on
Azure OpenAI, just substantially reduces variance.

**7 manual runs of the unmodified (pre-fix) tool, all 5 fixtures, temperature
and seed pinned.** Findings, tabulated per fixture across all 7 runs:

- **`brand_consistent` never failed on item3 once.** The regression this
  session was written to chase looks resolved -- most likely the noise (or
  the specific invalid unsaved-edit run) STATUS.md already flagged as
  suspect from the Aug 31 write-up. Treating this thread as closed.
- **item3's `text_legible` failed 7/7, identical reasoning every run**
  ("headline... also readable despite the low-contrast overlay"). Not the
  old wordmark-citation bug -- the model explicitly engages the manipulated
  headline every time and still judges it legible. Fully characterized now,
  not noise: this is a real mismatch between the fixture's design intent
  (`content-items-plan.md`: "readable to a human only with effort, if at
  all") and the model's actual legibility threshold. Open item, next up.
- **item2's `info_accurate` came back genuinely unstable: 4 True / 3 False
  out of 7, even with temperature and seed both pinned.** New finding, never
  documented before. Checked `content-items-plan.md` directly: item2 is
  designed with "no factual claims" at all, so any `False` here is a wrong
  answer by design intent, not an open interpretive question. Root cause:
  the model was inconsistently reading the headline ("Seasonal Home
  Maintenance Checklist") as an implied service claim -- `info_accurate`'s
  wording never distinguished a topic/headline from an explicit factual
  assertion.

**`info_accurate`'s wording rewritten to fix item2, iteratively -- Gerard
drafted each pass, Claude critiqued.** Went through several revisions:
"claims" -> "offerings" (flagged as moving the wrong direction -- "offering"
leans toward "thing sold," which is closer to the misreading causing the
bug, not further from it) -> "assertions" (the actual right term for this
job -- a declarative statement asserted as fact, standard fact-checking
vocabulary). Added an explicit independent-evaluation clause (kept
"accuracy, or lack thereof" over "inaccuracy" alone -- deliberately both-
directional, since an accurate claim shouldn't excuse an inaccurate one but
also shouldn't get contaminated by one, the same halo-effect risk flagged
for `brand_consistent`). Final, missing piece added last: "A headline or
title describing the content's topic is not itself a checkable assertion"
-- this was the actual fix; the noun-choice iteration helped but wasn't
sufficient on its own. `build_audit_messages()`'s docstring updated to match
(had gone stale on the old wording).

**Verified via a new script, `probe_fixture_stability.py` -- 7 runs,
automated, matching the manual batch size.** Result: item2 now 7/7 clean
pass, up from 4/7 -- fully converged, not just improved. Items 1/4/5
unaffected (still 7/7 as before), item3 unchanged at 7/7 fail on
`text_legible` -- confirms the fix was isolated to exactly the field it was
supposed to touch, no ripple into anything else. Script mirrors
`probe_legibility_variants.py`'s conventions (module docstring, `RUNS`/
`STABLE_THRESHOLD` constants, no `main()` wrapper) and saves full per-run
records (booleans + notes, not just a tally) as timestamped JSON in
`scripts/results/`.

**New design constraint logged in `content-items-plan.md`, not just code.**
The headline-exemption fix means a future flawed item's info-accuracy
violation can't live inside the item's own headline/title -- it has to be a
separate visible element, the way item5's "OPEN 24/7" callout already is.
Logged there specifically (not just as a code comment) since that's the doc
actually consulted when designing new fixture images, not something that'd
get read mid-image-creation.

**Next action:** item3's `text_legible` miss on the tool-rental fixture --
same "one thing at a time" discipline that just worked for `info_accurate`.
Open question is a calibration one, not a wording-clarity one: either the
fixture's low-contrast manipulation isn't strong enough to cross this
model's actual legibility threshold, or the wording needs to define
"legible" more strictly (e.g. "readable at a glance, without deliberate
effort") to match the fixture's own design intent. Real risk to watch for:
overcorrecting could make item1/2/4/5's genuinely-legible text start failing
too -- a new false-positive problem mirroring the one just fixed on item2.
Use `probe_fixture_stability.py` to verify whatever gets drafted, same
rhythm as today.


**M7 session (Sep 2): `text_legible` calibrated and fixed on item3 -- and
cross-check contamination confirmed, with `info_accurate` regressing on
item2 and item3 as a direct consequence of that fix.**

**Confirmed the working folder fresh and read `m7-orientation.md` first,
per standing rule.** Git state clean going in: `HEAD` `4b52e2b`, `main` in
sync with `origin/main`, nothing uncommitted but the session-prompt doc
itself.

**Fixture-strength hypothesis ruled out by arithmetic, before spending a
run on it.** The Sep 1 handoff left two competing explanations for item3's
7/7 `text_legible` miss: (1) the fixture's low-contrast manipulation isn't
strong enough to cross the model's real legibility threshold, or (2) the
wording's bar for "legible" is looser than the fixture's design intent.
Pulled item3's actual colors from `build.py` (`title_color` `#F2803D` on
`bg_color` `#FD5A1E`) and computed the WCAG contrast ratio: **1.19:1**,
against a 3:1 minimum for large text and 4.5:1 for normal text. The fixture
is not underpowered -- it sits at roughly a third of even the lenient
large-text threshold, matching `content-items-plan.md`'s "readable to a
human only with effort, if at all" closely. Hypothesis 1 closed without a
35-call run.

**Wording change (Gerard drafted, Claude critiqued -- same rhythm as Sep
1).** Two edits to `text_legible`'s clause only; no other check touched:
added "or vice versa" so an illegible element can't drag a legible one
down (the reverse direction of the halo effect already guarded the other
way), and added a bar -- "Legible should be defined as readable by a
typical human without undue effort or assistance." The "typical human"
anchor is the load-bearing part: the model can resolve text from pixel data
that a person glancing at a thumbnail could not, so the question had to be
posed about a human observer rather than about the model's own capability.

**Claude predicted this wording would fail, and was wrong -- logged
because the prediction was stated before the run.** The critique argued
"undue" was a hedge (excessive effort, not merely effort) that would leave
the same loophole open, and predicted item3 would stay `True` with notes
reading "some effort but readable." The run falsified that: item3's
`text_legible` went **7/7 True to 0/7 True (7/7 correctly False)**, with
consistent right-reason notes every run -- "the business name at the bottom
is readable, but the main headline text in the center is too faint/overlaid
to be clearly legible as a separate text element." Both the Aug 29
quantifier fix and the new bar are holding, and `text_legible` is now
correct and stable across all five fixtures.

**The overcorrection risk did land -- but in a different check than the one
warned about.** The stated risk going in was that a stricter legibility bar
would make item1/2/4/5's genuinely-legible text start failing. It did not
(`text_legible` is now 7/7 correct on every fixture). Instead
`info_accurate` regressed, on a clause that was never edited this session.
Diffed run-for-run against the Sep 1 baseline
(`results/20260901-145716_fixture_stability.json` vs.
`results/20260902-103821_fixture_stability.json`), single variable changed:

| fixture | field | Sep 1 | Sep 2 |
|---|---|---|---|
| item3 | `text_legible` | 7/7 True (wrong) | **0/7 True -- fixed** |
| item3 | `info_accurate` | 7/7 True (correct) | **2/7 True -- regressed** |
| item2 | `info_accurate` | 7/7 True (correct) | **4/7 True -- regressed** |

Everything else identical across both runs (item1 clean 7/7 on all three,
item4 `brand_consistent` 0/7, item5 `info_accurate` 0/7 -- all as
expected).

**Cross-check contamination is now confirmed, and this is the session's
headline finding.** The hypothesis was raised Aug 31 for `brand_consistent`,
tested, and dismissed as noise -- that dismissal remains correct on its own
evidence (`brand_consistent` never failed across 7 pinned runs, and still
doesn't). What is now falsified is the broader working assumption behind it:
that editing one check's wording cannot disturb another check. It can. The
three checks share one system prompt, and strengthening one instruction
shifts the balance against instructions near it. **Practical consequence:
any wording edit to any check requires a full 5-fixture regression run, not
a targeted single-fixture check.** `probe_fixture_stability.py` already does
exactly this -- the harness caught a two-fixture regression from a one-line
edit within minutes of the change, which is the process working as designed.

**item2's regression is the Sep 1 bug returning verbatim, not a new one.**
Notes on the failing runs: "Info accuracy fails because the visible title
asserts 'Seasonal Home Maintenance Checklist,' but the fact sheet does not
list this as a business service." The headline exemption added Sep 1 is
still present in the prompt, untouched -- it simply stopped being obeyed
3/7 of the time once `text_legible`'s clause grew longer and more emphatic
about scrutinizing every text element independently. The exemption wasn't
deleted; it was outvoted.

**item3's `info_accurate` failures split into three distinct causes**, only
one of which is the same bug as item2's:

1. **Illegibility contaminating info accuracy (runs 3, 6).** "because the
   image is too obscured to verify all text cleanly, I am marking info
   accuracy as false due to insufficiently clear visible assertions." The
   rubric has no way to express "not assessable," so *unverifiable*
   collapses into *inaccurate*. This is arguably caused by the legibility
   fix succeeding: now that the model correctly concludes the headline is
   illegible, it reaches for the only adjacent verdict the schema offers.
2. **Headline-as-assertion (run 4)** -- same failure as item2's.
3. **Boolean contradicting its own notes (runs 2, 5)** -- see below.

**Methodological finding, and the most consequential one here: the `notes`
field is not always a faithful account of the boolean it accompanies.** In
2 of 7 item3 runs the prose reasons explicitly to a pass -- "so no info
discrepancy is visible" and "so the info check passes for the visible
assertions" -- while `info_accurate` is emitted as `False`. Every root-cause
finding on this tool to date (the Aug 29 quantifier bug, the Sep 1 headline
misread) has depended on `notes` explaining why a boolean came out as it
did. Structured outputs guarantee the *shape* of the response, not that the
free-text and boolean fields were produced by the same line of reasoning.
Close-reading `notes` remains the best diagnostic available, but it is now
known to be unreliable at roughly a 2-in-7 rate on a contested field, and
conclusions drawn from a single run's notes should be treated accordingly.

**Process notes from this session:**

- **The unsaved-edit failure mode recurred, and was caught before a run
  this time.** The wording edit was reported as made but was not on disk
  (`git status` clean on the file, mtime a day old, and a repo-wide grep
  for the new terms found nothing). Checking disk state before running is
  now the standing pre-run step -- an invalid run against wording that
  isn't live already cost this project one suspect data point on Aug 31.
- **Recurring `.git/index.lock` files diagnosed.** Not a repo problem and
  not VS Code: they are created by Claude's own `git status` calls through
  the desktop bridge, which take the optional index lock and then cannot
  unlink it (the bridge shell is barred from deleting files in mounted
  folders). Confirmed by ownership (sandbox session user, not the Windows
  account), by timestamp matching the exact command, and by the "unable to
  unlink ... Operation not permitted" warning in that command's own output.
  Fix: use `git --no-optional-locks status` (or `GIT_OPTIONAL_LOCKS=0`) for
  read-only queries from that shell. Stale locks must be deleted from
  Windows.
- **End-of-session checklist added to `m7-orientation.md`**, after the
  `brand_consistent` Todoist task sat open a full day past the doc already
  recording it as resolved. Reconciling the Todoist punch list against what
  the session actually resolved is now a documented closing step rather
  than a thing to remember. That task is now closed.

**Next action (SUPERSEDED same day -- see the continuation entry below):** two changes to `info_accurate`, implemented **separately**
with a full `probe_fixture_stability.py` run between them, so the
contamination just demonstrated can't hide a second time. (1) **Isolation
clause** -- state that text which cannot be read is out of scope for
`info_accurate`, and that only legible, checkable assertions are evaluated.
This targets cause 1 above and is correct design independent of the bug:
each check should own its own failure mode, the same principle as the "or
vice versa" edit but applied *across* checks rather than within one.
(2) **Re-strengthen the headline exemption** to survive alongside the
longer `text_legible` clause, targeting item2's regression and item3's run
4. Do not combine them. Expected end state: all five fixtures back to 7/7
agreement with the `content-items-plan.md` table, with `text_legible`'s
fix intact.

**Held open as a documented decision point, not work to do now: whether the
three checks should be split into separate calls.** One prompt and one call
makes cross-check contamination structurally possible, and no amount of
wording care removes that -- it can only be detected. Splitting would
isolate the checks completely, at the cost of paying image tokens three
times per audit, three prompts to maintain, and a messier tool contract for
the orchestrator agent to call. It also would not fix the notes/boolean
contradiction, which is a different class of problem. Trigger condition for
revisiting: if the two fixes above do not return all five fixtures to
stable agreement, or if further wording edits keep causing regressions
elsewhere, the single-prompt design is fighting the work and the split
becomes justified on evidence rather than on principle.


**M7 session (Sep 2, continued): `info_accurate` fixed and both regressions
cleared -- but `text_legible` broke in the reverse direction on a clause
that was never touched. Prompt split decided.**

**The `info_accurate` edit took three drafting passes (Gerard drafting,
Claude critiquing), and the concept that finally landed is worth keeping.**
Pass 1 asserted independence ("Accuracy is not dependent on legibility and
vice versa") -- correct but inert, because it forbade a link without giving
the model anywhere else to go; the failing runs had reasoned "I can't
verify this, and I only have True or False, so False." Pass 2 added "When
accuracy cannot be determined due to legibility issues, note this
explicitly" -- Gerard caught the flaw himself: that instructs the `notes`
field, not the boolean, so the model could comply perfectly and still emit
`False`. Pass 3 landed it: **"When nothing legible contradicts the fact
sheet, record it as True."** The transferable principle -- **define the
passing condition by what is absent rather than what is confirmed** -- is
the reason it worked. "When the assertions do match" (an intermediate draft)
still required affirmative verification, which is exactly what illegibility
prevents; "nothing legible contradicts" lets unreadable text drop out of
the comparison instead of counting as a failed match. Deny-by-default vs.
allow-by-default, applied to a rubric.

**Result: both `info_accurate` regressions cleared completely.** item2 went
4/7 back to **7/7**, item3 went 2/7 back to **7/7**.

**But `text_legible` on item3 reverted to 7/7 True (wrong) -- and its clause
was never edited.** Verified byte-for-byte on disk against the wording that
produced 7/7 correct `False` that morning: identical. Same fixture, same
pinned `temperature=0`/`seed=42`. The original bug's reasoning came back
verbatim in the notes -- "the headline text 'Tool Rental 101: What We
Offer' is also readable **despite the low-contrast overlay**" -- the same
phrase from the pre-fix failure. Editing a different check's wording undid a
fix that was not touched.

| edit | target | result | collateral |
|---|---|---|---|
| `text_legible` (AM) | item3 legibility | fixed (0/7 True) | `info_accurate` broke: item2 4/7, item3 2/7 |
| `info_accurate` (PM) | those two regressions | both fixed (7/7, 7/7) | `text_legible` broke: item3 7/7 True |

14 of 15 cells correct both times, a different cell failing each time.

**A second wrong prediction, and the way it was wrong is itself evidence.**
Going into the PM run the stated expectation was that item2 would NOT fully
recover, since the edit didn't address the headline-exemption cause. It
recovered to 7/7 anyway -- the Sep 1 exemption started being obeyed again
without being touched, purely because the surrounding text changed. That
rules out "some individual sentence is wrong" and points at **salience
competition between instructions sharing one prompt** as the actual
mechanism. Contamination runs in both directions, helpful and harmful.

**DECISION (Sep 2): split the audit into two calls, accepting the added
cost.** The trigger condition written into this log and `m7-orientation.md`
that same morning -- "if further wording edits keep causing regressions
elsewhere, the single-prompt design is fighting the work and the split
becomes justified on evidence rather than on principle" -- was met, on a
criterion set before the data came in rather than after. What settles it is
the asymmetry: continuing to tune wording has **unbounded** cost with no
convergence guarantee, while the split has a **known, bounded** cost. And a
magic phrasing that passed all 15 cells tomorrow would still leave the
design fragile -- a new fixture, a model version bump, or a fourth check
would re-roll the dice. The tool's job is to be reliable for the
orchestrator, not to win at prompt golf.

**Two calls, not three -- the split follows the observed collision, not the
theoretical one.** Every contamination event across all three runs has been
between `text_legible` and `info_accurate`. `brand_consistent` was 7/7
correct on every fixture in every run (including item4's intended 0/7 fail)
and was never once implicated, even when it was the suspect on Aug 31. So:
`text_legible` gets its own call; `brand_consistent` + `info_accurate` stay
together. One extra image upload per audit instead of two, two prompts to
maintain instead of three. **Cost accepted deliberately** -- at this
project's size, awareness of the cost is sufficient; the reliability of the
tool the orchestrator depends on is worth more than the token delta.

**`notes`/boolean contradiction did not recur in this run** -- all seven
item3 notes matched their booleans. It appeared at 2-in-7 previously, so one
clean run is not proof it's gone. The backlog item stands.

**Next action: implement the two-call split, with both clauses' wording
frozen exactly as they are now.** Do not tune wording and split in the same
step -- the whole point of the split is to remove the variable that has
been confounding every measurement today, and changing both at once
reproduces the problem being solved. Each clause has already been proven
correct in *some* configuration; the split's first probe run is the test of
whether both can be correct *simultaneously*. Expected end state: all 15
cells matching `content-items-plan.md`'s table.

Implementation notes / open design question for that session:
`build_audit_messages()` becomes two builders (or one parameterized by
check group), and `audit_thumbnail()` makes two calls and merges the
results into a single `ThumbnailAudit` so the orchestrator's tool contract
doesn't change. **The real decision to make is what happens to `notes`:**
two calls produce two reasoning strings, and the current schema has one
`notes` field. Concatenate them, keep the schema and lose the per-call
attribution, or restructure `notes` into per-check keys and change the
tool's return shape? Worth deciding deliberately rather than defaulting --
`notes` is the diagnostic surface every root-cause finding on this tool has
depended on, and it's already known to be unreliable at ~2-in-7 on a
contested field.
