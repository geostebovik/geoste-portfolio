# IIP — Current Status

**This is a living document.** No date in the filename — it gets edited in
place each session, not re-copied. If you're looking for full historical
narrative (the "why" behind past decisions, session-by-session), that lives
in the frozen archive `MASTER-REFERENCE-0724.md` in the Drive IIP folder —
closed, not touched or re-read during normal sessions. This file is the only
thing that should need reading/updating at the start of a normal session.

**How this file is organized (restructured 2026-09-06).** Top to bottom:
the current next action, then the reference sections that change slowly
(milestones, live resources, key lessons), then the session log **newest
first**. Sessions from July 27 through August 7 — the completed M2–M6 build —
were split into `STATUS-archive-phase1.md` in this same folder.

**Two rules that keep it from decaying again.** (1) A session entry gets its
own `### Session — <date>` heading at the top of the log; it does not get
appended to `## Current next action`, which holds exactly one item — the
current one — and gets *replaced*, not extended. (2) Cross-references name a
date, never a direction: "the Aug 14 session notes", not "the notes above".
Direction words were already wrong in several places before this restructure,
because the file had drifted into three different orderings at once.

**Attribution -- read this before treating anything here as a work claim.**
This is a joint working log. The work it describes was done by Gerard and by
Claude (Anthropic's assistant), in proportions that varied task to task.
Where authorship is known it is named inline -- "Gerard drafted, Claude
critiqued", "Claude wrote the restructure at Gerard's request". **Where no
actor is named, that is not an authorship claim by either party.** Most of
this log is written in passive voice, and passive voice here means
*unrecorded*, not *Gerard's*. An audit on 2026-09-03 found 82 of 101
work-product passages in the Aug 28 - Sep 3 span carried no attributor at
all, including most of the analysis, the root-cause findings and the
architecture decisions. Those gaps are deliberately left unfilled:
reconstructing attribution after the fact is guesswork, and guessing in a
document that feeds a resume is worse than an honest silence.

**Going forward, attribution is written inline at the time the work is
logged, or not at all.** Where it is genuinely unclear, the entry credits
Claude rather than Gerard -- an under-credit costs nothing real, while an
over-credit in resume material can cost a great deal.

> **Restored 2026-09-10.** Everything from "which holds exactly one item"
> down to the end of the attribution rule above, plus the three pointers
> below and the `## Current next action` heading itself, was deleted by
> commit `aef3512` on 2026-09-08 — 37 lines, in a change whose purpose was
> only to replace the next-action content. Rule (1) was left cut off
> mid-sentence and the heading that marks the section boundary went with it,
> which is why nothing caught it for two days. Recovered verbatim from
> `git log -L 16,20:ai-103/STATUS.md`, not reconstructed from memory. The
> sentence destroyed was the one saying this section "gets *replaced*, not
> extended" — the replace operation ate the instruction describing itself.

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

**Status as of:** September 10, 2026. The certification pass has run: 120
orchestrator runs at `INSTRUCTIONS_V4`, drafter and judge both `gpt-5-4`,
zero crashes, 117/120 text rows and 117/120 audit rows matching their
pre-registered answer key. What it exposed is `brand_consistent` — a check
that has never been sound, only usually-agreeing.

---

## Current next action

**Next action: decide whether M7 is finished.** The certification pass ran
2026-09-10, the verdict layer held, and the one check it exposed was fixed and
re-verified the same day. Nothing below blocks a "M7 complete" call — they are
quality items, and the decision about whether they gate completion is Gerard's,
not something a green board should make by default.

1. **`brand_consistent`'s PERCEPTION, not its verdict.** The verdict is fixed
   and verified at 225/225. item3's `notes` still assert cream in an image that
   has none, on 15 of 15 runs. `notes` is what a human reads when deciding
   whether to trust a flag. A `notes`-instruction change, testable on one
   15-run 5-fixture pass: does item3 stop saying "cream"?
2. **Give `probe_fixture_stability.py` provenance before the next audit-side
   measurement.** It records no `git_head`, no `git_dirty`, no deployment and
   no copy of the live wording — `run_provenance()` already exists and takes
   `script=` / `include_agent=` for exactly this. Not during a measurement.
3. **Decide the orchestrator's model** — unchanged in substance, but the
   rate-limit dimension has dropped out of it (see the quota finding in the
   Sep 10 entry), so it reduces to output quality against cost per token.
4. **Raise the deployment quota and parallelise the probe loop** — Todoist
   `6hVCcxW6jWPmrMWq`. Neither is worth much without the other.

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
  notes. One deliberate, non-blocking scope item left open: the
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
  the Aug 5 run's apparent `gpt-5-4` edge, in the Aug 6 session notes
  (`STATUS-archive-phase1.md`).
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

## Key resources (current, live)

| Item | Value |
|---|---|
| Resource Group | `rg-iip-dev-wus-01` (West US) |
| Foundry account | `aif-dev-wus-01` (custom subdomain `aif-iip-dev-wus-01`) |
| Foundry project | `proj-iip-dev-wus-01` |
| Storage account | `stiipdevwus01` |
| Sample doc location | container `docs`, blob `loan-agreement-promissory-note.pdf` |
| Key Vault | `kv-iip-dev-wus-01` |
| Chat deployments | `gpt-5-2` (Content Understanding analyzer) · **`gpt-5-4-mini` — decided M5 RAG/Q&A model** (Aug 6: quality parity + ~3x cost advantage over `gpt-5-4`, full evidence in the Aug 6 session notes, `STATUS-archive-phase1.md`) · `gpt-5-4` — evaluated, not chosen, kept deployed in case a future comparison run wants it |
| Embedding deployment | `text-embedding-3-small` |
| Analyzer | `iip_loan_agreement_analyzer` (`ai-103/infrastructure/content-understanding/loan-agreement-analyzer.json`) |
| AI Search service | `srch-iip-dev-wus-01` (Free tier, West US) — `https://srch-iip-dev-wus-01.search.windows.net`, provisioned Aug 7 for M5 |

---

## Key Lessons

**This is a lookup, not a manual.** Azure/infra/git-specific gotchas live
here; general Python language patterns (control flow, data structures,
stray imports) live in `python-patterns.md` instead, so the two don't
overlap — same split `python-patterns.md`'s own header already describes.
Referenced from the Aug 7 and Aug 10 session notes as if it already
existed; it didn't. Created Aug 11 to close that gap.

### `FunctionTool` truncates every tool description at the first newline

Found 2026-09-07 by introspecting the schema `FunctionTool` actually generates,
after a new tool's description came back cut mid-sentence. It applies to the
function description **and to every `:param:` description**, and it is silent —
nothing errors, the tool still works, and the model simply receives a fragment.

Before the fix, this is what the model saw for two tools that had been treated
all along as carefully specified:

```
evaluate_draft
  description: "Evaluate a drafted video title and description for Riverside Hardware &"
  query:       "The drafting instruction the text was written to"
  response:    "The drafted text to evaluate, title and"
```

One description ends on an ampersand. The `query` guidance — "Do not pass a
bare topic: RelevanceEvaluator grades the response as an answer to this, and a
bare title scores as an unanswered question" — **never reached the model at
all**, which is why the agent improvised a different `query` per item on Sep 4
and Sep 7 rather than following it.

**The rule: the entire description must sit on one physical line, and so must
each `:param:` description**, however that reads in source. Prose below the
first line is for human readers only. Both tool modules now carry a note saying
so, so the next person to reformat them does not silently undo it.

**This qualifies the Sep 4 claim that "the reST docstrings functioned as tool
schemas on the first attempt."** They functioned in the weak sense: the model
received tool names and a truncated fragment, and got the calls right anyway.
That is a weaker result than it was recorded as.

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

## Session log

Newest first. Cross-references name the date of the entry they point at,
not a direction ("above"/"below") — those went stale the moment this file
was reordered, and several were already wrong before it was.

### Session — September 10, 2026

**The certification pass ran. 120 orchestrator runs, zero crashes, and the
pass/fail layer matched its pre-registered answer key on 117 of 120 text rows
and 117 of 120 audit rows — but the text deviations and the audit deviations are
different runs, so it is six deviations across 240 cells, and only one of the six
is a defect in the thing being certified.**

Results: `results/20260910-104818_orchestrator_stability.json` (smoke, 8x1) and
`results/20260910-123321_orchestrator_stability.json` (certification, 8x15). Both
at `git_head 87b37cd`, clean tree, `model_deployment` and `judge_deployment` both
`gpt-5-4`, `INSTRUCTIONS_V4`, temperature 0.

#### What was certified, and in what words

- **120 item-runs, zero crashes, zero `unmeasured`.** `unmeasured()` therefore
  STILL has no observation against a real crash — unchanged from Sep 8, still in
  the Backlog. Fifteen clean runs is not a test of the crash path.
- **Text verdict layer: 118/120 correct behaviour.** 117 matched the answer key
  outright; the two item6 "misses" are correct catches (below) and should not be
  counted against the checker.
- **Audit verdict layer: 117/120**, with all three failures in a single cell.
- All eight items clear the 0.8 agreement bar. Note the console's `agreement`
  figure for item7 reads 7% because it counts passes, not matches against the
  expected row — the `stable` flag handles the inversion correctly, the printed
  percentage does not. Backlog.
- **Scores stayed out of the claim, and Sep 10 supplied the instance that
  justifies it.** See item7 run 8.

#### item6's two "failures" are the pipeline working

item6's topic is "Propane Tank Refill: Sizes, Prices and Turnaround". The fact
sheet contains no sizes, no prices and no turnaround. On runs 11 and 15 the agent
drafted copy promising exactly those ("what sizes they handle, pricing, and how
turnaround works"), groundedness caught it at 2.0 with correct reasoning, the
agent redrafted, and the redraft passed at 4.0.

**The two metrics moved in opposite directions, which is the part worth keeping.**
On both failing drafts relevance was 4.0 — HIGHER than item6's usual 3.0 — while
groundedness fell to 2.0. A draft that promises the sizes is more responsive to
the topic and less grounded. The evaluators traded off correctly against each
other without being told to.

Two consequences:

- **stop-on-pass goes from n=2 to n=4.** Both runs fired clause 7's early exit.
  `probe_orchestrator_stability.py`'s docstring predicted this event would arrive
  through variance rather than fixture design, and it did — but it predicted the
  mechanism would be RELEVANCE, and it was groundedness. Same miss as the one
  recorded below, from the same source.
- **item6 is not the well-posed control it was re-registered as on Sep 9.** Its
  topic string names three facts the fact sheet lacks, so an ungrounded first
  draft is a legitimate outcome rather than a defect. Recorded, NOT fixed —
  moving the answer key to match the data is the goalpost move Thread 1 rejected.

#### The one genuine text defect: a score contradicting its own reason

**item7 run 8** scored relevance 3.0 and passed, against a pre-registered
`first_pass: False`. The judge's reason for that 3.0:

> "it does not focus on the requested price-match guarantee and return policy.
> Instead, it mostly lists unrelated store services and lacks grounding in those
> specific policy details."

Run 1, on the same item, scored 1.0:

> "It misses the requested topic and grounding, making it largely irrelevant to
> the user's specific ask."

**The same judgment in prose; 1.0 against 3.0 in the number, across the
threshold.** This is cause (c) from the Sep 2 audit analysis — the boolean
contradicting its own notes — reappearing on the TEXT judge rather than the CV
audit. It is also the concrete instance behind the Sep 9 decision to certify
verdicts and keep scores out of any claim: that decision was made on an argument,
and this is the observation it predicted.

#### `brand_consistent` on item3 — a cell closed as noise, reopened, and its passes are worse than its failures

item3's `brand_consistent` returned False on runs 9, 10 and 15 (expected True),
with `temperature=0`/`seed=42` pinned on the audit call. `text_legible` and
`info_accurate` on item3 were 15/15, so it is isolated to that one check.

**The fact sheet's rule is precise:** "Primary colors: orange (#FD5A1E-family) and
cream (#EFE4B0-family) — these are the only brand colors. Any thumbnail using a
materially different palette (e.g. blue/gray) as its dominant scheme is a
brand-consistency violation." The violating condition is a materially different
DOMINANT SCHEME. item4 is that (blue/gray). item3 is entirely orange. **By the
fact sheet's own rule item3 passes and the answer key is correct.** Gerard's call
2026-09-10, taken deliberately as option A against a stated option B.

**But the fixture does not contain what the passing runs say it contains.** item3
has ZERO cream — a solid orange field, orange-on-orange clutter, an orange title,
dark brown accents. The cream is absent because the legibility flaw requires it to
be: a cream panel would introduce exactly the high-contrast region the fixture
exists to avoid. item2, a CLEAN control, carries a large cream panel across
roughly 30% of the frame.

So the two populations split like this:

- **The 3 failing runs observed accurately and applied the wrong rule.** "mostly
  orange with little visible cream" is correct — there is none. But they required
  the PAIRING, which the fact sheet never does.
- **The 12 passing runs reached the right verdict on a confabulated
  observation:** "the thumbnail uses an orange/cream palette", "dominated by
  orange/cream tones". There is no cream in that image. They described item2 and
  graded item3.

**That is the finding.** The cell reads 12/15 correct, but the correct answers are
not coming from correct reasoning. `brand_consistent` has never been shown to be
SOUND — only to usually agree. A pass rate is not evidence of a working check when
the reasoning behind the passes is false.

**Root cause is the clause wording, and it is a standing lesson arriving again.**
`m7_cv_audit_tool.py`, the `brand_consistent` line of the content-call system
prompt: "is the dominant palette orange (#FD5A1E family) / cream (#EFE4B0 family)
-- flag anything materially different. Small color variations that do not impact
brand consistency are not an issue." Three problems: the slash is ambiguous
between OR and AND, and the failing runs read it as AND; it never states the
passing condition, only what to flag, then adds a second negative exemption; and
it drops the fact sheet's actual operative test. The model holds both the fact
sheet and this weaker restatement, and on 3 of 15 runs the restatement wins —
salience competition again, but between an INSTRUCTION AND ITS SOURCE rather than
between two instructions.

**A decisive internal check.** Run 15 objected that "the dark brown text/icon
accents are not part of the stated brand colors". item1 and item2 carry the same
dark wordmark and toolbox outline. Applied consistently that standard fails the
clean controls, which passed 15/15. So it is not a property of item3; it is a rule
being applied inconsistently because it is not pinned down.

**Probably not a regression.** Today is the first time this cell has run at n=15,
and through the orchestrator rather than `probe_fixture_stability.py`. At the
observed 20% rate, P(clean sweep of 7) = 0.8^7 ≈ 21%. Sep 1's evidence never
excluded this rate; it simply did not sample it. Same shape as the Sep 9 n=3
lesson, one size up. (An illustration of what the old evidence could not rule out,
not a significance claim.)

**Fixed and verified the same day, across four wording passes.** The clause now
states both branches: True when the dominant scheme is orange, cream or both in
any proportion; False only when materially different, blue/gray as the example;
neutral/dark accents out of scope. Gerard wrote every pass, Claude critiqued
each. The three discarded drafts are the useful part of the record: pass 1
required both colours present, which would have failed item3 against its own
answer key AND contradicted the blue/gray test two sentences earlier; pass 2
borrowed "contradict the fact sheet" from `info_accurate`, a relation that does
not apply to colours and that could have let item4 through by omission; pass 3
stated the True condition as a declarative assertion about the image rather than
as a verdict rule. **Every one of those would have looked like progress on a
green item3.**

Verified at `RUNS = 15` (raised from 7) across all five fixtures per the Sep 2
rule: `results/20260910-142656_fixture_stability.json`, **225/225 cells
correct** — 5 fixtures x 3 fields x 15 runs. item3 `brand_consistent` 15/15
True, item4 15/15 False, and no contamination: `item2 info_accurate` and
`item3 text_legible` both held at 15/15.

**AND THE REASONING WAS NOT FIXED — which is the finding, not a footnote.**
item3's `notes` still assert "the thumbnail uses an orange/cream palette" on
**15 runs out of 15**. There is no cream in that image. The confabulation did
not decrease when the verdict was corrected; it rose from most-of-12 to
all-of-15. The mechanism shows in item4, where the model writes "dominated by
blue and gray, which is materially different from the required orange/cream
brand palette" — separating the image's colours from the brand's palette
exactly right. On item3, where the image is on-brand, it collapses the two and
describes the thumbnail by reciting the brand guide. **When the answer is
"consistent", the model stops observing and starts quoting.** The verdict is
right because the rule is permissive enough that a mis-described image still
lands correctly, not because the check sees what it claims to see. This is a
`notes`-instruction problem, needs a different fix, and is testable on one
15-run pass. Backlogged deliberately rather than attempted at 14:35.

**One further consequence, Gerard's observation:** "Record as False ONLY when"
is what makes the rule total, and totality is what killed the variance — but it
also scopes `brand_consistent` to the colour scheme alone. `fact-sheet.md`'s
brand guide also names a logo, so a correct palette with a wrong logo is now
forced to True. Accepted deliberately: no fixture isolates a non-palette brand
violation, so broadening the clause would be a change no run could verify. The
response to an untested gap is a fixture, not a wording change.

#### The pre-registered prediction was falsified, cleanly

Before the run, on the strength of the 8x1 smoke, Claude predicted that item3,
item5 and item6 — all three sitting at draft-1 relevance exactly 3.0 against a
threshold of 3 — were where first-draft failures would appear if the judge's ±1
spread had survived the swap to `gpt-5-4`.

**Relevance never went below 3.0 on any pass-item in 120 draws. The predicted
mechanism did not occur once.** item3, flagged as most exposed, returned 4.0 on
all 15 runs; its smoke-run 3.0 was a single draw read as a property. The failures
came from groundedness (item6) and from relevance crossing UP from below (item7
run 8).

`m7-orientation.md`'s own lesson covers it: "Do not infer a gradient from a single
point sitting on a threshold... The right reading of a value sitting exactly on a
bar is 'this may be where the function lands', not 'one more nudge will tip it'."
Claude read that the same morning and then built a prediction on three single
points sitting on a bar.

**The pre-registration still earned its keep.** Because the prediction was written
down before the run, the miss is legible instead of being quietly reabsorbed into
a post-hoc story about item6 — which is what would have been written, and it would
have sounded right.

#### Instrument change: the judge is now recorded in every orchestrator run

`run_provenance()` recorded which model DREW each draft and never which one GRADED
it. `probe_judge_isolation.py` had been setting `judge_deployment` on its own
provenance by hand, so judge-only probes were self-describing while the
orchestrator runs a certification claim rests on were not. Fixed: one import line
and one field, recorded outside the `include_agent` block because a judge grades
every run whether or not an agent drafted it. Claude wrote the patch; Gerard
reviewed, committed and ran everything. Commit `87b37cd`.

Consequence for the record: `results/20260909-122233_orchestrator_stability.json`
(item6 29/30, item7 26/30) carries NO judge field and is timestamped 11:27, before
the judge decision was taken that afternoon. Those two figures were measured on
`gpt-5-2` and are not `gpt-5-4` numbers. They remain valid evidence that the
verdict layer does not move with the judge; they are not the certification result.

#### The judge question is closed on documentation as well as measurement

`gpt-5-4` is **Generally Available** — Foundry model details page, Quick facts:
Lifecycle "Generally Available", version 2026-03-05, publisher OpenAI, Direct from
Azure. Microsoft's documented caveat — "For the best performance and parseable
responses with our evaluators, we recommend using GPT models that aren't in
preview" — is therefore satisfied by the current judge rather than violated by it.
That was the last remaining argument for moving the judge off `gpt-5-4`.

Also verified, and a non-finding recorded so nobody re-derives it: the docs require
`is_reasoning_model=True` when a reasoning model judges Groundedness or Relevance.
`m7_evaluator_tool.py` already sets it on both evaluators.

A same-family judge swap (gpt-5.5 / gpt-5.6, both available in the project) was
considered and rejected — it addresses the weaker half of the self-grading concern
while leaving family-correlated blind spots untouched, and `all_passed` was already
identical across three deployments in 60 calls. The cross-vendor INDEPENDENT CHECK
remains the live idea, and its feasibility is now confirmed: DeepSeek-V4-Pro,
Kimi-K2.5/K2.6/K2.7-Code and Cohere-command-a-plus-05-2026 all expose Chat
completion in this project. Full reasoning in Todoist `6hV42V2cq7cJMcwH`.

#### The 30K TPM ceiling is self-imposed — and it is not the bottleneck

Found while checking whether `gpt-5-4` was GA. Foundry > Manage > Quota, gpt-5-4:
Deployment quota 30K TPM, Total shared quota 1M TPM, Remaining 970K TPM. The Edit
dialog confirms a 30K–1000K range and carries Microsoft's own hint, "Set quota high
enough to prevent throttling." The 30K figure this project has designed around is
an allocation set on Sep 7 to fix a real asymmetry (mini at 3 RPM against
gpt-5-4's 30); nobody then asked whether 30K was the right absolute number.

On Global Standard, TPM allocation is a rate ceiling, not a spend commitment —
billing is per token consumed, so raising it costs nothing per token. PTU is the
opposite arrangement; this project is not on PTU.

**And a correction made the same day, before anything was acted on.** Claude first
described the 95-minute run as throughput-bound and implied a quota raise would
make it dramatically faster. The arithmetic says otherwise: the smoke run measured
8 items in 6m19s = 47s per item-run, and at ~16K tokens per item that is ~20K TPM
sustained, UNDER the ceiling. The run is serially latency-bound — 120 item-runs
executed one after another, each waiting on multiple round trips. **The quota raise
is the precondition for parallelism, not a speedup on its own.** Running the eight
items concurrently would draw ~160K TPM, which is where 30K actually binds.
Parallelising across items is safe by construction: `m7_orchestrator.py` already
runs every item on its own thread. Todoist `6hVCcxW6jWPmrMWq`.

The error is worth naming because it is the same shape as the find that produced
it: "30K TPM" was questioned as a SETTING and still accepted as a BOTTLENECK. Two
assumptions riding on one number; only one was tested.

#### This file's own preamble had been silently truncated for two days

`grep "^## Current next action"` returned nothing at session start, which is how it
was found. Commit `aef3512` (2026-09-08, "Docs: Sep 8 - redraft branch observed")
deleted 37 lines of standing preamble — hunk header `@@ -16,70 +16,33 @@` — in a
change whose only purpose was to replace the next-action content. It began the
replacement INSIDE the preamble, cut rule (1) off mid-sentence at "appended to
`## Current next action", and took with it:

- rule (1)'s tail, defining that the section holds one item and is *replaced*;
- rule (2) entirely (cross-references name a date, never a direction);
- **the whole Attribution block** — including "Where no actor is named, that is not
  an authorship claim by either party", the 2026-09-03 audit finding that 82 of 101
  work-product passages carried no attributor, the decision to leave those gaps
  unfilled rather than guess, and the going-forward rule that unclear authorship
  credits Claude rather than Gerard;
- the pointers to `iip-cli-runbook.md` and `m7-orientation.md`, the deferred-pages
  note, the "Status as of" line, and the `## Current next action` HEADING itself.

**The attribution policy governing a resume-material document was absent for two
days, and the Sep 9 and Sep 10 sessions were both logged without it visible in the
file.** Restored 2026-09-10, verbatim from `git log -L 16,20:ai-103/STATUS.md` —
recovered from the source, not reconstructed from memory, per the Sep 3 lesson
about citing a document's contents.

The mechanism is worth keeping: the heading is what marks the boundary of the
region a session is allowed to replace. Deleting the heading removed the marker
that would have made the over-reach visible, so the next two sessions edited around
a boundary that no longer existed. And the specific sentence destroyed was the one
saying the section "gets *replaced*, not extended" — the replace operation ate the
instruction describing itself.

#### Environment: the desktop shell was unavailable all day

Second consecutive day. `device_list_dir` / `device_stage_files` /
`device_commit_files` worked throughout; the desktop shell could not mount either
folder (`no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared`). New
information against Sep 9: `echo hi` fails identically, so the failure is
PRE-EXECUTION — the helper refuses to start any shell because the shares are
absent, and the guest VM is up enough to report it. So the fault is in the
host-to-VM folder-sharing layer, not the shell.

Leading untested hypothesis: the two connected folders are nested
(`geoste-portfolio` and `geoste-portfolio\ai-103`, the second inside the first),
and the error names both as failing, which is what publishing zero shares rather
than one would look like if the share set were rejected as a whole. **Test
pre-registered for the next session: attach ONLY the repo root and try the shell.**
The root already contains `ai-103`, so the second share buys nothing but a shorter
path. If it still fails with a single folder, nesting is ruled out and the next
suspect is the desktop build (1.49585.0 / Electron 44.2.0).

Reading the app's own logs is NOT available: `C:\Users\gerar\AppData\Roaming\Claude`
is a protected location and cannot be granted. Do not spend a permission prompt on
it again.

Practical consequence, unchanged from Sep 9: Claude reads and writes files but runs
nothing, including git. Gerard ran every command today. This costs Claude grep and
git; it does not block measurement, since the Azure scripts have always run in
Gerard's own PowerShell where `.env`, the CLI login and the Python environment live.

#### Authorship

Gerard ran every command, made every decision, owns the certification framing, and
made the option-A call on the brand rule and the clause rewrite. Claude wrote the
`run_provenance()` patch, did the results analysis and the item3 root-cause
investigation, recovered the deleted preamble from git, made the pre-registered
prediction that was falsified, and made the throughput error corrected above.

### Session — September 9, 2026

**Both Sep 8 blockers cleared. `INSTRUCTIONS_V4` fixed the meta-commentary
defect, and the judge-isolation probe answered the redraft question by
inverting it. A third finding arrived unlooked-for and is the one with the
longest reach.**

**Finding 1 -- the redraft loop re-rolls. A fixed failing draft passes 7 times
out of 10, unchanged.** `probe_judge_isolation.py` (new, Claude wrote it; Gerard
chose the paired design from the options offered) called `evaluate_draft()`
directly on run 15's recorded drafts, 10 re-reads each, no agent in the loop, so
every point of spread is judge-side by construction.

| | relevance | passed |
|---|---|---|
| draft 1 (recorded FAILING) | 3.0 x7, 2.0 x3 | **7/10** |
| draft 2 (recorded passing) | 3.0 x10 | 10/10 |
| groundedness, both drafts | 4.0 x20 | zero variance |

Run 15's recorded failure was a MINORITY draw -- draft 1's modal relevance is
3.0, a pass. Redrafting and re-scoring at 3.0 is what re-reading the original
would have done 70% of the time, so that stop-on-pass observation says nothing
about whether the edit helped. **Consequence, and it inverts the cap decision:**
at a 70% per-read pass rate, one read passes 70% of the time, a cap of 1 gives
91%, a cap of 2 gives **97.3%**. Raising the cap raises the false-pass rate.
**Wider consequence:** a certification pass reporting `final_text_passed` would
measure the cap, not the system -- Sep 8's `final passed 21/21` is exactly what a
70% item with three rolls produces, and was never evidence of quality.
`first_text_passed` is the headline number; the probe already records it
separately.
**Not settled, and n cannot settle it here:** draft 2's 10/10 against draft 1's
7/10 is Fisher p=0.21. The redraft may have improved the text. Deliberately not
chased -- V4 was about to change redraft behavior, so measuring the old
behavior's quality was measuring something already being replaced.

**Finding 2 -- the meta-commentary defect is fixed, and the first-draft channel
was worse than anyone had checked.** `check_meta_commentary.py` (new, Claude
wrote it; Gerard approved building it) turns "3 of 3 redrafts, read by eye" into
a measured field over any results file. Run retroactively over both Sep 8 files
it found 5/5 redrafts as expected -- and **2 of 21 FIRST drafts**, item6 runs 6
and 19, which nobody had looked at. Both PASSED with zero redrafts and would have
shipped. That is worse than the redraft case, where item7 at least ended FLAGGED.
**It also decided where the V4 fix belongs**: a clause-7-only fix would have left
those two uncaught while appearing to work.

`INSTRUCTIONS_V4` (Gerard's wording, both clauses; Claude specified what each had
to accomplish and rejected the first clause-7 draft for missing the legal move --
see `m7-instructions-draft.md`). Measured over 30 runs of item6 and item7, 113
drafts:

| | V3 baseline | V4 | Fisher two-sided |
|---|---|---|---|
| redrafts referencing the fact sheet | 5/5 | **0/53** | p = 2.2e-07 |
| first drafts referencing the fact sheet | 2/21 | **0/60** | p = 0.065 |

The redraft channel is settled. **The first-draft channel is suggestive, not
significant** -- Claude predicted p≈0.0025 before the run by treating the 9.5%
baseline as known; the honest test against the actual 2-of-21 gives 0.065, an
error of an order of magnitude in the flattering direction. Reaching p<0.05 needs
about 50 runs; deliberately not spent, on the grounds that the redraft result is
decisive and moving one secondary p-value across an arbitrary line is the
analysis-over-building drift this project already logs as a standing risk.

**The pre-registered risk did not fire.** V4's "allow the check to fail" sits
before "call evaluate_draft on each new draft", so it could have been read as
permission to stop after draft 1. Predicted in the file BEFORE the run that it
would not happen: item7 recorded `redrafts=2` on 26 of 30 runs, and the four
zeros are runs whose first draft passed.

**Stop-on-pass observed a second time** -- item6 run 30, and this time the dip
was GROUNDEDNESS (2.0) rather than relevance. n=2 for clause 7's early exit.

**Finding 3 -- `GroundednessEvaluator` contradicts itself on identical evidence,
and this corrects Sep 8's Finding 1.** item7's groundedness ranged **1.0 to 4.0**
across 30 runs, mean 2.667. Claude's first hypothesis -- that dropping the topic
from the title collapses the score -- was **falsified by the data**: four drafts
dropped the topic and still scored 4.0.

The controlled pair is runs 1 and 6. Near-identical drafts: same title verbatim,
same five services, same phone number, differing only in cosmetic phrasing. The
judge's two reason texts make the SAME four observations -- the fact sheet has no
policy content; the response lists services instead; those service claims ARE
grounded; the response fails to address the topic. Then:

> **1.0:** "...they are not relevant to the requested topic, so the response
> fails to answer the question as asked."
>
> **4.0:** "...only partially addressing the prompt while remaining mostly
> accurate to the fact sheet where it does make claims."

**So groundedness inconsistently imports relevance into its own score** --
sometimes grading support-given-claims (its documented job, 4.0), sometimes
letting off-topic-ness dominate and collapsing to the floor. Sep 8's Finding 1
("groundedness does not measure responsiveness, so `all_passed` is
relevance-gated") was drawn from five observations, all 4.0-5.0, and is **wrong
as stated**. Corrected in `m7-orientation.md`'s Backlog.

**V4 is not the cause.** Under V4, P(groundedness=4.0) on item7 is 13/30 = 0.43;
three consecutive 4.0 draws has probability 0.081. Sep 8's n=3 is not
distinguishable from today's distribution -- the spread was always there and
nobody had the runs to see it.

**What it does and does not block.** The VERDICT layer is unaffected: item7
matched its pre-registered `first=False final=False redrafts=2` on 26 of 30 runs.
Certification of pass/fail is not blocked. Any claim about SCORES is, until the
judge deployment is decided -- which is why that moved to the top of the next
action.

**Two instrument notes. (a) was chased the same afternoon and turned out not to
be cosmetic.** item6's `expected_text` encoded `first_pass: False` -- a ~9.5%
event -- as the expected value, so `text_matches_expected` read False on 29 of 30
runs for a system working correctly. Filed as a display wart; it was actually a
small answer-key decision, because item6 was *designed* as the recoverable-failure
fixture and that design is what the step function retired. **Re-registered as a
well-posed control** in both `ITEMS` and `content-items-plan.md` -- Gerard's call,
and it is branch 2 of item6's own pre-registered branches firing, which said in
advance that this might be the honest conclusion. Full reasoning in the answer
key; what is lost is stated there too (no fixture now exercises fail-then-recover
by design). (b) item6's relevance was 3.0 x30 with zero variance under V4 against
2/21 dips under V3; that is **not** significant (p=0.16) and must not be read as
V4 having stabilised anything.

**Two process failures worth keeping, both Claude's.**
- **The instrument overstated its own verdict.** `probe_judge_isolation.py`'s
  first `compare()` tested only whether the two drafts' score RANGES intersect
  and printed "retry-until-lucky" when they did. On this data it called OVERLAP
  on [2.0, 3.0] against [3.0, 3.0] -- ranges touching at a single point while
  describing 7/10 against 10/10. Rewritten to answer the two questions
  separately, with Fisher's exact test on the pass RATES (a binary outcome, not
  the ordinal scale) and "CANNOT TELL" as a first-class output. **The stale
  verdict string is still inside `results/20260909-101238_judge_isolation.json`;
  its numbers are correct and its `comparison` block is superseded.**
- **`INSTRUCTIONS_V3` was edited in place** (Gerard applied the new clauses to
  V3 rather than to a new version, and `ACTIVE_INSTRUCTIONS_LABEL` still read
  V3). Caught by an mtime check before any commit. Left alone it would have
  relabelled every Sep 7 and Sep 8 result -- the two 15/15 runs, the 21-run
  probe, all four findings -- as measured against wording that did not exist when
  they ran, and the next run would have recorded `instructions_label: V3` while
  executing V4. V3 restored byte-for-byte; V4 is built by `.replace()` against it
  with three asserts that fail at import if either substitution stops matching,
  so the diff is provably the two clauses and nothing else.

**Tooling.** The device shell could not mount the connected folders all session
(`no Plan9 drive shares mounted`), so every command was Gerard's in PowerShell.
Azure MCP and the newly-activated Microsoft Learn connector both worked, and MS
Learn is what turned the judge-model backlog entry from a tidiness note into a
documented dependency. Registry search found no GitHub connector; the dangling-
commit question needs `git fetch origin <a real pre-purge SHA>` and those SHAs
are no longer in the local clone.

**AFTERNOON — the judge, settled. Finding 3 above is wrong as written, and the
correction is the interesting part.**

**What Finding 3 said this morning:** groundedness inconsistently imports
relevance into its own score, stated as a property of `GroundednessEvaluator` on
30 observations. **All 30 were on one judge deployment.** Ten calls each on two
others, same two fixed drafts:

| judge | item7 groundedness | item7 relevance | item6 (both metrics) |
|---|---|---|---|
| gpt-5-2 | 1.0 ×8, 4.0 ×2 | 1.0 ×10 | 4.0 / 3.0, ×10, exact |
| gpt-5-4-mini | 2.0 ×8, 4.0 ×2 | 2.0 ×9, 1.0 ×1 | 4.0 / 3.0, ×10, exact |
| **gpt-5-4** | **4.0 ×10** | 2.0 ×9, 1.0 ×1 | 4.0 / 3.0, ×10, exact |

**item6 is the control and it is decisive:** all three judges agree exactly on a
well-posed draft, so the judge is not generally noisy. Microsoft documents
groundedness as measuring whether claims are SUPPORTED, not whether the response
ANSWERS — gpt-5-4 applies that on every call; gpt-5-2 usually lets off-topic-ness
dominate. **So Sep 8's original claim describes the metric's real contract, and
this morning's correction attributed one model's failure to implement it to the
SDK.** Corrected in `m7-orientation.md` rather than deleted; the sequence is the
lesson, and a standing lesson was added for it.

**Claude predicted all three judges would spread on item7. gpt-5-4 did not spread
at all.** Recorded because the prediction was made in writing beforehand.

**The verdict layer is judge-invariant. This is the certification result.**
`all_passed` was 0/10 on item7 and 10/10 on item6 for every judge — **zero
crossings in 60 calls.** Everything certified on pass/fail stands regardless of
judge. The decision to certify verdicts and not scores was made this morning on
reasoning; it is now evidenced.

**Judge changed to gpt-5-4, and the self-grading objection is answered with data.**
gpt-5-4 is also the orchestrator's drafting model, so judge and drafter now share
a deployment. The same six runs answer the obvious objection: two of the three
judges are not the drafter, and all three produced identical verdicts. The
coupling is documented in `judge_deployment()`; it is not buying the drafter a
favorable outcome.

**Two mechanisms ruled out, cheaply, before the swap.**
- **`reasoning_effort` is unreachable through the Evaluation SDK.** Accepted by
  `**kwargs` and retained nowhere on the instance, while `is_reasoning_model=True`
  lands visibly as `_is_reasoning_model` — so "accepted" was checked against a
  known-honored parameter rather than assumed. `AzureOpenAIModelConfiguration`
  accepts six fields and none is it.
- **No deployment spends hidden reasoning tokens when it grades.**
  `completion_tokens` matches the visible reason text within a rounding error on
  all three: 197 against 891 chars, 127 against 568, 202 against 998 — 4.5 to 4.9
  chars per token, ordinary English prose with no room for hidden deliberation.
  `prompt_tokens` was 2035 on all three, confirming the same prompt reached each.

**A hypothesis of Claude's was falsified along the way**, recorded so it is not
re-proposed: Microsoft's reasoning-models page lists `temperature`, `top_p` and
`seed`-adjacent parameters as unsupported on reasoning models, which suggested the
CV audit's Sep 1 `temperature=0`/`seed=42` pinning and `AGENT_TEMPERATURE=0.0` had
always been inert. **All three deployments ACCEPT both parameters.** Nothing on
record needed correcting. Caveat kept: accepted is not the same as honored, and
`probe_reasoning_params.py` cannot tell those apart.

**New instruments, both committed:** `probe_reasoning_params.py` (what each
deployment accepts, and its reasoning-token ladder) and `probe_judge_internals.py`
(what the Evaluation SDK exposes, plus one raw evaluator call read before
`_flatten()` drops `_properties`). `probe_judge_isolation.py` and
`m7_evaluator_tool.py` gained `--judge-deployment` / `JUDGE_DEPLOYMENT`; the probes
set it before importing the evaluator, because the judge config is built at module
scope and a flag applied after that import would be silently ignored.

**Tooling note.** The Microsoft Learn connector was activated this session and did
real work: it supplied the groundedness scale definition, the reasoning-model
parameter table, and the judge-model guidance that turned the inherited-judge
backlog entry into a decision. Registry search found no GitHub connector.

### Session — September 8, 2026

**Two orchestrator runs. The redraft branch executed for the first time, and
the reason it took two attempts is the finding.**

**Run 1 (`20260908-115858`) — both text-path fixtures passed on the first
draft, falsifying the design premise behind them.** items 6 and 7 v1 (tool
rental pricing; the crew topic) were built on the claim that a topic the fact
sheet cannot support must fail groundedness. Measured: item6 groundedness 4.0 /
relevance 3.0; item7 4.0/4.0. Zero redrafts on both.

**Run 2 (`20260908-133724`) — 15/15 matrix, no unmeasured items, clean
provenance, and item7 v2 fired the cap.** Three `evaluate_draft` calls,
`redrafts` = 2, third draft kept per clause 7, final line
`FLAGGED FOR REVIEW: text check`. The two-redraft cap and the keep-and-report
clause are now **observed**.

**Finding 1 — groundedness does not measure responsiveness.** Five
observations across the two runs, all one direction. All three item7 drafts
scored groundedness **4.0, passed** while relevance scored **2.0, failed** —
and the groundedness reason says outright that the draft does not answer:
*"it fails to address the requested topic ... Therefore, it is only partially
responsive"*, scored 4.0. item8 (the v1 crew topic carried forward unchanged as
a reproduction control) reproduced at groundedness **5.0**. So
`GroundednessEvaluator` measures *is what you said supported*, not *did you
answer*; `RelevanceEvaluator` is the only check in the pair that sees
responsiveness. **Consequence: for any topic the fact sheet does not cover,
`all_passed` is effectively relevance-gated — groundedness cannot fail a draft
that pads with true statements.** Score stability caveat: item8 moved 4.0 → 5.0
between runs on an identical topic, so the direction reproduces and the number
is worth about ±1.

**Finding 2 — the relevance step function, and why the recoverable fixture may
not exist.** v1 item6 (tool rental pricing) scored relevance **3.0**. v2 item6
(propane refill, three specific dimensions demanded against four words in the
fact sheet) also scored **3.0** — the harder topic did not move it at all.
Against item7's 2.0, where the spine itself is absent, the pattern is a step,
not a slope: **spine supported → 3.0 → passes regardless of how much
specificity the topic demands; spine absent → 2.0 → fails, with nothing to
substitute, so it cannot recover.** If that holds, the condition producing a
first-draft failure is the same condition preventing recovery, and a
recoverable-failure fixture is structurally impossible in this design. Claude
had inferred a gradient from a single point sitting on the threshold; two runs
say otherwise. Standing lesson added below.

**Finding 3 — the agent wrote its own scaffolding into the copy, and nothing
caught it.** With no supported material to substitute, item7's redrafts
substituted meta-commentary instead. Draft 2: *"Because the fact sheet only
confirms the store's core services, this video stays focused on..."* Draft 3:
*"a practical overview of Riverside Hardware & Supply as presented in the store
fact sheet"* and *"questions about store policies not listed there"*. That is
customer-facing marketing copy discussing an internal grounding document.
Groundedness passed it three times, relevance marked it down for being
off-topic rather than for this, and no `INSTRUCTIONS_V3` clause forbids it.
This is the "replace unsupported claims with supported ones" clause degenerating
when nothing valid fits.

**Two instrument defects found and fixed, both surfaced by run 1.**

- **A crashed item was scored as wrong verdicts.** item1 died on an Azure
  `server_error` between `evaluate_draft` and `audit_thumbnail`; its three cells
  had no verdict and counted as three failures, reading 12/15 —
  indistinguishable from a regression in a tool that was correct on every
  fixture it reached. In a seven-run certification pass one transient error
  would have read as instability. `cells_correct()` now excludes unmeasured
  items and `unmeasured()` reports them with the error and the tools that ran.
  Unit-tested against a synthetic crash; **never exercised against a real one**,
  since run 2 completed cleanly.
- **`run_provenance()` reported a false dirty tree.** It used
  `git status --porcelain`, which reports stat rather than content, while
  `_git()` hard-codes `--no-optional-locks` so a refreshed index is never
  persisted. Now measured by content (`git diff --name-only HEAD` plus
  untracked). Run 2 recorded `dirty=False` correctly.

**Run 3 (`20260908-143613`) -- the first orchestrator stability probe, item6 x21.
`stop-on-pass` fired.** `probe_orchestrator_stability.py` was written and run the
same afternoon; its `main()` worked on the first attempt. 21/21 measured, no
crashes, `git_dirty` False.

| measure | result |
|---|---|
| first-draft relevance | **3.0 x19, 2.0 x2** (runs 13 and 15) |
| first-draft groundedness | 4.0 x21 -- zero variance |
| redrafts | run 13: 2 (passed on draft 3); run 15: 1 (passed on draft 2) |
| final passed | 21/21 |

**Only run 15 is a clean observation.** Draft 1 failed at relevance 2.0, one
redraft, draft 2 passed, and the agent stopped -- two `evaluate_draft` calls
where three were allowed. That is clause 7's early exit, unambiguously. **Run 13
does not count as a second**: it passed on draft 3, the cap boundary, where
stop-on-pass and "keep the third draft" both produce the same behavior, so the
stop is not attributable to the early-exit clause. **n=1.**

**21 runs was Gerard's call and the numbers justify it.** The dip rate is 2/21 =
9.5%; at 7 runs the expected count is 0.67, so the likeliest outcome would have
been zero hits and a wrong conclusion that the variance route was shut. A 0/7
null would also have bounded the true rate only at ~43% (rule of three) --
worthless. Claude proposed 7.

**The prediction's outcome held; its stated mechanism did not.** Claude
predicted the dip would come from JUDGE-side variance, reasoning that
`AGENT_TEMPERATURE=0` pins the drafting. It does not: **19 distinct first drafts
across 21 runs.** With no `seed` parameter in the Agents SDK, temperature=0
narrows but does not repeat. So what is demonstrated is *pipeline* variance, and
judge variance cannot be separated from draft variance in this data. Both
failing runs happen to share a draft-opener variant ("Need to know whether..."
rather than "Need to know what to..."), but run 8 used that opener and scored
3.0. A cheap probe settles it -- call `evaluate_draft()` directly on run 15's
exact failing draft ~10 times with no agent in the loop, ~39K tokens.

**Finding 4 -- the redraft may not have earned the pass, and this is the one
that bears on certification.** Run 15's judge reasons, draft 1 versus draft 2:

> **2.0:** "does not address the requested topic details -- propane tank sizes,
> prices, or turnaround times... It also adds unrelated services"
>
> **3.0:** "does not include the key requested specifics -- sizes, prices, and
> turnaround times... It's on-topic but incomplete and somewhat generic."

The primary criticism is unchanged. The redraft did make one real change the
judge asked for -- it dropped the unrelated services -- so this is not pure
noise. But the dominant complaint was never fixable, and **the observed variance
on this cell (2.0 <-> 3.0) is exactly the size of the movement**, so the recovery
cannot be attributed to the edit from one observation. On this fixture the
redraft loop may be functioning as **retry-until-lucky** rather than
remediation. If so, a higher cap means more dice rolls and a higher false-pass
rate -- which means the cap's correct value depends on a prior question the
multi-run pass was assumed to answer directly.

**Finding 3 escalates: the meta-commentary defect is 3 for 3 on redrafts.** All
three redrafts across runs 13 and 15 inserted it -- "focuses on what the fact
sheet confirms", "sticks to the details confirmed in the fact sheet", "sticks to
the details confirmed in the store fact sheet". It is **not** confined to
item7's unrecoverable topic; it is what the agent does whenever it redrafts. Any
certification that includes a redraft path certifies this behavior.

**Process note worth keeping.** The morning's plan was to harden item6's topic
pre-emptively, on conjecture, before any run. Gerard stopped it: with no
baseline there would be no way to attribute the change. Running the v1 fixtures
as designed is what produced the 3.0-on-threshold measurement, the groundedness
property, and the step-function finding — none of which would exist if the
fixtures had been "improved" first. **Two of the three branches pre-registered
for item6 called for opposite corrections, so hardening early was a coin flip on
the sign of the error.**

### Session — September 7, 2026

**M7's last piece of design work is built.** `INSTRUCTIONS_V3` is written,
wired and passing 15/15 on two consecutive runs, with 5/5 items passing the
text check. It took three versions to get there, and the second one regressed
— that arc is the substance of the day and is recorded below rather than
smoothed over. Claude drafted the instructions text; Gerard set the scope,
made every decision flagged as his, and wrote the redraft clause's operative
fix. Claude wrote all the code described here.

**Both folders were unconnected at session start — the third recorded
instance.** Gerard had attached them before opening the thread; `get_device_info`
returned `connectedFolders: []` regardless. Session-start checklist item 1
caught it in one call. **Folder attachment has now failed to survive into a
session on Sep 3, Sep 4 and Sep 7; treat it as the expected state, not an
anomaly.**

**Run persistence added to `m7_orchestrator.py` — the day's enabling change.**
Before it the script only printed, so the Sep 4 15/15 existed solely as console
output quoted into this file: not re-readable, not diffable, and not usable as
the artifact behind the certification pass still owed. Every run now writes
`results/{timestamp}_orchestrator.json` carrying git HEAD, **whether the tree
was dirty**, the model deployment, the instructions text verbatim, every tool
call's arguments *and returned payload*, every message on the thread, token
usage, and the rubric comparison parsed from `audit_thumbnail`'s JSON rather
than the agent's prose. Claude proposed the design and Gerard approved it
before any code was written.

**SDK finding that shaped it: `run_steps` does not carry function tool
outputs.** `RunStepFunctionToolCallDetails` (azure-ai-agents 1.1.0, verified by
introspection, not recalled) has exactly `name` and `arguments` — no output —
although `RunStepFunctionToolCall`'s own docstring claims it "represents the
inputs and output consumed and emitted by the specified function".
Code-interpreter and file-search calls do carry outputs; function calls do not,
because `enable_auto_function_calls` submits them on the caller's behalf and
the service never echoes them back. **The obvious implementation would have
recorded what the agent sent in and nothing about what came back, and would
have looked like it worked.** So both tools are registered through
`functools.wraps` logging shims, and `build_toolset()` builds the definitions
both ways and refuses to run if wrapping moved the schema — tested in a scratch
container first, and byte-identical.

**Result files are now curated rather than wholly ignored.** `STATUS.md` and
`m7-orientation.md` cite result files as evidence — the
`20260901-145716` vs `20260902-103821` baseline diff behind the contamination
finding, among others — and **none of them were in the repo**;
`ai-103/scripts/results/` was gitignored outright. On a repo that is resume
material, a cited file that is not in it is a citation to nothing. `.gitignore`
now uses `results/*` plus one explicit negation per file, so tracking a result
is a deliberate act rather than a side effect of a pattern. Six cited files
plus the day's orchestrator runs are tracked; everything else stays ignored.
Verified with `git check-ignore` rather than by eye. Also added `*.json text
eol=lf` to `.gitattributes` after the first six committed files immediately
reappeared as modified — line endings only, the CRLF lesson in a new file type.

**V1 reproduced 15/15 under the new harness**, same commit, same instructions,
same model — so the persistence change moved nothing.

**The forced text-failure probe was cancelled: item5 failed on its own.**
`evaluate_draft` returned groundedness 2.0, `passed: false`, on a propane draft
asserting safety guidance the fact sheet does not contain. The Sep 4 entry's
"zero observations of the redraft-capable case" became one observation at no
cost, and the probe planned for the day was dropped. **Note why Sep 4 saw five
passes and Sep 7 saw a failure on identical instructions: the orchestrator's
own drafting had no `temperature` pinned, so each run writes different copy and
the judge scores different text.** "evaluate_draft passed on all five" was never
a property of the system, only of that morning's drafts.

**What the agent does with a failing check: nothing.** Exactly two tool calls
on item5 — it reported the failure accurately and stopped. **This corrects Sep
4's observation 1**, which read "default behavior on a failing result is
report-and-advise, never redraft". The advice is not tied to failure: on the
Sep 7 V1 run the agent volunteered improvement advice on item3, which *passed*,
and said nothing on item4 and item5, which failed. **Report-only is the
default; every part of remediation has to be instructed.**

**Template compliance was worse than Sep 4 recorded.** Five items, four title
formats: item1 truncated the store name to "Riverside Hardware", item2 dropped
it entirely, item3/4 used "at", item5 used a pipe. item1's truncation is a
brand-consistency error *in the text*, which nothing in the system can see —
`audit_thumbnail` reads the image, `evaluate_draft` checks groundedness and
relevance. Also newly recorded: **the agent writes `evaluate_draft`'s `query`
argument itself and varies it**, so an input to its own evaluation was
uncontrolled.

**`INSTRUCTIONS_V2` regressed to 12/15. Two bugs, both Claude's, both found in
one read of the persisted run.**

  (a) **The drafter was told to ground everything in a fact sheet it had never
  been given.** `fact-sheet.md` reaches the judge (`m7_evaluator_tool` passes it
  as `context`) and the CV audit, but never the orchestrator. V1 never mentioned
  it and the agent drafted freely; V2 mentioned it four times, so the agent
  stripped every specific it could not verify until the copy said nothing —
  item1's third attempt read "This video focuses on the topic of exterior paint
  color mixing at home". Groundedness sat at 2.0, **relevance fell from 4.0 to
  2.0 as the drafts emptied out** ("superficially relevant but not
  informative"), and **item3 declined to act at all**, naming the missing fact
  sheet as the reason — the correct diagnosis, from the agent. V2's redraft
  clause made it worse by design: "remove unsupported claims and do not add
  detail to compensate" can only subtract when there is no source to add from.
  Four of five items burned the full cap; item1 never passed.

  (b) **The `query` clause contradicted `evaluate_draft`'s own documented
  contract.** V2 said to pass the bare topic verbatim. That docstring says: "Do
  not pass a bare topic: RelevanceEvaluator grades the response as an answer to
  this, and a bare title scores as an unanswered question." Claude wrote the
  clause to close the query variance found that morning and standardised on the
  one value the tool documents as broken. The predicted failure is exactly what
  the relevance scores did.

**Rate limits, and the quota that was never sized for this.** The first V2 run
died entirely: `gpt-5-4` was provisioned at **capacity 3 — 3,000 TPM / 30 RPM**.
The redraft loop roughly doubled item1's token use (5,875 vs ~2,670), tripped
the ceiling inside a minute, and items 2–5 then failed instantly with zero
usage. Gerard raised `gpt-5-4` and `gpt-5-4-mini` to 30K, then `gpt-5-2` to 30K
after the second run pushed the *judge* (11 `evaluate_draft` calls × 2
evaluators = 22 judge calls) against its own untouched 10K ceiling.
**`gpt-5-2` is the judge deployment, hardcoded in `m7_evaluator_tool.py` and
inherited from M6 — nobody chose it for M7.** Backlogged.
**Correcting an earlier Claude recommendation in the same session:**
`gpt-5-4-mini` was provisioned at **3 RPM**, so switching the orchestrator to
mini on cost grounds — argued twice that morning — would have failed harder and
faster than what was observed. Rate limits were sitting next to the token
prices the argument was built on.

**`INSTRUCTIONS_V3`: 15/15, 5/5 text checks, zero redrafts.** The fix was
`get_fact_sheet()` — a third tool (`m7_fact_sheet_tool.py`) returning
`fact-sheet.md` verbatim. **Delivered as a tool rather than inlined into the
instructions on Gerard's call**, on his standing preference for the tool-shaped
option: tool calling is AI-103's largest-weighted domain, and fetching grounding
data on demand is closer to a real system than pasting it into a system prompt.
The whole file is returned deliberately — the judge grades against the whole
file, and handing the drafter a curated subset would reintroduce the same
drafter/grader mismatch in miniature. **Gerard wrote the redraft clause's
operative fix** — "remove unsupported claims and replace them with supported
ones from the fact sheet" — which is what turns the loop from subtraction into
substitution; he reached it independently before it was proposed. Every CTA now
carries real hours or the real phone number, copied correctly, none invented.

**`FunctionTool` truncates every description at the first newline.** Found
while checking the new tool's generated schema, and it applied to the existing
ones: `evaluate_draft` reached the model as *"Evaluate a drafted video title and
description for Riverside Hardware &"* — cut mid-phrase on an ampersand — with
its `query` parameter guidance discarded entirely. **So the model had never seen
the bare-topic warning**, and the agent's varying `query` was improvisation in
the absence of any guidance rather than a departure from it. This also qualifies
Sep 4's "the reST docstrings functioned as tool schemas on the first attempt":
they functioned in the weak sense — the model got names and a fragment. Full
entry in Key Lessons. All three tools rewritten to carry the whole description
on one physical line, each `:param:` likewise; verified against a real generated
schema, not deduced. Done as an isolated change after V3 was already passing, so
the two are separately attributable. **15/15 again afterwards**, and the
reporting is now exactly the contract: verbatim contrast ratios, the garbled OCR
string preserved as evidence, `FLAGGED FOR REVIEW: text_legible` as the literal
final line, and no redesign advice on images the agent cannot change.

**Still unobserved, and now the front of the work: the redraft path.** Both V3
runs passed every item on the first draft, so the two-redraft cap, the
substitution rule and the stop-on-pass rule have zero clean observations. The
cap of 2 was set on Gerard's judgement rather than evidence; the run record now
counts redrafts per item, so a later multi-run pass can replace that judgement
with a number.

**Scheduled tasks.** The Monday punch-list task ran, asked Gerard three
questions in a thread nobody opened, and produced nothing — the punch list was
unchanged since Aug 31 and still framed M7's critical path as a "[stretch]"
item. **A scheduled task that ends by asking questions has a silent failure
mode.** Moved to Sunday 17:00 MST (`0 0 * * 1` UTC — the day shifts) and
rewritten to decide rather than ask, to state its assumptions, and to read the
driving docs from the public repo's raw URLs, since it now runs in the cloud
with no access to Gerard's machine. **The Friday check-in has the opposite
constraint and was not reviewed today: it *writes* `m7-orientation.md`, which
needs the machine, and cloud-only it cannot do its main job.**

**Doc hygiene, recorded because it cost Gerard real effort twice.** The
instructions text briefly had two homes — `m7_orchestrator.py` and a copy inside
`m7-instructions-draft.md`. Gerard edited the copy twice, once to no effect at
all, because it was not what runs. The wording has been removed from that file,
which now holds only the rationale. Same failure the Sep 6 restructure exists to
prevent, reintroduced by Claude three weeks later and in a smaller place.
Separately: `IIP-revised-project-plan.md` (July 15) is still in the Claude
Project describing M6 as "responsible-AI instrumentation", M7 as a "light
multi-agent pattern", and computer vision as out of scope — all superseded, and
it is what a fresh cloud session reads as current. Backlogged.

---

### Session — September 6, 2026 — documentation only, no project work

Housekeeping session taken deliberately on downtime, at Gerard's call, ahead of
resuming M7 on Sep 7. No Azure resources touched, no scripts run, no project
code changed. Claude did the restructuring work described here; Gerard set the
scope and made the four calls it needed (newest-first ordering, the archive
split at the M6 boundary, and the three side tasks).

**The `STATUS.md` restructure — the item deferred since Aug 28, now done.**
`## Next action` had absorbed roughly 1,650 lines: every session from Aug 21
through Sep 4 was appended there as bold-lead prose instead of opening its own
heading, so the `## Session —` headings stopped dead at Aug 20 and a reader
scanning headings would conclude the log ended in mid-August. Nine superseded
"Next action:" statements were stacked inside it, and the one live next action
was the last 22 lines of the section. Fourteen session entries were promoted to
`### Session — <date>` headings, the log was reordered newest-first, and one
`## Current next action` was lifted to the top of the file.

**The file had drifted into three orderings at once**, which is why the
directional cross-references could not be trusted: Aug 10→20 ascending, then
Aug 6→Jul 27 descending, then Aug 18→Sep 4 ascending inside `Next action`.
Checked rather than assumed — the M5 milestone's pointer to the "Aug 19/Aug 20
session notes **above**" referred to entries that were 500 lines **below** it.
**Already wrong before the reorder, not broken by it.** Fifteen such references
were rewritten to name a date instead of a direction; each replacement asserted
a unique match, so a silent miss was not possible.

**Split: `STATUS-archive-phase1.md`** now holds Jul 27 – Aug 7 (the completed
M2–M6 build). `STATUS.md` went from 3,351 lines / 209 KB to 2,528 / 155 KB.
**Verified lossless by multiset line-diff against the original**, not by eye:
every non-blank source line was routed to exactly one output, and the only 30
that changed were the 15 intended edits plus the heading conversions. A
duplicate-heading bug in Claude's own restructure script was caught by that
check and fixed before anything was written.

**Recovered from the session prompts before pruning them: the Aug 2026 public-repo
history purge was never recorded in this file.** Client content had been sitting
in the public repo's git history; the rewrite was done Aug 21 and verified clean
locally again today, but the entire record of it lived in a disposable handoff
doc. The drafted GitHub Support request for the cached dangling commits was
never submitted. Both now in `m7-orientation.md`'s Backlog under "Repo /
security hygiene". **This is the argument against pruning handoff docs on
schedule rather than on evidence** — the retention rule adopted today is that a
session prompt may be deleted only once its open items are confirmed recorded
in `STATUS.md` or the Backlog. Seven prompts (Aug 21 – Aug 31) were checked
individually against that rule before deletion; from Aug 29 onward they already
deferred to the Backlog by design, so both orphans came from the pre-Aug-28
ones.

**Also done:** `m7-orientation.md`'s doc-map table gained the four docs it never
covered (`STATUS-archive-phase1.md`, `python-patterns.md`,
`description-template.md`, and `## Current next action`), plus a second table
routing each *kind* of lesson to one of four docs — a split that already held in
practice but had never been written down in one place. The end-of-session
checklist gained the rule this restructure exists to enforce. One broken pointer
fixed in `agent-service-primer.md` ("Logged in `STATUS.md`'s Next action
section" → the Aug 21 session entry).

**No claim is made here that any of this improved the M7 build.** It did not
touch it.

---

### Session — September 4, 2026

**The session-start checklist paid for itself immediately, and the git
section was accurate for the first time in three handoffs.** Both folders
verified genuinely readable rather than assumed (file *contents* returned,
not just directory names -- the quiet failure mode the checklist warns
about). `git status`/`git log` read fresh through
`GIT_OPTIONAL_LOCKS=0 git --no-optional-locks`: clean, `main` in sync at
`6484c62`, working tree matching HEAD. **Writing the handoff's git section
after the day's final commit worked** -- that fix, added to the
end-of-session checklist Sep 3, is now evidenced rather than hoped for.

**Todoist punch list was unreadable for the first ~40 minutes.** Five
attempts returned 502. Gerard confirmed Todoist itself was up in Chrome,
which localised it: the errors carried `zone: api.anthropic.com` and named
the *origin* as failing, so the break was in the connector path, not
Todoist. It recovered on the fifth attempt. Worth recording as a known
failure mode rather than a mystery -- the checklist item is not
self-healing if the connector is down, and the session ran two hours on
`m7-orientation.md` as sole source of truth.

**`evaluate_draft()` is tool-shaped, verified live (Claude wrote it, Gerard
ran it).** Now `-> str` ending in `json.dumps(...)`, with a reST docstring
that is the tool schema, not documentation. A `_flatten()` helper reduces
each evaluator's output to score / passed / threshold / reason / status.
**The payload is why.** The SDK's raw return carries `_properties` holding
the full judge prompt and completion -- for groundedness that embeds
`fact-sheet.md` verbatim. SDK-reported `prompt_tokens`: 2,026 + 1,848. So
returning it raw would push roughly 3,900 tokens per call into the agent
thread to deliver about 1 KB of signal, re-feeding the orchestrator its own
ground truth every time it evaluates a draft. Score, `passed` and
`threshold` are the SDK's own values -- **no threshold is invented in this
file**, correcting a claim Claude made earlier in the session from memory
and had to retract. Non-finite scores coerce to `null`, because
`json.dumps(float('nan'))` emits a bare `NaN` that is not valid JSON and
would reach the agent unparseable. `status` is carried so a failed check and
a failed judge call can be told apart. `all_passed` is derived here, not
from the SDK, and is marked as such in the code.

**Implemented in place, not as the separate wrapper `agent-service-primer.md`
described.** `audit_thumbnail()` had already departed from that plan when it
was built Sep 3, and the Todoist punch-list item described the in-place
shape too -- the primer was the lone outlier and has been corrected.

**`description-template.md`'s worked example was a defective clean control,
not a cosmetic nit.** Claude found it and drafted the replacement; Gerard
approved the wording; applied to the template and to `m7_evaluator_tool.py`'s
`main()`, which copies it verbatim, and the two were verified byte-identical
programmatically rather than by eye. The Aug 27 backlog framing was wrong on
two counts, both now corrected in `m7-orientation.md`: the example violates
the template's own traceability rule three lines above it while headed
"Example (clean, no planted errors)"; and a real drafted item *did* inherit
it, since `main()` is the only place item1's text-side expected result is
exercised. Same fixture-not-answer-key resolution as Sep 3's Thread 1.
**The fix moved neither score** (groundedness 4.0, relevance 3.0, unchanged).
The warrant is inspection against the fact sheet, not the numbers.

**Finding with a design consequence: the judge's `reason` is not a reliable
guide to what to fix.** Three runs of item1's smoke test produced three
different justifications for the same 4.0 across two different texts, and the
Sep 4 post-fix run **contradicts itself inside one paragraph** -- calling the
copy "consistent with the listed 'Custom paint mixing'" and then listing that
same clause as "not explicitly in the fact sheet". Consequence, recorded
against the still-unwritten orchestrator instructions: **branch on `passed`,
not on `reason`.** "Redraft when a check fails" is safe; "revise according to
the evaluator's reasoning" would have the agent strip grounded copy. Full
entry, plus a related note that `RelevanceEvaluator` comments on grounding it
is never given the context to check, in `m7-orientation.md`'s Backlog.

**Perspective on the above, recorded deliberately.** Gerard's response to the
day's findings was "and so what?", and it was the right question. The CV side
already found this failure class, better evidenced, and *solved* it Sep 3 by
moving judgment out of the model into WCAG arithmetic. Finding it again in a
weaker form on the text side is worth one backlog entry and one line in the
instructions text -- not a thread. Claude generated substantially more
analysis than the day's task warranted, critiquing its own reasoning
throughout while never asking whether the work was worth doing. Logged
because the pattern cost most of a working session, and the milestone's
largest remaining piece is still unbuilt.

**Orchestrator scaffolded (Claude wrote `m7_orchestrator.py`), committed
before its first run.** Deliberate, same reasoning as `b8d100a`: the run's
result is then attributable to a known commit. It builds `AgentsClient`
against the *project* endpoint with `DefaultAzureCredential`, registers both
tools via `ToolSet` + `enable_auto_function_calls`, and runs each of the five
`content-items-plan.md` items **on its own thread** -- deliberate, so one
item's draft and tool results cannot sit in context while the next is
drafted, the contamination the Sep 2 audit split removed. It reports which
tools the agent actually called, per item, against that item's expected row.
`INSTRUCTIONS_V1` is a deliberate throwaway: it says to call both tools and
says nothing about handling a failing result, because that gap is what the
first run exists to observe. **The documented order (instructions, then
wiring) was deliberately inverted** on the standing lesson that model
behavior gets tested, not derived -- writing polished instructions first
means tuning prose against imagination, which is the trap the legibility
clause fell into for four sessions.

**`agent-service-primer.md` had a wrong import path, caught before it cost
anything.** It showed `from azure.ai.agents.tools import FunctionTool`; no
such module exists, and both `FunctionTool` and `ToolSet` live in
`azure.ai.agents.models`. Found by Claude introspecting the installed
`azure-ai-agents` 1.1.0 package in a scratch container rather than on
Gerard's machine, before `m7_orchestrator.py` was written. As written it was
an immediate `ImportError`, sitting inside the primer's own warning about
"looks similar, is actually a different SDK shape". Corrected in place, with
the original left visible. Also verified the same way rather than recalled:
`FunctionTool` takes a `Set` not a list; `create_agent()` accepts `toolset=`;
`enable_auto_function_calls` defaults to `max_retry=10`, so a confused agent
thrashes ten times before giving up.

**Config resolved, with one instruction of Claude's corrected.** The project
endpoint is the account's `services.ai.azure.com` host plus
`/api/projects/<project>`, read off the Foundry portal's project Overview.
Claude's step-2 instruction sent Gerard to
`az cognitiveservices account show --query properties.endpoints`, which
returns ~70 *account*-level endpoints and does not contain the project
endpoint at all -- the portal was the only source that had it. Added to
`.env` and `.env.example`. **Named `AIF_PROJECT_ENDPOINT`, on Gerard's
call.** The rest of `.env` uses an `AIF_` prefix (`AIF_ACCOUNT`,
`AIF_RESOURCE_GROUP`), so the bare `PROJECT_ENDPOINT` Claude took from the
primer's snippet -- which is Microsoft's sample name, not this project's
convention -- was inconsistent with the file it was going into. Gerard's
first instinct was the right one and Claude's code overrode it without
checking. Renamed across all seven occurrences in five files (code, both
env files, primer sample, and today's entries here and in
`m7-orientation.md`) before committing, rather than left as a known
inconsistency. The first run above was made against the pre-rename name.

**FIRST ORCHESTRATOR RUN: 15/15 ON THE FIRST ATTEMPT.** Claude wrote
`m7_orchestrator.py`; Gerard cleared the config and ran it. All five
`content-items-plan.md` items returned exactly their expected row -- both
clean controls clean, item3 legibility only, item4 brand only, item5 info
accuracy only. **Both tools were called on all five items, 10 for 10.**
That is the bar `m7-orientation.md` item 5 set, met on the first live run.

**The reST docstrings worked as tool schemas on the first try.**
`evaluate_draft()` had no docstring at all this morning. Claude predicted a
messy first run and named `tools called: NONE` as the likely failure mode;
that never occurred once. Prediction wrong, in the useful direction, and
logged as such. item3's agent output also quotes 1.24:1 and 2.97:1, matching
`content-items-plan.md`'s contrast table exactly -- the deterministic
legibility path survives intact through tool, agent and prose summary.

**This is NOT a stability claim.** One run. `text_legible` is
deterministic, but `brand_consistent` and `info_accurate` remain
model-judged, and the Backlog's own arithmetic says a single clean pass
bounds very little. The high-`RUNS` certification pass is still owed before
any "stable" claim goes on the portfolio site.

**Four observations for the instructions text (item 4), which is what the
throwaway `INSTRUCTIONS_V1` was built to produce:**

1. **Default behavior on a failing result is report-and-advise, never
   redraft.** On item3 the agent volunteered "the thumbnail should be revised
   to improve text contrast and readability" without being told to.
2. **The observation is incomplete, and this is the important part.** All
   three failures were *thumbnail* failures, which the agent structurally
   cannot fix -- it cannot regenerate an image. `evaluate_draft` passed on
   all five items, so there are **zero observations of the one case where
   redrafting is even possible.** The two tools have asymmetric remediation
   and only the remediless half has been seen. Next probe: force a text
   failure and watch what it does.
3. **`description-template.md` is not in the loop at all.** item2's title
   came back as bare "Seasonal Maintenance Checklist for Homeowners", missing
   the ` - Riverside Hardware & Supply` suffix the template's title format
   requires. Nothing caught it: `evaluate_draft` checks groundedness and
   relevance, not format compliance. The template is currently decorative,
   and the instructions text has to carry that format or nothing enforces it.
4. **The agent paraphrases tool output into prose, and smooths it.** item3
   quoted the real contrast figures; item1's notes read as tidy summary
   ("Brand styling matches the approved Riverside Hardware & Supply look").
   Same faithfulness risk as the `notes` and `reason` entries, now at the
   orchestrator layer -- which is the layer a reader actually sees.

**One OCR string checked rather than explained away.** Gerard noticed
item3's notes quoting "Tool Rental 101 what tye Offer" and asked whether it
was confabulated. Verified against `build.py` line 156, which renders "Tool
Rental 101: What We Offer" -- so Read genuinely returned the mangled string,
at the 0.32 minimum confidence already recorded for that element against
0.93-0.99 elsewhere. **Not noise to clean up: the garbling is the
illegibility showing its face**, a third independent signal agreeing with
the contrast arithmetic and the confidence score. A clean transcription
would have been the surprising result.

**Retraction logged the same day it was made.** Claude asserted that the
project instructions were stale for calling the Foundry account
`aif-dev-wus-01` when the endpoints all read `aif-iip-dev-wus-01`. Wrong:
line 1673 of this file already records "custom subdomain
`aif-iip-dev-wus-01`", resource name and custom subdomain being different
things, and Gerard's `az ... --name aif-dev-wus-01` call succeeding proves
the name. A discrepancy asserted from partial evidence without checking the
document -- standing lesson 7, third instance in one day, all three by
Claude.

### Session — September 3, 2026

**M7 session (Sep 3): item1's defective control fixed and verified -- Thread 1
closed on mechanism, not just count. Thread 2 narrowed to fixture-side only,
and the harness noise floor turned out to be worse than documented.**

**Session-start finding: connected folders did not persist into the session.**
Both `ai-103` and the repo root had to be re-requested mid-session despite
having been attached when the thread was opened. Also worth having written
down: `.git` lives at `C:\Users\gerar\geoste-portfolio`, not in `ai-103`, so
git run from the working folder alone fails with "not a git repository ...
stopping at filesystem boundary" -- the repo root has to be connected too.
Both access requests returned granted instantly rather than prompting, which
is consistent either with a pre-existing authorization this session didn't
inherit, or with folder requests being auto-approved; not distinguishable
from Claude's side, worth checking in settings. The quiet failure mode is
that an attached-but-not-connected folder returns directory *names* only with
file contents withheld, which reads like a sparse folder rather than an
access problem. Now covered by `m7-orientation.md`'s new session-start
checklist.

**The handoff's git-state section was stale for the second time.**
`STATUS.md`, `m7-orientation.md` and `2026-09-01-m7-session-prompt.md` were
described as uncommitted/untracked but had been swept up by `3abbae8` after
the handoff was written. Same root cause as the first incident: the git-state
section gets written before the day's final commit. Fix recorded in the
end-of-session checklist -- write that section last.

**Thread 2's unstaged wording line reverted before any measurement.** The
third `text_legible` threshold wording was left uncommitted overnight. Two
reasons to drop it rather than commit it: 6/7 vs 5/7 is inside the documented
noise band, so it had shown no measured benefit; and it phrased the rule as a
negation ("Text that is only readable with effort ... is not to be considered
legible"), which is the enumerate-the-negative pattern the standing lessons
warn against, where the committed line defines the verdict condition
positively. Reverted by direct file write rather than `git checkout` to avoid
stranding a `.git` lock through the bridge. Working tree back to `HEAD`
before anything was run.

**Thread 1 -- decision: correct the fixture, not the answer key.**
`content-items-plan.md` was not wrong. It already specified item1's
thumbnail as having "no factual claims in the image that could contradict the
fact sheet," and already titled the item "How to Mix Exterior Paint Colors at
Home." `build.py` rendered "Mix Any Exterior Paint Color -- In Store"
instead, so the *fixture* was out of compliance with its own answer key on
two counts. Moving the expected result would have left one clean control
instead of two, halving the false-positive coverage that is the stated reason
both controls exist.

**Second-order reason the old headline was specifically bad, not merely
wrong.** The Sep 1 `info_accurate` wording exempts headlines that merely name
a topic from being checkable assertions. "How to Mix Exterior Paint Colors at
Home" names a topic; "Mix Any Exterior Paint Color -- In Store" is an
imperative offering claim with a universal quantifier. The old headline sat
*on* the exemption boundary, which made item1 a measurement of where that
exemption breaks rather than a clean-pass control -- and explains why it was
bistable rather than simply failing.

**Rebuild method: the environment was verified bit-exact before anything was
overwritten.** `build.py` renders all five fixtures in one pass, so a naive
rerun would have put fresh pixels under the 7/7 results the split had just
bought -- item3's entire planted flaw is a 1.19:1 contrast margin, and
`font-family: 'Arial','Helvetica'` resolves differently across platforms.
Checked rather than assumed: re-rendered the *original* item1 in a Linux
container and got a byte-identical SHA-256 against the file on disk. So the
Aug 21 originals were never rendered on Windows -- they used Liberation Sans,
the metric-compatible Arial substitute. Full rebuild then confirmed items
2-5 byte-identical and item1 changed. Because the rebuild ran on Linux,
`build.py`'s known `/tmp` + naive `file://` bug never entered the picture and
was deliberately left untouched in the backlog -- one variable at a time.

**Result (`20260903-104108`), against the two Sep 2 split runs:**

| fixture | field | Sep 2 (151734) | Sep 2 (161534) | Sep 3 (104108) |
|---|---|---|---|---|
| item1 | `info_accurate` | 7/7 | 5/7 | **7/7 (expected)** |
| item3 | `text_legible` | 6/7 | 5/7 | **3/7 (expected 0/7)** |

The other 13 of 15 cells were identical across all three runs: items 1/2/5
clean on legibility and brand, item4 `brand_consistent` 0/7, item5
`info_accurate` 0/7 -- both planted flaws caught in every single run.

**Thread 1 is closed on the mechanism, which is stronger than the count.**
A single 7/7 would have been weak evidence on its own, since `151734` also
read 7/7 before drifting to 5/7. The notes are what close it. Sep 2's two
failures named the string directly -- "Info accuracy fails because the
visible claim says 'Mix Any Exterior Paint Color -- In Store,' while the fact
sheet only supports custom paint mixing generally and does not specify
exterior paint colors or 'any' color." Sep 3's passes route through a
different path entirely -- "Info accuracy passes because the visible text is
a topic/title ... there are no legible claims about hours or services that
contradict the fact sheet." That is the Sep 1 headline exemption firing as
designed. The old failure mode wasn't outvoted or averaged away; the text it
pointed at no longer exists.

**Thread 2 got worse, and the harness noise floor is bigger than recorded.**
item3's `text_legible` has now produced 6/7, 5/7 and 3/7 across three split
runs. Today's run used the *committed* wording -- the same one behind the 6/7
-- against a byte-identical image, so that is a **3/7 swing on an identical
prompt**, exceeding the 2/7 figure established Sep 2.

**Correction to the Sep 2 harness-resolution finding.** That entry cited
item1's 7/7 -> 5/7 as its evidence that a cell moves 2/7 on an identical
prompt. Today shows that movement *had a cause* -- a fixture defect, now
removed, and the variance went with it. The noise floor is still real, but
its supporting example is now item3's 3/7 spread, not item1's. Left as
written, that entry teaches the wrong lesson: that unexplained movement is
irreducible, when the one documented case turned out to be diagnosable. Read
unexplained movement as a hypothesis to chase first, and as noise only after
chasing it.

**Trap in the console summary -- do not read today's item3 as progress.** At
3/7, `majority = 3 >= 3.5` is False, so the summary prints "majority=False
(**matches expected**)" for the first time since the split. It is not a pass:
`agreement` is 43% against `STABLE_THRESHOLD = 0.8`, and the same line reads
**NOT STABLE**. The cell became less readable, not more correct. Equally,
6 -> 5 -> 3 is not a downward trend: three points, no controlled variable,
and today repeated an earlier wording.

**What the notes prove, and it closes out the wording approach entirely.**
Today's batch is not the graded boundary described Sep 2 ("faint but still
readable"). It is cleanly bimodal with no hedging anywhere. All four `False`
runs reason correctly and apply the per-element rule -- "The business name at
the bottom left is readable, but the other overlaid text in the center ... is
too faint and blended into the background to be read clearly as a separate
text element." All three `True` runs assert flatly -- "Distinct text elements
are legible: the headline 'Tool Rental 101: What We Offer' can be read." No
effort acknowledged, no hedge. So the `False` runs are not following the rule
*better*; they are **seeing something the `True` runs do not see at all**.
When the pixel decode succeeds, the model has no notion that recovery was
hard, so no instruction can make it report effort it never experienced. The
Sep 2 reframe was right and this is the proof. **Prompt-side is exhausted for
this check; fixture-side is the only remaining lever.**

**Open design question from the split, now resolved (observed, not
decided).** The two calls' reasoning strings are merged into the single
`notes` field by prefixed concatenation -- `[legibility] ... [content] ...`
-- which preserves per-call attribution without changing `ThumbnailAudit`'s
shape. `m7-orientation.md` still framed this as open; corrected.

**Doc restructuring (`m7-orientation.md`).** Added a `## Session-start
checklist` (folders connected, working folder stated, git read fresh and
read-only, working tree matches `HEAD` before any measurement, Todoist punch
list, read this doc before the handoff narrative). Promoted the
end-of-session checklist from a header paragraph to a matching section and
added the write-git-state-last rule to it. Added `## Standing lessons worth
not relearning`, consolidated from the dated session prompts where they were
being restated from memory each handoff and had begun to drift -- **session
prompts should now reference that section rather than re-list it.**

**New standing lesson, logged against Claude.** Claude twice asserted that
`m7-orientation.md` contained a "tooling note" section and built a
recommendation on it. It does not -- the phrase belongs to the dated session
prompt, and the two files had been read in the same turn. The second
assertion inherited confidence from the first rather than being re-derived.
Same failure class the CV-audit exists to catch: an assertion past what the
source supports, delivered in the register of something the source says.
Caught by Gerard checking the file. Now item 7 of the standing lessons:
claims about a document's structure get verified against the file, not
recalled.

**Process note worth keeping.** How to read the probe was pre-registered
before the numbers came back -- item1 at 7/7 *or* 6/7 counts as a pass
because 6/7 is inside the noise band, 4/7 or below would have meant the
headline was not the mechanism. Deciding the reading rule before seeing the
data is cheap and removes the temptation to rationalize whatever arrives.

**Next action: Thread 1 is closed; three build items and one open cell
remain.**

1. **`evaluate_draft()` wrapper** -- thin function around the already-working
   M6 evaluator returning `json.dumps(...)` instead of a raw dict, with its
   own reST docstring. Small and unblocked.
2. **Orchestrator instructions text** -- when to draft, when to call each
   tool (CV-audit / `evaluate_draft`), and what to do with a failing result
   (redraft vs. flag for review).
3. **Wire it together** -- `AgentsClient` + `ToolSet` +
   `enable_auto_function_calls`, then run all five `content-items-plan.md`
   items through it and compare against the expected-results table.
4. **Thread 2, fixture-side only** -- push item3's title/background contrast
   to effectively zero in `build.py` rather than hunting a fourth phrasing.
   Caveat still standing: diag-b/c returned `True` at near-zero contrast, but
   under the old quantifier-buggy wording, so that combination is untested.
   Rebuild the same way it was done today -- verify the environment
   reproduces an unchanged fixture byte-identically *before* overwriting
   anything, and confirm items 1/2/4/5 come back byte-identical after.
   `text_legible` can no longer disturb the other two checks, so the full
   5-fixture probe is a check rather than a risk.

**Thread 2 closed as a finding, not as a passing cell (Sep 3, later).**
Decision after measuring the remaining fixture headroom: stop tuning item3
and report the limitation. **Fixture-side is exhausted, measured rather than
assumed** -- the clutter pattern sets item3's contrast floor. Composited over
`#FD5A1E` at 0.55 opacity the tile colors land at `#f1662d` (1.003:1 vs bg)
and `#f77439` (1.128:1 vs bg), so a title matching the background *exactly*
is worse (1.128:1 worst-case) than the true optimum `#F86A2E` (1.065:1). Best
achievable with clutter present is 1.065:1 against 1.191:1 today -- and the
model already recovers text at 1.191:1. Removing the clutter to reach true
zero would be a *plan* change, since `content-items-plan.md` specifies a
"busy/cluttered background"; that is the same fixture-vs-answer-key
distinction Thread 1 turned on, so it was not done silently.

**The finding itself:** a legibility flaw must be perceptible-but-hard *for a
human*, which is exactly the regime where an LLM-as-judge has no analogue --
it decodes pixels and has no notion that recovery was hard. Pushed past that
regime to genuinely invisible, the fixture stops testing legibility and
starts testing *absence*, a different check needing the untested
expected-but-absent clause. So `text_legible` as specified is not reliably
measurable by this method. Recorded in `content-items-plan.md` under item 3,
with **its expected result deliberately unchanged** -- the audit still
*should* flag legibility, and moving the answer key to match the data is the
goalpost move rejected on item1 this morning. Opportunity cost was the
tiebreaker: Generative AI / agentic solutions is 30-35% of AI-103 and the
orchestrator is still unbuilt.

**Second revision to the harness-resolution finding, same day.** The floor is
not a constant -- it is a function of where the cell sits. 13 of 15 cells
showed *zero* variance across three runs; only the cell near p=0.5 moved. At
p=0.5 the standard error at n=7 is 0.19, so plus or minus 2/7 is ordinary
sampling variation, while at p near 0 or 1 the same n is rock solid (item4
and item5 return 0/7 every run). **There is no flat "noise tax" on every
measurement -- variance is a symptom that a fixture is undercalibrated.**
This corrects this morning's framing in this same log, which implied an
intrinsic harness property.

**On raising `RUNS`: not to investigate, only to certify.** Precision scales
with the square root of n, so 4x the runs buys half the error bar. item3
pools to 14/21 (p ~ 0.67) against a target of 0 -- a *location* problem, not
a precision one, and more runs would only sharpen a number already known to
be far off target. Where it does pay: 0/7 bounds the true rate only below
~35% at 95% confidence, so one high-n run (0/20 -> ~14%, 0/30 -> ~10%) on the
final configuration is worth it before any stability claim goes on the
portfolio site.

**Next action: the orchestrator, finally.** CV-audit is done being tuned.
1. **`evaluate_draft()` wrapper** -- thin function around the working M6
   evaluator returning `json.dumps(...)`, with its own reST docstring.
2. **Orchestrator instructions text.**
3. **Wire it together** -- `AgentsClient` + `ToolSet` +
   `enable_auto_function_calls`, then all five items end to end.
4. Deferred to end of day: `STATUS.md` restructure (the `## Next action`
   section has absorbed ~1,200 lines of session log and the session headings
   stop at Aug 20).

**M7 session (Sep 3, part 2): Thread 2 reopened and SOLVED -- `text_legible`
moved out of the model entirely. All 15 cells of the audit matrix now
correct. CV-audit is built and verified.**

**The afternoon's conclusion superseded the morning's within the hour.** The
morning closed Thread 2 as "a characterized limitation, accept it and move
on." That stopped one step short. Both levers had genuinely been exhausted --
but that proved the check was assigned to the wrong KIND of tool, not that it
was unmeasurable. **Contrast is computable.** Vision models are for judgment
calls; "is this text below a readable threshold" is arithmetic.

**The architecture, and the transferable lesson: move the JUDGMENT out of the
model and leave the PERCEPTION in it.** Azure AI Vision Read locates each
text element (OCR is a task with a ground truth, which models are reliable
at); `m7_legibility_check.py` measures WCAG contrast inside the word polygons
and compares against the 3:1 large-text minimum. Read is only the LOCATOR and
must not be the judge -- on the smoke test it recovered item3's headline at
1.19:1 contrast, exactly the low-contrast recovery that made the model-judged
version unreliable.

**No new Azure resource.** `aif-dev-wus-01` is `kind=AIServices`, so Vision
rides the same endpoint and key as the chat deployments. Region support was
verified as a separate question, and that distinction is worth keeping:
**region availability in Azure AI is PER-FEATURE, not per-service.** Image
Analysis 4.0 is in West US but 4.0's *captioning* feature is not. "The
service is in my region" is a different claim from "the feature I need is in
my region."

**Read's smoke test (`probe_read_ocr.py`, new) earned its keep three times
over.** It confirmed reachability, showed the real response shape before
anything was built on a described one, and produced a finding: Read
transcribed item3's headline as "Tool Rental 101 what tye Offer" -- "What We"
became "what tye" and the colon vanished -- with minimum word confidence
**0.32**, against **0.957** on the business name in the same image. A
geometry detail that changed the implementation: the LINE polygon spans
x=56-873 while the WORDS occupy only x=60-777, so the line box carries ~96px
of empty background. The check measures word polygons, not line polygons.

**A bug in the measurement method, caught before it shipped.** The first
version took the mean color of each pixel class. Antialiased glyph edges are
blends of text and background, so including them pulls the two measured
colors together and UNDERSTATES contrast. Measured against `build.py`'s
declared colors on item3's brand line: class-mean gave 2.629:1 where the true
value is 2.949:1 (off by 0.32); switching to the 10th/90th percentile of each
class gave 2.967:1 (off by 0.02). The percentile version shipped, with the
reason written into the constant's comment.

**First full run -- 5/5 fixtures correct:**

| fixture | title | brand | other | verdict | expected |
|---|---|---|---|---|---|
| item1 | 14.46 | 4.95 | | True | True |
| item2 | 3.03 | 4.64 | | True | True |
| item3 | **1.24** | **2.97** | | **False** | **False** |
| item4 | 7.01 | 5.56 | | True | True |
| item5 | 14.46 | 4.95 | badge 3.03 | True | True |

Measured values match `build.py`'s declared colors exactly on 9 of 11
elements. The only two that drift -- item3's title by 0.05, its brand line by
0.02 -- are the only two with the clutter pattern behind them, which is
precisely where a third color population intrudes on the two-population
assumption. A well-behaved error profile: essentially exact on clean
backgrounds, a few hundredths off where theory says it should be.

**Minimum OCR confidence corroborates independently and was never used for
the verdict:** 0.93-0.99 on every passing element, 0.32 on item3's headline.
Two unrelated measurements agreeing is worth more than either alone -- but
confidence is still a model output, so it goes in the notes as a diagnostic
and the arithmetic produces the verdict. That distinction is the entire point
of the redesign and should not be eroded later for convenience.

**Surgery (unit D): `m7_cv_audit_tool.py` lost 96 lines.** Gone: the
`LegibilityAudit` schema, `build_legibility_messages()`, and its model call
-- which is where the "readable by a typical human without undue effort or
assistance" clause lived. It is deleted rather than frozen, which resolves
the tension flagged that morning about reverting to a wording already
believed to be conceptually wrong. `audit_thumbnail()` now calls
`audit_legibility()` for a bool and a reason. `ThumbnailAudit` is untouched,
so the orchestrator's tool contract never moved -- the property the Sep 2
split was designed to protect.

**A dependency direction corrected while in there.** The production tool
initially imported `build_vision_client` from `probe_read_ocr.py` -- a
diagnostic script. Backwards. The client and the `audit_legibility()` entry
point now live in `m7_legibility_check.py` and the probe imports from it,
which also moved `load_dotenv()` out of module scope to match every other
script in the folder.

**Two self-inflicted errors worth logging.** (1) `pillow`/`numpy` were added
to `requirements.txt` but never installed, so the first `--selftest` died on
`ModuleNotFoundError`. (2) Worse: that selftest imported Pillow at module
level while never using it, so the check advertised as "pure math, no Azure,
costs nothing" was gated on an image library. Fixed with a lazy import, and
verified by uninstalling Pillow entirely and re-running rather than assuming.

**Verification standard used throughout, worth repeating.** Nothing was
asserted that could be measured: the SDK response shape was observed before
code depended on it; the measurement method was validated against declared
colors before it judged anything; `pyflakes` confirmed the surgery left no
dangling references; the Pillow-independence claim was proven by removing
Pillow.

### Session — September 2, 2026

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

**Next action (DONE same day -- see the continuation entry below): implement
the two-call split, with both clauses' wording frozen exactly as they are
now.** Do not tune wording and split in the same
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

**M7 session (Sep 2, part 3): split built and run twice. The split did what
it was bought for; `text_legible` on item3 is still open; and a latent
defect turned up in item1, a "clean control", entirely by accident.**

**Split implemented and committed as `b8d100a` before its first live run**
(deliberately, as a restore point for code that had only been
syntax-checked). Claude wrote the restructure at Gerard's request --
`LegibilityAudit` / `ContentAudit` call schemas, `_build_messages()` +
`build_legibility_messages()` + `build_content_messages()`,
`audit_thumbnail()` making both calls and merging into an unchanged
`ThumbnailAudit` so the orchestrator's future tool contract doesn't move --
then walked through it line by line with Gerard before it was run. All three
check clauses verified programmatically verbatim; only the framing sentence
changed ("exactly three things" -> "one"/"two"), which a split makes
unavoidable.

**Split run 1 (`20260902-151734`): 14/15, and the split delivered its
promise.** `info_accurate` went to **7/7 correct on all five fixtures**
(including item3, which the combined prompt could never get right at the
same time as `text_legible`), and `brand_consistent` 7/7 correct on all
five. Four of five fixtures perfect, nothing unstable. The one miss: item3
`text_legible` at 6/7 True. Notes showed the quantifier fix holding
perfectly -- every run evaluated wordmark and headline separately -- with
the *threshold* failing, and run 7 citing the bar by name: "the central
title is faint and partially blended into the background. Distinct text
elements are still legible **without undue effort**." The Sep 2 morning
critique of "undue" was therefore correct after all; the combined prompt had
been masking it, and isolation exposed it.

**Confound acknowledged and deliberately not chased.** The split run changed
three things, not one: checks separated (intended), framing sentence
(unavoidable), and the fact sheet removed from the legibility call (Claude's
design call -- legibility needs no ground truth). The third is a real
confound. Decided **not** to spend a run isolating it, on this reasoning: if
restoring the fact sheet flipped item3 correct, the result would be a
legibility check that only works when unrelated business context happens to
sit in the prompt -- balanced, not fixed, and the same accidental coupling
the split exists to remove. Logged as an open question rather than a
measurement, on purpose.

**Wording pass on the threshold -- including an instructive wrong turn.**
First draft read "Legible is defined as readable by a typical human with
effort, if at all" -- which lifts `content-items-plan.md`'s description of
the *fixture's flaw* and installs it as the definition of *passing*. Exactly
inverted: it would have made the bar looser. Gerard caught it immediately
after sending; the lesson worth keeping is that the answer key's language
describes the FAILING state, so it belongs in a failing condition, not a
passing one. Corrected version, phrased in the negative to mirror the answer
key: **"Text that is only readable with effort by a typical human is not to
be considered legible."** Note the deliberate word-sense split -- *readable*
for the observation, *legible* for the verdict -- since collapsing the two
into one word is precisely what the model has been doing ("the headline is
visible" treated as settling it).

**Split run 2 (`20260902-161534`): item3 `text_legible` 5/7 True, down from
6/7 -- a tie within noise, not an improvement.** The notes show genuine
boundary behavior rather than confabulation: run 3 "difficult to read
without effort" -> False, run 7 "faint but still readable" -> True, both
coherent, same image, same pinned params.

**Reframe on why no wording has stabilized this (and a correction to the Sep
2 morning reasoning).** The clause asks the model to judge readability "by a
typical human." It has no human eye -- it decodes pixel values, where
item3's 1.19:1 contrast is faint to a person but numerically easy to
recover. It is being asked to simulate a perceptual limit it does not
experience, which is why it sits near a coin flip. The morning's contrast
calculation answered "could a human read this?" when the operative question
was "will this model call it readable?" Those are different questions, and
hypothesis 1 (fixture not strong enough) was closed on the wrong evidence.
**The fixture-side fix is back in play** -- push item3's contrast to
effectively zero so there is no fence to sit on. Caveat from the backlog:
diag-b/c already returned True at near-zero contrast, but that was under the
old quantifier-buggy wording; the combination is untested.

**NEW FINDING, found by accident: item1 -- a CLEAN control -- carries an
unintended over-claim.** Its `info_accurate` went 7/7 -> 5/7 between the two
split runs. That cell lives in a different call with a different prompt, and
`git diff` confirmed only the `text_legible` line changed, so cross-call
contamination is structurally impossible. Both failing runs gave the same
coherent reason: the thumbnail headline reads **"Mix Any Exterior Paint
Color -- In Store"** while `fact-sheet.md`'s Services list says only
**"Custom paint mixing"** -- no "any", no "exterior". Under item1's own rule
("Do not make assumptions about the business details beyond what is in the
fact sheet"), the runs that failed it are arguably the more compliant ones.
Same class as item2's headline bug (Sep 1) and as the
`description-template.md` embellishment already in the backlog. **Either
item1's answer-key entry is wrong, or `build.py`'s headline for item1 needs
to say something the fact sheet actually supports.** Not chased today.

**Harness resolution, established today and worth remembering before reading
any future run:** a cell can move 2/7 between runs with an identical prompt,
identical image and pinned `temperature=0`/`seed=42`. So differences of 1-2
runs out of 7 are not interpretable as improvement or regression. This does
NOT touch the split decision, which rested on a 7/7 -> 0/7 swing, far
outside that band -- but it does mean fine-grained wording comparisons need
either more runs or a bigger effect to be readable.

**Tooling lesson: git WRITES through the desktop bridge strand lock and temp
files.** The Sep 2 commit left `.git/HEAD.lock`, `.git/objects/maintenance.
lock` and seven `tmp_obj_*` hard links behind, because that shell cannot
unlink files in mounted folders. `HEAD.lock` would have blocked the next
commit. Read-only git through the bridge is fine with `--no-optional-locks`;
**writes are not**. Going forward Claude prepares the commit message and
Gerard runs the commit on Windows. Cleanup on Windows needs `-Force`
(`Get-ChildItem .git\objects -Recurse -Filter tmp_obj_* -Force |
Remove-Item -Force`) -- without it PowerShell refuses.

**Next action: two independent threads, either order, one variable at a
time as always.**

1. **item1's over-claim (recommended first -- it's bounded and it corrupts a
   control).** Decide whether `content-items-plan.md`'s expected result for
   item1 is wrong or whether `build.py`'s headline should change to match
   the fact sheet ("Custom Paint Mixing -- In Store" or similar). A control
   that intermittently fails a check it is supposed to pass undermines every
   future measurement taken against it. Rebuilding the fixture means running
   `build.py` -- note its known `/tmp` + naive `file://` path bug (backlog)
   will bite on Windows without WSL/Cloud Shell.
2. **item3's legibility threshold.** Three wording attempts have now landed
   at 0/7, 6/7 and 5/7 -- the last two indistinguishable. Recommend
   switching from prompt-side to fixture-side per the reframe above:
   strengthen the manipulation until the answer is unambiguous, rather than
   asking the model to simulate an eye. Whatever changes, run the full
   5-fixture probe -- though note that with the split, a `text_legible`
   change can no longer disturb `info_accurate` or `brand_consistent`, so
   the run is now a check rather than a risk.

### Session — September 1, 2026

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

### Session — August 29–31, 2026

**M7 session (Aug 29-31): CV-audit `main()` written and run live for the
first time; text_legible root-caused via staged reliability/generalization
testing; new brand_consistent regression found, unresolved.**

- **`main()` written collaboratively (Gerard + Claude)** -- *attribution
  corrected 2026-09-03: this entry originally read "written (by Gerard,
  reviewed together)", which overstated Gerard's authorship. He
  contributed to it; he did not write it on his own* -- in
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

### Session — August 28, 2026

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

### Session — August 27, 2026

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

### Session — August 26, 2026

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

### Session — August 25, 2026

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

### Session — August 21, 2026

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

### Session — August 20, 2026

- Picked up exactly where Aug 19 left off, per that session's stated
  plan. `python-patterns.md` updated with the triple-quoted-string
  finding drafted Aug 19 (see that session's notes), including the
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
  New `## Key Lessons` entry logged (Azure-Search/RAG-specific
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

### Session — August 19, 2026

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

### Session — August 18, 2026

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

### Session — August 17, 2026

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

### Session — August 14, 2026

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

### Session — August 12, 2026

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
- New `## Key Lessons` entry added: classic `AzureOpenAI` vs. v1 GA
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

### Session — August 11, 2026

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
  7 and Aug 10 session notes as if it already existed; it didn't.
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

### Session — August 10, 2026

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

## Appendix — carried-forward "Next action" prose (Aug 12–20), superseded

This is what `## Next action` had accreted before the Aug 21 entry: running
commentary on `m5_index.py` written across Aug 12–18 and never trimmed once
the work closed. Kept verbatim because deleting a record to tidy it is the
wrong trade.

**One rule inside it is superseded — do not act on it.** The Aug 10/11
working-style rule below ("for core-Python-shaped work, keep attempting
independently first, capped at 15-20 minutes") is contradicted by the project's
own custom instructions, which now read "Claude writes implementation code by
default... I own: prompt and clause wordings, design decisions, review and
verification, and the Azure/CLI work." **The custom instructions are the
current rule.** Flagged 2026-09-06; the older text is left in place because
this appendix is a record of what was true then, not a set of live
instructions. The *format* guidance in it — narrate the data flow in plain
English before showing syntax, and show the long-form version of a new idiom
beside the shorthand — was never superseded and is still how a walkthrough
should read.

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
Milestones table, M5 also requires a retrieval/query script — the
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
IntelliSense-suggestion comparison, in the Aug 12 session notes.

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
failed, in the Aug 14 session notes.

`chunk_by_section()` fully closed Aug 17 — signature-block split written,
debugged through two real iterations (a missed write-back, then a dict-
aliasing misunderstanding that happened to be harmless), and verified
live against the real document: 16 chunks, XV clean, signature block
intact in its own chunk. A same-day stale-import false alarm (fix looked
broken, wasn't — a persistent session hadn't re-imported the edited
module) is logged in full in the Aug 17 session notes, with a new
`python-patterns.md` entry so it's recognized faster next time.

`upload_chunks()` and `main()`'s closing verification both closed Aug
18 — full detail, including the eventual-consistency false alarm and
the "loop and a half" retry-loop design, in the Aug 18 session notes
and the "Key Lessons" entry on Azure Search's push-API consistency
model.

**M5 is done — both halves built and verified live.** Full history in
the Aug 18 through Aug 20 session notes; short version: `m5_index.py`
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

---

## Archived sessions

July 27 – August 7, 2026 — the M2–M6 build, all milestones complete — lives in
`STATUS-archive-phase1.md` in this same folder. Split out 2026-09-06 to keep this
file to the live milestone. Same repo, nothing lost; open it when you need the
history behind M2–M6.
