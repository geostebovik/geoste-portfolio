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
were split into `STATUS-archive-phase1.md` in this same folder. Sessions from
August 10 through September 16 (the M7 era) were split into
`STATUS-archive-m7.md` on 2026-09-24, moved verbatim.

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

**Status as of:** September 24, 2026. Phase 1 of the IIP labs is closed: M7
passed its acceptance test at `a915217` (`results/20260915-184006`, 120/120 text
and 120/120 audit rows). Phase 2's M8, M9 and M10 are complete (Sep 21-23). For
which milestone is current, read the marker at the top of
`phase2-orientation.md` — that line is the single source of truth. The M7
write-up waits on outside readers and goes out in one group push with the Phase
2 write-up and the two stale ostebovik.net lines.
*(Replaced 2026-09-24, housecleaning — Claude drafted, at Gerard's request.
The previous paragraph was dated Sep 16 and predated M8-M10. Its M7 detail —
the item3 colour flaw moving from `[observed]` to `[content]`, 40/45 then
34/45 — is in the Sep 16 session entry and the Todoist task that accepts it as
a stated limit.)*
---

## Current next action

**Next action: row 15 stage 2 (one custom role), then M11 pass 2, sign-in.**
Updated 2026-09-25, end of session, at the HEAD this entry's commit creates.
M11 is the working milestone. Row 16 is verified. Row 15's failure-path
defect was found and fixed (stage 1). See the Sep 25 session entry.

1. **Row 15 stage 2 (about 45 min, plus a long wait).** Expand **IIP Queue
   Trigger (dev)** in `modules/rbac.bicep` to Action `queues/read` + dataActions
   `messages/read`, `messages/process/action` and `messages/write`, which is the
   union of the two built-ins and the custom role. Then remove
   `functionQueueReader`/`functionQueueProcessor` from the Bicep. **ORDER MATTERS:**
   deploy the expanded role first and **confirm it's effective** (the stage 1
   assignment took 65+ min). Only then delete the two built-in assignments by
   hand (Incremental mode never deletes), or the trigger may lose read/process
   for as long as propagation takes. Re-test with the confirmed-pause method
   (`m11-prep.md`, row 16 caveat). Also check that scale-from-zero still works:
   `queues/read` is Get Queue Metadata.
2. **`what-if` register (about 30 min).** The Sep 25 what-if showed 8
   unregistered diffs (listed in the Sep 25 entry). Register the read-back gaps.
   Declare `stiipdevwus02/blobServices/default` `deleteRetentionPolicy` and the
   `app-package-…` container's encryption-scope properties as found, in their
   own change. Unsupported diagnostics are now **13** (12 + the stage 1 assignment).
3. **M11 pass 2, sign-in (1-2 sessions).** The app registration **IIP Results
   (dev)**, the viewers group, built-in authentication on
   `func-iip-dev-wus-01`, and `id-iip-dev-wus-03` as a federated credential
   (D-M11-2 (b), row 17); plus an HTTP function for the results page. M11's
   done-when needs "a group member can sign in and see it".
4. **Small follow-ups from pass 1:**
   - deployed-package provenance (the Function records no git; record the
     package or deployment instead);
   - `WEBSITE_INSTANCE_ID` is empty on Flex, so find the right instance field;
   - the Azure SDK's HTTP logging fills `AppTraces` at Information on every call,
     so trim it.
5. **Gerard's steps:**
   - add the custom role **IIP Queue Trigger (dev)** (`d28c60b2-…`) and RBAC
     row 18 to the project instructions' resource notes;
   - if `m7-writeup-draft.md` is with outside readers, send them the Sep 23
     section 4 change.
6. **Small, any time:** make D1 accurate; the `__main__`-guard refactor for
   `m6_generate.py`, `m6_probe.py` and `m6_evaluate.py`; `.gitattributes` for
   `.gitignore`; the token-undercount backlog item (Friday check-in).

**Settled — do not reopen:**
- The `listKeys` calls are VS Code's.
- item7's judged row is a rate, flagged at 9 of 15.
- M3's `--blob` uses a user-delegation SAS.
- Trigger: Event Grid → queue, delivered with the topic's identity; row 14 at
  ACCOUNT scope (Event Grid checks the account when it creates a subscription).
- Sign-in: a managed identity as a federated credential.
- Python 3.14, remote build.
- `versionUpgradeOption` = `OnceCurrentVersionExpired`.
- One agent per upload; topic as blob metadata.
- Event Grid writes base64 JSON to the queue.
- **Row 16 works** (poison after `maxDequeueCount` 2; verified 2026-09-25).
- **Update Message needs `messages/write`**, which neither built-in in row 15
  has. Proven by a probe and a negative control, 2026-09-25.
- **Row 15's final shape: one custom role** (Gerard, 2026-09-25), not the
  built-in Contributor.

Still open and unchanged: the M7 write-up waits on outside readers (Gerard's
step), and goes out in one group push with Phase 2 and the two stale site lines.

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
- [x] **M7:** Build a single orchestrator agent (Generative AI/agentic exam
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
  **Complete: acceptance test passed at `a915217`** (`results/20260915-184006`,
  120/120 text rows, 120/120 audit rows). Phase 1 of the IIP labs is closed.
  *(Updated 2026-09-24, housecleaning: until today this entry still read "Not
  built yet", unticked, from Aug 21.)*

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
| Chat deployments | `gpt-5-2` (Content Understanding analyzer; 30K TPM) · **`gpt-5-4-mini` — decided M5 RAG/Q&A model** (Aug 6: quality parity + ~3x cost advantage over `gpt-5-4`, full evidence in the Aug 6 session notes, `STATUS-archive-phase1.md`); M7's CV audit model; 300K TPM · `gpt-5-4` — not chosen for M5, but M7's orchestrator and judge (Sep 9); 300K TPM. All GlobalStandard. TPM raised from 30K on 2026-09-16 |
| Embedding deployment | `text-embedding-3-small` |
| Analyzer | `iip_loan_agreement_analyzer` (`ai-103/infrastructure/content-understanding/loan-agreement-analyzer.json`) |
| AI Search service | `srch-iip-dev-wus-01` (Free tier, West US) — `https://srch-iip-dev-wus-01.search.windows.net`, provisioned Aug 7 for M5 |
| Managed identities | `id-iip-dev-wus-01` (Function runtime) and `id-iip-dev-wus-02` (GitHub Actions deploy, OIDC) — deployed by M9, 2026-09-21. `id-iip-dev-wus-03` (sign-in federated credential, D-M11-2 (b)) is planned, not deployed |
| App data containers | `uploads` and `results` on `stiipdevwus01` — deployed by M9, 2026-09-21 |

---

## Key Lessons

**`az role assignment list -o table`'s Principal column is NOT the principal
ID** (added 2026-09-22). For a *user* it prints the UPN — obviously not an ID,
so nobody transcribes it. For a **managed identity** it prints the **appId**, a
bare GUID that looks exactly like a principal ID and is not one. The one case
where the value is wrong is the one case where it is plausible. Query
`principalId` explicitly:
`--query "[].{principalId:principalId, role:roleDefinitionName}"`.
Verified on `aif-dev-wus-01`: `id-iip-dev-wus-01` is principal
`3b6695b3-f1d7-40f9-b21a-5158e6f71739` (shown as `efc6dd4a-…`);
`proj-iip-dev-wus-01` is `39bed562-c0ca-4acb-9d18-8400e806b824` (shown as
`98ee20de-…`).

**Cognitive Services User is a LEGACY role; Foundry User supersedes it** (added
2026-09-22). The Image Analysis / Vision docs still name Cognitive Services
User as the Entra prerequisite. Microsoft Learn's current Foundry RBAC page
lists it as "legacy Azure AI Services role" and Foundry User as the
Foundry-native replacement. Reaching for it assigns a deprecated role.

**Foundry RBAC role NAMES are mid-rename — key on the GUID** (added
2026-09-22). Foundry User / Owner / Account Owner / Project Manager were
previously Azure AI User / Owner / Account Owner / Project Manager. Microsoft's
own guidance is to use the role definition ID in code while the rename rolls
out. Foundry User = `53ca6127-db72-4b80-b1b0-d745d6d5456d`. Role IDs and
permissions are unchanged by the rename; only the display name moves.

**Keyless code is not the same as keys being unavailable** (added 2026-09-22).
Foundry User's `actions` include
`Microsoft.CognitiveServices/accounts/listkeys/action`, and its `dataActions`
are the wildcard `Microsoft.CognitiveServices/*`. An identity granted Foundry
User *in order to stop using keys* can still retrieve them. `disableLocalAuth`
is the control that closes it.

**Azure AI Search free tier: inbound Entra auth works, outbound managed
identity does not** (added 2026-09-22). Learn contradicts itself across five
pages. Measured: a `SearchClient` query with `DefaultAzureCredential` succeeds
on the free tier with Search Index Data Reader assigned. The "billable tier"
prerequisite applies to the *service* holding a managed identity (for indexers
reaching storage), not to clients authenticating to it.

**An RBAC test with no role assigned is not a test of anything else** (added
2026-09-22). 403 means "identity lacks the role" (up to 10 min to propagate);
401 means "RBAC not enabled on the service". A probe designed to answer "does
this tier support keyless?" returns 403 when the answer is really "you have no
role", and that misreading pointed at a paid-tier service recreate. Assign the
role, wait, then measure.

**`AzureOpenAIModelConfiguration` accepts keys its validator rejects** (added
2026-09-22). Introspection shows `credential` among its accepted fields;
passing it fails with `Model config validation failed` (MISSING_FIELD /
USER_ERROR). The working keyless form is to **omit `api_key`**. Accepting a
field and validating it are not the same thing, and introspection cannot tell
you which you have.


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

### Session — September 25, 2026 — row 16 verified; row 15's failure path found broken and fixed

**Claude wrote every doc edit and the Bicep in this entry, and did the analysis
and test design, except where a design is credited to Gerard below. Gerard
made every decision named below, ran every Azure CLI command and deployment,
and caught two of the problems himself: the what-if's unregistered diffs, and
the empty peek before R2.** Two app-side disconnects before 10:15 lost the
first run's questions and answers. The session restarted from the handoff, and
decisions were asked in plain text from then on. Claude kept running notes in
`Claude outputs/2026-09-25-session-notes.md` (gitignored).

**Housekeeping.** The VS Code "Initialize Azure Functions project" prompt
appeared because `40f9199` added `function/host.json`. Gerard dismissed it;
`.vscode/` is gitignored, and initializing would add a second, untested deploy
path. The previous entry's step 4 (project-instruction key files) was already
done.

**Row 16 verified.** The method is Gerard's upload-then-delete idea. Claude
added pausing the Function (`AzureWebJobs.process_upload.Disabled`), which
removes the race. A real Event Grid message named a deleted blob, and
`get_blob_properties()` raised on both tries. The host logged the move to
`upload-events-poison`, and the message was peeked there. Two tries, not the
row's "five": five is the runtime default, and `host.json` says 2. The test
needed **row 18** (Gerard: Storage Queue Data Reader on both queues, CLI, not in
Bicep; kept as an operator role). Model cost $0 throughout. **Method caveat:**
confirm the pause with `appsettings list` about 2 min before uploading. One
re-test didn't, and was voided.

**Found: a failed message couldn't be released.** Failed tries retried after
**10 min, not 1**, each time with a 403 `AuthorizationPermissionMismatch` from the
queue service. The stack trace (`QueueProcessor.ReleaseMessageAsync` →
`QueueClient.UpdateMessageAsync`) identified Update Message. Microsoft's
permissions table maps it to `messages/write`, which row 15's documented
minimum (Reader + Message Processor) lacks. There's a latent risk too: the
listener renews visibility every 5 min during a run with the same call, so a
run over ~10 min could be processed twice.

**The fix, and a detour.** Gerard chose a custom role (option a) over the
built-in Contributor, ending as one role reached in two stages ("A then R",
his reasoning: cleaner, one point of change). Stage 1, **IIP Queue Trigger
(dev)** with `messages/write` only, was deployed as
`m11-row15-stage1-20260925`. The re-test **still got 403, 65 min after
assignment.** A temporary built-in Contributor fixed it within ~20 min, which
pointed at the custom role. A probe on Gerard's own identity (poison queue,
`az storage message get`/`update`) showed the custom role **works**: update
allowed with it, refused without it (a negative control, run in plain text at
Gerard's option 1). With Contributor removed, the Function passed at 20:14Z
(inconclusive: only 6 min after the removal) and **cleanly at 21:00:28Z: no 403,
retry at +100 s.** **The 65-min delay is open:** a slow custom-role assignment
for a managed identity, or a permission refresh triggered by the Contributor
add and remove. It's recorded both ways; not claimed either way.

**Claude's errors today, for the record:**
- Called row 8 "unproven"; it was confirmed on Sep 24, and today's check was a
  re-check.
- Two "Expected" outputs were wrong (`role assignment create` doesn't return
  the role name; `appsettings set` hides values).
- The first 403 diagnosis was right about *what*, but the fix had to be proven.
- Probe P0 had no negative control until N1.
- One verdict query started after try 1, and missed it.
- The upload came too soon after a pause (the voided run).

**What-if, first since the M11 deploy.** The stage 1 what-if showed the create
and 13 Unsupported, as expected. It also showed **8 unregistered diffs**, none
from today's change:
- `appi-…` `+Flow_Type`/`+Request_Source`;
- `func-…` `+siteConfig` ×3, and `~deployment.storage.value` (literal vs
  `reference()`);
- `func-…/config/appsettings` `+` block;
- `stiipdevwus02/blobServices/default` `-deleteRetentionPolicy`;
- the `app-package-…` container `-defaultEncryptionScope`/`-denyEncryptionScopeOverride`.

The last two are the writable class, to be declared as found. Next action, item 2.

**Cleaned up:** the temporary Contributor on the Function (removed ~20:08Z);
Gerard's temporary Message Processor and custom role on the poison queue.
**Left in place:** 6 test messages in `upload-events-poison` (17:41:38Z to
21:02:08Z), which expire 2026-10-02; one "missing topic" result, `results/row16-retest5/20260925T203810Z.json`.

### Session — September 24, 2026 — housecleaning, then M11 pass 1 built, deployed and working end to end

**Claude wrote every doc edit, all the code and all the Bicep in this entry, and
ran the offline checks. Gerard made every decision named below, and ran every
Azure CLI command, commit and deployment.**

**Housecleaning, first.** Stale lines found and fixed:
- STATUS.md's Sep 16 status paragraph, M7 still unticked, and a Key resources
  table missing M9;
- phase2-orientation.md's M10 bullets, the M11/M12 table rows, the backlog
  header and the doc table;
- m7-orientation.md's checklist item 7;
- in Todoist: 3 tasks closed and 4 annotated.

Gerard's project-instruction edits (key files, the M9 identities) were handed
to him. Commit `a184630`.

**`versionUpgradeOption`: decided and deployed.** `OnceCurrentVersionExpired` on
all four deployments, now set per deployment (Gerard). It's a fourth option the
original task had missed. The first `what-if` exposed three unregistered but
writable storage properties, which were declared as found. Verified afterwards:
gpt-5-4 is still on `2026-03-05`, and the `what-if` shows the register only.
Commit `c923daa`.

**M11 decisions (Gerard):**
- remote build first;
- Python 3.14;
- the event queue on `stiipdevwus01`, with queue-scoped Function roles;
- the poison queue declared in Bicep, with Message Sender on it only;
- the topic carried as blob metadata;
- one agent per upload (D-M11-3);
- row 14 moved to account scope (below).

**M11 pass 1 (upload → result), built and working:**
- `function/` holds the code (`b713df9`), with the Function's requirements
  fully pinned to Gerard's venv (`577bad3`).
- One change to certified code: `expected_audit` is now optional (own commit, `97038fb`).
- A live laptop run of the handler matched item4's key.
- The Bicep adds `app.bicep`, `eventsub.bicep`, the two queues, and RBAC rows 7,
  8, 12 and 14–16, all priced first.

**Row 14 needed account scope.** The event subscription failed 3/3 over about
20 minutes with "Managed Identity Authorization Error". The queue-scoped grant
existed; Gerard confirmed it with `az role assignment list`. Hypothesis (Claude):
Event Grid checks the identity when it creates the subscription, against the
destination's `resourceId`, which is the account; Microsoft Learn also says "on
the storage account". Gerard approved widening the role. The redeploy succeeded
first time, and the orphaned queue-scoped grant was deleted. Recorded in
`rbac.bicep` and the RBAC model.

**First light:** upload → Event Grid → queue → Function → agent → result in
**46 s**, cold start included. The remote build succeeded first time. Both
Azure runs matched item4's key (run 2 on the committed code, `2ac2c34` +
`40f9199`). Settled by evidence:
- **Event Grid writes base64 JSON** to the queue.
- Rows 4, 5, 6, 7 and 15 are confirmed. Row 7 needs **no** Queue Data
  Contributor.

**Defect found in the Function's first result, fixed in its own commit
(`2ac2c34`):** `provenance.py` recorded `git_dirty: false` where git doesn't
exist. It now records None plus a reason. Laptop records are unchanged.

**Row 8 confirmed.** The Entra-only App Insights received 491 traces and 2
requests in 3 h. One `ConnectionAbortedException` at 19:07:19Z has no operation
name and falls 4 minutes before the first upload, inside the deploy window:
likely host noise at deploy time (an inference from the timing, not a traced
cause). Claude's `-o table` in the first query printed nothing even though rows
existed, and `-o json` showed them.

**STATUS.md split:** Aug 10 – Sep 16 moved verbatim to `STATUS-archive-m7.md`
(hash-checked). The file went from 5,527 lines to about 1,040.

**Claude errors this session:**
1. Ended a turn on a status message with two questions buried in its prose.
   Gerard had to prompt a restart, and the rule is now "question tool, or
   WAITING ON YOU".
2. Wrote that D-M11-1 (b) "dissolved" the M12 inbound question. It moved the
   question to the storage account; corrected the same turn.
3. Said to drop `python-dotenv` from the Function. Six modules import it;
   corrected before any deploy.
4. Timed "3.14" on a 3.14.0 release candidate without noticing; re-measured on
   3.14.7.
5. Wrote row 14 at queue scope, which cost three failed deploys and about 20
   minutes.
6. Gave `-o table` for an App Insights query. Its nested output printed
   nothing, and briefly looked like "no telemetry".

### Session — September 23, 2026 — the `listKeys` caller named, the judge test-retest, item7 becomes a rate, and M10 closed

**Claude drafted this entry and every doc edit in it, and proposed the VS Code
hypothesis (Sep 22). Gerard ran every Azure CLI command, supplied the Sep 22
evidence from the previous chat, and caught that the handoff never reached the
repo.**

**The session opened on a process failure.** Sep 22 closed with a "threads for
next time" list that lived only in the chat's closing summary. `## Current next
action` was not replaced after the day's last commit, so it still said "read
the acceptance run", and nothing from the late Sep 22 work was in this log
(now bracketed onto the Sep 22 entry). A new session reads the repo, not the
last chat: it rebuilt the agenda from stale docs and re-questioned a finding
Gerard had already settled. The same summary gave HEAD as `5498ece`; the real
hash is `5798ece` — typed, not copied. New end-of-session rule in
`m7-orientation.md`: the closing summary is derived *from* `## Current next
action`, and hashes are copied from `git log -1 --oneline`.

**The `listKeys` caller is Visual Studio Code.** Evidence, strongest first:
- **appid.** Every `Microsoft.CognitiveServices/accounts/listKeys/action` row in
  a 2-day window carries `claims.appid` `aebc6443-996d-45c2-90f0-388ff96faa56`,
  which Microsoft Learn's first-party app list names as Visual Studio Code;
  caller Gerard's account. (`az ad sp show` finds no service principal for it:
  VS Code is a Microsoft client with none in the tenant. Expected.)
- **Cadence.** Sep 22 baseline: calls arrive in pairs a fraction of a second
  apart, on a fixed 14m42s timer (20:19:37, 20:34:18, 20:49:00, 21:03:42 UTC).
  Not a person, not event-driven.
- **Shutdown.** VS Code closed ~21:35 UTC Sep 22; a query afterwards returned
  nothing. VS Code was not reopened until after attribution on Sep 23.
- **Not determined: which extension.** The Activity Log sees the VS Code client
  ID, which every Azure extension signs in with.
- Also in the window: two `Microsoft.Search/searchServices/listAdminKeys/action`
  rows, appid `c44b4083-…` (Azure Portal) — the portal loading Search pages,
  the same pattern as the Sep 16 note. Benign.

**What it changes** (both now in the `disableLocalAuth` backlog entry):
turning local auth off at M11 has two known breakages, this poll and
`m3_analyze.py`'s exempted pipeline; and the poll leaves `listKeys` with no
audit value, since roughly eight retrievals an hour under Gerard's own identity
hide any genuine one.

**THREAD 2 — the judge test-retest. Pre-registered in Todoist 10:02 MST,
before any data (Claude proposed; Gerard approved and raised n from 20 to 40).**

*The reframe that shaped it (Claude, from existing data):* Sep 9's "gpt-5-4
groundedness 4.0 x10, no variance" was test-retest on ONE fixed text; Sep 22's
two 2.0s were on DIFFERENT drafts, so they could not contradict it. But two
Sep 22 first drafts differing by one clause (runs 1 and 13) had scored 4.0 and
2.0, and across all 39 item7 judge calls in that pass groundedness was 4.0 x32,
2.0 x4, 1.0 x3. So the question became: is gpt-5-4 stable on a fixed text?

*Instrument:* `probe_judge_isolation.py`, judge gpt-5-4, build `2026-03-05`
recorded in every file (`model_builds`, added at `ba54311`), n=40 per text,
all at `ba54311` with a clean tree, 200/200 calls measured, 0 errored.

| Text | Source | Originally | Groundedness x40 | Relevance x40 | all_passed |
|---|---|---|---|---|---|
| A | `20260909-122233` item7 run 1 d1 | 4.0 x10 (Sep 9, gpt-5-4) | 4.0 x38, 2.0 x2 | 1.0 x20, 2.0 x20 | 0/40 |
| B | `20260922-131551` item7 run 13 d1 | 2.0 | 4.0 x38, 2.0 x2 | 2.0 x32, 3.0 x8 | 8/40 |
| C | `20260922-131551` item7 run 15 d1 | 2.0 | 4.0 x29, 2.0 x11 | 2.0 x17, 3.0 x23 | 17/40 |
| D | `20260922-131551` item7 run 1 d1 | 4.0 | 4.0 x37, 2.0 x3 | 2.0 x25, 3.0 x15 | 14/40 |
| E | `20260922-131551` item7 run 2 d2 | 1.0 | 1.0 x23, 2.0 x5, 4.0 x12 | 1.0 x40 | 0/40 |

Files: `20260923-101620`, `-102419`, `-103341`, `-105824`, `-110516`
`_judge_isolation.json`, in that order.

**Verdict, by the pre-registered rule: R2 and R3 both fired.** Every text drew
at least two distinct groundedness scores. Claude predicted R2 with A stable:
B and D unstable was right, A stable was wrong.

**What it means:**
1. **The judge CHOICE stands; two claims about it narrow.** On text A gpt-5-2
   scored 1.0 in 8 of 10 (Sep 9) and gpt-5-4 scores 4.0 in 38 of 40 — still
   clearly the most faithful of the three. But "no variance" and "applies the
   definition on every call" were n=10 artifacts: a 1-in-20 wobble is invisible
   in 10 reads about 60% of the time. Sep 9 was not wrong; it could not see this.
2. **item7's judged verdict is a rate, not a property.** One unchanged draft
   passes 0 to 17 of 40 re-reads depending on its wording. Sep 22's 3/15 (and
   B's 2.0) are fully explained by judge variance on fixed text; no change in
   agent behaviour is needed to explain them. The Sep 11 revisit trigger was
   the judge, not the agent.
   **[Corrected same day, after `4d52012` — the last two sentences overclaim.**
   The agent's draft mix moved too. Counting item7 first drafts that raise
   returns or pricing (regex `bring something back|pricing|better price|return`,
   chosen by Claude AFTER seeing the data, so exploratory, not pre-registered):
   Sep 10 2/15, Sep 11 0/15, Sep 15 5/15, Sep 22 9/15. Across all four passes,
   those drafts passed first time 4 of 16; drafts without it, 0 of 44 — matching
   text A's 0/40 and B–D's 8–17/40. So a first-draft pass needs BOTH a draft
   that raises the topic (the agent's variance) AND a favourable read (the
   judge's). Sep 22's 3/15 is what nine such drafts at ~25–30% produce. Neither
   factor alone explains it.**]**
3. **On an unanswerable query, groundedness imports relevance.** E is the one
   draft that makes no unsupported claim — it describes what the store does
   offer — and it draws gpt-5-4's LOWEST groundedness: 1.0 in 23 of 40, and 22
   of those 23 reasons say "not responsive", "unrelated" or "irrelevant" (the
   23rd says it "does not answer" the query). Both of A's 2.0 reads
   say "off-target relative to the query". The failure Sep 9 attributed to
   gpt-5-2 is present in gpt-5-4 at a lower, text-dependent rate.

**Decision (a), Gerard:** item7's judged first-draft row is reported as a rate,
not scored against the answer key; its deterministic rows stay pass/fail. Not
circular in the way re-keying from the Sep 22 run would have been: the evidence
is this pre-registered fixed-text measurement, with no agent in the loop.

**Decision (a) implemented (afternoon).** `m7_orchestrator.py`: item7's key
gains `mode: "rate"`, `first_pass_flag_at: 9`, `flag_defined_for_runs: 15`; for
a rate item `text_matches_expected` is None (not asserted) and the per-run line
says so. `probe_orchestrator_stability.py`: `summarize()` prints and records a
`rate_item` block — count, threshold, whether the flag applies and whether it
fired. The original first_pass/final_passed/redrafts keys are kept as the
registered expectation, unasserted. **Gerard chose the threshold** (9 of 15) from
three offered. Claude wrote the code; `summarize()` was checked offline against
the Sep 22 file (3/15 within range; a forced 10/15 flags; a 7-run batch reports
"not evaluated"). Known wart, left alone: the pre-existing STABLE/NOT STABLE
label still prints for item7 and means only "80% of runs agreed", which for a
rate item says nothing.

**Smoke of the rate code (live, one run):** `20260923-115337_orchestrator_stability.json`
at `287d740`, clean tree, build `2026-03-05`. The record carries the rate key
with `text_matches_expected: None`; the summary's `rate_item` reads
`flag_applies: False` for a 1-run batch. Both code paths confirmed.

**THREAD 3 — M3's migration, and M10 closed.**
- **Service auth** (`fcc55b6`): `submit_analyze()` and `poll_result()` send an
  Entra ID bearer token for `cognitiveservices.azure.com/.default` — the scope
  the Content Understanding 2025-11-01 REST reference names — refreshed per
  request. The module docstring's old claim that Entra ID "doesn't apply" on a
  laptop was corrected: it conflated managed identity with Entra ID.
- **`--blob`: decision (A), Gerard** — a user-delegation SAS
  (`--as-user --auth-mode login`), chosen over downloading and sending inline.
  **Claude's reading found the Todoist task wrong on one point:** it did NOT
  amend the RBAC model — Gerard already held Storage Blob Delegator and Storage
  Blob Data Contributor on `stiipdevwus01`. Letting the Foundry account's own
  identity read the blob was ruled out: no Microsoft documentation shows it for
  Content Understanding.
- **Verified live on both paths:** `20260923-121256` (`--file`) and
  `20260923-121335` (`--blob`) against the July 27 key-based run: all 21
  non-generative extracted values identical, markdown identical in length
  (4,186 characters). Only the 11 model-written KeyPhrases differ, in wording
  — and today's two keyless runs differ from EACH OTHER in 2 of them, so that
  is generation variance, not auth.
- **M10 clause 1** (`08bc35c`, own commit): `get_subscription_key()`,
  `get_storage_key()` and `get_search_admin_key()` removed with dead imports in
  nine scripts. Import check on the eight import-safe modules passed.
  Gitignored `m6_probe.py` fixed to match; gitignored `tester3.py` left broken.
- **M10 clause 2:** `m6_generate.py` hand-run (`20260923-122420_generate_results.json`,
  28 answers, 14 per model, none empty) and `m6_probe.py` hand-run — both keyless.
- **M10 COMPLETE. Gerard moved the marker to M11.** Every clause of the
  done-when is met and M3's stated exception is closed.

Claude wrote all the code and doc changes in thread 3. Gerard chose (A), ran
every command, and made the milestone call.

**M11 PREP — the survey, started the same afternoon (`m11-prep.md`, `390eb55`).**
Claude surveyed the M7 code paths and Microsoft Learn; nothing was built.
- **Headline: the M7 code assumes a laptop.** `get_endpoint()` shelled out to
  `az`, and `m7_evaluator_tool.py` calls it at module scope — so importing the
  evaluator in a Function would fail while the host loads. **Fixed at
  `71b90b9`:** an `AIF_ENDPOINT` setting wins; `az` is the fallback. Verified
  with a deliberately bogus account name (no `az` error) and a live `m6_probe`.
- **Two keys hiding in the textbook design** — the blob trigger's
  `blobs_extension` webhook key and Easy Auth's client secret. **Gerard chose
  the keyless alternative for both:** D-M11-1 (b) Event Grid → storage queue →
  queue trigger (no inbound endpoint; the M12 inbound-restriction question
  dissolves); D-M11-2 (b) a dedicated `id-iip-dev-wus-03` as a federated
  credential on the app registration.
- **Probes (Gerard ran all three):** `westus` supports Flex Consumption, with
  Python 3.10–3.14; `import m7_orchestrator` takes **4.57 s** on the laptop
  (`openai` 2.07 s, `azure.ai.evaluation` 1.51 s) against a 30 s ceiling; the
  dependencies install to **235 MB**. Sizing that surfaced the real risk:
  remote build has a documented **60-second** timeout.
- **Claude error:** drafted a placeholder where a commit hash belonged in
  `m11-prep.md`, the third hash slip of the day; caught before commit and
  replaced with `71b90b9` from `git log`.

Recorded as dated corrections in `m7-orientation.md` (two closed backlog
entries), `m7-writeup-draft.md` sections 4 and 5, `phase2-orientation.md`'s M10
bullet, and `m7_evaluator_tool.py`'s docstring (own commit). Cost ~780K tokens,
~$3 estimated.

**Claude errors this session:** (1) questioned the validity of the Sep 22
shutdown test without knowing it was Claude's own design and already settled; (2) attributed the `5498ece` hash to a typo of
Gerard's — it was in Claude's summary; (3) put a `<placeholder>` inside a
copy-paste command block, which Gerard ran as written; (4) said "eight" tracked
scripts import `get_subscription_key` unused — it is nine; (5) reported
text B's relevance as 3.0 x9 in the interim read — it is x8; (6) buried the
item7 decision inside an analysis instead of asking it as a question — Gerard
had to find it, and chose with less confidence than the decision deserved; (7) counted E's
"irrelevant" reasons as 16 of 23 with a substring match that also hit "offer"
— the correct count is 22 of 23; (8) typed a commit hash from memory into a
Todoist comment ("3de3…") hours after writing the rule against it — corrected
with the real `67d0e31`; (9) estimated m6_generate at 13 questions — it has 14.

### Session — September 22, 2026 — M10: the keyless migration, and four probes that reshaped it

**Claude wrote every probe, the migration script and all code changes in this
session. Gerard directed the work, ran every Azure CLI and Python command, made
the scope decisions, and caught the Cognitive Services User deprecation that
Claude had wrong.**

**Plan on entry:** housekeeping, then the two tests at the top of `m10-prep.md`
— Vision Read, then the Search token. Both ran, plus two more that the first
pass of review showed were needed.

**Before anything ran, five contradictions surfaced in the docs** — the M8
bullet contradicting the M9 bullet four lines above it, two verbatim duplicate
backlog entries, the M10 script count, an unsatisfiable backlog precondition,
and a test design that could not distinguish its own outcomes. All fixed the
same day; see `phase2-orientation.md`, `phase2-rbac-model-draft.md` and
`m10-prep.md`.

**The test-design problem was the important one.** `m10-prep.md`'s Group C test
said a 401/403 meant the free tier does not support keyless. But the RBAC model
deliberately assigns nothing on Search, so the run would have 403'd for a
missing role and been read as a tier limit — pointing M10 at a service recreate
on a paid tier, a one-way door with a recurring bill. Search Index Data Reader
was assigned first. That single change is what made the result mean anything.

**The subscription-scope Foundry User grant was removed BEFORE the probes, not
after.** The backlog said to remove it only after M10's acceptance test passed
"on the account-scope grant" — but the broad grant silently carries that test,
so the condition could never be met. Removing first (one reversible command)
put Gerard and `id-iip-dev-wus-01` on the same grant at the same scope, which
is what makes the results transfer to the Function.

**Results — four probes, all green:**
- **Vision Read:** Foundry User covers it. Row 4's first half closed.
- **AI Search, free tier:** keyless query works. `m10-prep.md`'s "PROBABLE
  BLOCKER" retired. The query was carried by Search Index Data Reader, a
  dataAction; Owner inheritance cannot have masked it because Owner has no
  dataActions. Step [3/3] (`get_index`) *did* ride Owner — Claude predicted it
  would fail, it passed, and the reason means it proves nothing about what a
  workload identity could do.
- **Evaluation SDK:** works with `api_key` omitted. Row 4's second half closed.
- **`/openai/v1/` audience:** both `cognitiveservices.azure.com` and
  `ai.azure.com` accepted; a callable works as `api_key`, so no expiry ceiling.

**Migration:** all 12 call sites keyless, committed at `aa96bea`.
`get_subscription_key()` and `get_search_admin_key()` deliberately kept and
unused until the acceptance test passes.

**Scope correction, twice over.** The plan said eleven scripts. `m10-prep.md`
corrected that to ten because `tester3.py` is gitignored. `m6_probe.py` is
gitignored on the same `.gitignore` line and was missed. **Nine tracked.**
It was migrated anyway.

**Two mistakes Claude made and corrected in-session, recorded because the
corrections are the useful part:**
1. Recommended assigning **Cognitive Services User** as the remedy if Vision
   Read 403'd. Gerard remembered it was deprecated. It is: Learn lists it as a
   legacy role superseded by Foundry User. Had the 403 happened, the RBAC model
   would now carry a deprecated role as a documented decision, in resume
   material.
2. Wrote `credential=DefaultAzureCredential()` into the two Evaluation SDK
   sites on an argument about explicitness, overriding the probe's own finding
   that `api_key` should simply be omitted. The SDK's validator rejected it and
   the smoke test caught it. The empirical result was right; the aesthetic
   argument was not.
   A third, smaller one: the first smoke test imported `m6_generate`, which
   runs a full generate loop at module scope. Caught before it ran.

**8x1 smoke before the long pass** (`20260922-114320`, `git_head aa96bea`,
`git_dirty false`): 8/8 deterministic audit rows and 8/8 judged text rows match
the answer key. 366 seconds for 8 item-runs — ~46s each, so the 15-run pass is
~92 min. That is **latency-bound, not TPM-bound**: the 300K TPM quota increase
does not shorten it, and the old ~95 min figure stands.

**THE ACCEPTANCE PASS — `20260922-131551_orchestrator_stability.json`.** 15 runs,
all eight items, 89.5 minutes, `git_head aa96bea`, INSTRUCTIONS_V4, temp 0.0,
judge and model both `gpt-5-4`.

- **Deterministic layer: 240/240.** Every audit row on every item on every run
  matches the key, including the three carrying the deliberate flaws (item3
  `text_legible`, item4 `brand_consistent`, item5 `info_accurate`). This is the
  layer that evidences the migration: it runs at temperature 0 / seed 42 through
  `m7_legibility_check.py` and `m7_cv_audit_tool.py`, the two files whose auth
  changed most.
- **Judged layer: 7 of 8 items at 15/15.** item7 came in at 12/15.
- **M10's acceptance test is CERTIFIED on this basis** (Gerard's call). The
  migration changed how calls authenticate and nothing about what they return.

**item7 at 12/15 is NOT a migration regression, and the Sep 11 punch list said
so in advance.** First-draft relevance across 15 runs:
`[3,2,1,2,3,2,1,2,1,1,2,3,2,2,3]` — four draws at 3.0, three of which passed
(run 15 drew relevance 3.0 and still failed on groundedness 2.0). The Sep 11
task recorded item7 recovering **once in 18 runs** and said explicitly: *"if a
future pass shows item7 recovering at a materially higher rate, revisit whether
it should be re-registered the way item6 was on Sep 9."* **1-in-18 then, 3-in-15
now. That trigger has fired.** The key was NOT changed on the strength of this
run — certifying a migration and rewriting the answer key it was judged against,
using the same run, is circular. Re-registration needs its own evidence and its
own decision. Logged in Todoist.

**A SECOND shift that nobody pre-registered: item7's groundedness moved.**
Values `[4,4,4,4,4,4,4,4,4,4,4,4,2,4,2]` — two 2.0 draws. The Sep 9
judge-isolation probe recorded item7 on gpt-5-4 as groundedness 4.0 x10, *"no
variance"*, and that was the evidence for choosing gpt-5-4 as judge at all.
Three candidates, cheapest first: (1) the judge deployment's model build changed
under us — check `versionUpgradeOption`, because if it is
`OnceNewDefaultVersionAvailable` the judge moves without anyone deciding, and
every longitudinal comparison in the M7 write-up is then comparing two judges;
(2) the 500s (below) injected retried samples; (3) real variance that n=10 on
one item never surfaced.

**Transient judge 500s, invisible to the results file.** At least one
`InternalServerError: The model produced invalid content` fired from
`azure.ai.evaluation._legacy.prompty` during run 2 and was retried internally by
the Evaluation SDK ([0/10], 3s backoff); the run completed with all three tools
called. **The probe cannot see these** — the retry happens below `unmeasured()`,
which only catches runs that complete without a verdict. The only trace is
terminal scrollback. A retried call is a fresh sample, so this is a plausible
contributor to the variance above and there is currently no way to count it.

**`stop_on_pass` STILL has zero observations** after another 120 item-runs. The
three item7 first-draft passes are not stop-on-pass — that needs a pass *after*
a failure. Unobserved now across 33+ runs.

**PROCESS FAILURE, Claude's: `git_changed_during_run: True`.** Claude proposed
doing the documentation pass while the 15-run measurement was in flight, and
that tripped the provenance guard built to prevent exactly this. `git_at_end`
records `.gitignore`, `STATUS.md`, `m10-prep.md`, `phase2-orientation.md`,
`phase2-rbac-model-draft.md` and the 8x1 results file as dirty at the end.
**The measurement stands, for a specific and checkable reason: not one `.py`
file is in that list** — nothing under `ai-103/scripts/` changed, and `git_head`
is identical at start and end, so the code that ran is byte-identical to
`aa96bea` throughout. Recorded rather than waved off, because the flag is
permanently in the results file and a reader deserves the reason. **Lesson: do
not touch the repo while a measured run is in flight, even documentation. The
guard cannot tell docs from code and should not have to.**

**Governance findings, both new and both in the Phase 2 backlog:** Foundry
User's dataAction is the wildcard `Microsoft.CognitiveServices/*`, and its
actions include `listkeys`. Keyless code does not remove the permission to
retrieve a key — `disableLocalAuth` does. And Principle 2 cannot be satisfied
for row 4 while one shared AIServices account serves both OpenAI and Vision;
that is now stated as an accepted trade-off rather than left implicit.

**[Added 2026-09-23 — late Sep 22 work that never reached this log.** Committed
at `5798ece`, after the entry above was written: (1) `provenance.deployment_builds()`
now records each deployment's model build and `versionUpgradeOption` at run
start; (2) the Activity Log shows no `Microsoft.CognitiveServices/accounts/deployments`
write between Sep 7 and Sep 21 from any caller, and the live build reads
`2026-03-05`, so the Sep 9, 10, 11, 15 and 22 runs are comparable; (3) M10's
done-when amended to name `m3_analyze.py`'s own pipeline as a stated exception.
Claude wrote the code and the amendment. Gerard directed the work, ran every
command, chose to amend the done-when rather than leave the milestone open, and
pushed back on certifying data whose provenance was in question — which is
what surfaced (1) and (2). The commit message has the full reasoning. Why this
bracket exists: see the Sep 23 entry.**]**


### Session — September 21, 2026 — M8: the IaC baseline, written and what-if'd

**M8's Bicep is written and builds warning-clean.** `what-if` reports 3
resources to modify and 6 no change, and every remaining diff is either
intended or a property no template can assert. The register of accepted diffs
is `infrastructure/iip/README.md`; it is the complete expected output, so
anything else in a future run is a real change.

Gerard ran every Azure CLI call — the property dump, three build/what-if
cycles. Claude wrote the Bicep, the README and this entry.

**Structure.** `infrastructure/iip/` — `main.bicep` (orchestrates only),
`dev.bicepparam`, and `modules/{storage,keyvault,search,foundry}.bicep`,
matching the portfolio prod stack's shape rather than inventing a second one.

**The finding worth keeping: `what-if`'s noise disclaimer hides real
changes.** The first run showed 7 resources to modify. Five of those diffs
looked exactly like provider noise — a `-` on a property reading like a status
field, on a resource nobody meant to touch — and were writable properties the
template had silently dropped:

| Property | Consequence had it deployed |
| --- | --- |
| `accounts/properties.defaultProject` | data-plane calls without an explicit project name break |
| `accounts/properties.associatedProjects` | `proj-iip-dev-wus-01` detached from the account |
| `deployments/properties.currentCapacity` (x4) | the 300K/30K/10K TPM settings cleared |
| `searchServices/properties.computeType` | the Default vs confidential-compute choice cleared |

**Nothing in the `what-if` output separated those from the two that really
were noise.** The only reliable test is the resource provider's schema: a
property with no `ReadOnly` flag is a property a deployment can clear. Read
`what-if`'s "may contain false positive predictions" banner as a reason to
check each line, not as a licence to dismiss them.

**A related error, made and corrected the same session.** `networkRuleSet.bypass`
on Search was dropped on the stated grounds that it existed only in preview API
versions. It does not — it is absent from `2023-11-01` and present and writable
in `2025-05-01`, which is GA. The module had been pinned to a stale API version
and the missing property was then rationalised as unsupported. Bumping the API
version was the fix. **A "the schema does not support it" conclusion should be
checked against the current API version before it is written down.**

**Three findings about the live resources the docs did not have:**

- **The Foundry subdomain inverts the documented naming exception.** The
  account resource is `aif-dev-wus-01`, without the `iip` token, which is the
  known exception. Its `customSubDomainName` is `aif-iip-dev-wus-01` — *with*
  the token — and that is what every endpoint in `scripts/` is built from. It
  is pinned in `dev.bicepparam`. Left to default it would change the endpoint
  host and break every script at once.
- **`srch-iip-dev-wus-01` was missing the `managed-by` tag** that the other
  four resources carry. The baseline applies the full tag set, so the one
  intended `what-if` change is `+ tags.managed-by`.
- **The `managed-by: bicep` tag has been asserting something untrue since
  July.** Four resources carried it while nothing in the resource group was in
  Bicep. M8 is what makes it true. Recorded rather than quietly fixed.

**Also this session, outside M8:**

- **The stale Claude project doc `claude/2026-09-10-m7-session-prompt.md` was
  deleted**, at Gerard's instruction. Its own rule — promote anything durable
  before replacing — was checked first: `first_text_passed` vs
  `final_text_passed`, judge-invariance, the Plan9 mount failure mode, the
  item6 answer-key trap, the four probe scripts and the redraft cap are all
  already in `m7-orientation.md` or this file. `ACTIVE_JUDGE_DEPLOYMENT` is
  documented at the constant in `m7_evaluator_tool.py`. Nothing lost.
- **The Sunday punch-list scheduled task was rewritten.** It still named
  `m7-orientation.md` as the source of truth and carried a standing assumption
  "He is on M7", so the Sep 20 run seeded all three tasks from the M7 backlog
  and M8 got no slot in the week it was the working milestone. It now reads
  `phase2-orientation.md` for core items and takes its single `[stretch]` item
  from the M7 backlog. Gerard decided the MS Learn video series stays paused
  through all of Phase 2, not merely until M7 was stable. The cache-buster
  warning, freshness gate, no-questions rule and attribution rule were kept
  verbatim.
- **There is no Friday check-in scheduled task.** Only the Sunday punch list
  and the mid-October job-search checkpoint exist. Noted, not acted on.

**Open, and it is a real decision:** M8's done-when in `phase2-orientation.md`
reads "`what-if` shows **no changes**". Azure will not produce that here, for
the reasons in the register. Claude proposed amending it to "no changes other
than the documented provider-owned properties listed in
`infrastructure/iip/README.md`". Not yet decided — it is the standard M9-M14
inherit.

### Session — September 21, 2026 (afternoon) — M9: identities and RBAC, first real deployment

**M9 is complete, and it was the first time any of this left the template.**
Deployment `m9-identity-rbac` succeeded in 39 seconds. Gerard ran every Azure
CLI call; Claude wrote the Bicep, the verification queries and this entry.

**Created:** `id-iip-dev-wus-01` (purpose `function-runtime`) and
`id-iip-dev-wus-02` (`github-deploy`), the `uploads` and `results` containers,
and RBAC rows 2, 4, 5, 6 and 9. All five verified afterwards with
`az role assignment list` — rows 5 and 6 at **container** scope, not account
scope, as the model's principle 2 requires.

**M9's done-when was wrong as written, and was amended before any code.** It
said "the assignments exist and match the RBAC table." Eight of the table's
twelve rows cannot be assigned until M11 creates their scope resources. Gerard
chose to scope M9 to the identities plus every row whose scope exists — the same
correction made to M8's done-when earlier the same day.

**Four corrections to the RBAC model, found by checking before writing.** Full
detail is in `phase2-rbac-model-draft.md`'s new build-time findings section. The
one that matters:

- **Row 9 was marked "(automatic)" and is not.** The Foundry account had zero
  direct role assignments. Microsoft Learn: the automatic Foundry User
  assignment happens only via the portal or Foundry UI, and "doesn't apply when
  deploying Foundry from SDK or CLI". So the project managed identity had been
  running since July without one of the two assignments Microsoft documents as
  the minimum. **M10 would have hit this**, because the keyless migration removes
  the account keys that were concealing it.
- **Row 3 already existed** and is deliberately not in the template: Azure
  enforces uniqueness on the (principal, role, scope) triple, so declaring it
  would have failed the deployment with `RoleAssignmentExists` partway through.
- **Row 2 is redundant today** — Gerard holds Foundry User at subscription
  scope, which is how `m7_orchestrator.py` authenticates. Declared anyway, so
  the narrow grant is in IaC; removing the broad one is backlogged until after
  M10.

**M8 is now tested, not predicted.** The deployment applied the baseline without
recreating anything — the Foundry account and project principal IDs are
unchanged from the morning's dump — and the pinned `customSubDomainName` held,
so `https://aif-iip-dev-wus-01...` is intact. The `managed-by` tag applied to
`srch-iip-dev-wus-01`, which was M8's one intended diff.

**The `properties.endpoint` question is settled empirically.** It was left
undeclared on Search on the reasoning that a search endpoint is derived rather
than settable. The deployment left it unchanged, so the missing `ReadOnly` flag
is a schema inaccuracy. Recorded in the register with the reasoning, because the
method generalises: when a property's writability is ambiguous, prefer the error
that self-corrects.

**One more instance of the same mistake, caught by what-if.** `blobServices/default`
was declared with no properties, purely as a parent for the containers, and
`deleteRetentionPolicy` is writable — the third time in one day that a writable
property left undeclared produced a real diff. Now declared as found. The
standing rule: **declare every writable property you found a value for, or
expect what-if to report it every run.**

**`Unsupported` is not `-`.** what-if reported rows 4, 5, 6 and 9 as
`Unsupported`, naming the cause: the resource ID "cannot be calculated until the
deployment is under way", because each contains `reference(...).principalId` for
an identity the same template creates. Row 2 analysed cleanly — its principal ID
is a literal parameter. Same type, same file, same run: the only difference is
literal versus reference. **`Unsupported` means what-if declined to predict;
`-` means it predicted a removal.** Only the predictions needed checking against
the provider schema.

**Blob soft delete is OFF on `stiipdevwus01`** (`deleteRetentionPolicy.enabled:
false`). Declared as found, not changed. Backlogged against M11, when the
Function starts writing results there and an accidental delete stops being
theoretical.

### Session — September 18, 2026 — short session, one backlog item

**Scope was chosen deliberately small.** One self-contained backlog item with
no Azure calls and no acceptance-test exposure, rather than starting M8.
Gerard chose the item and ran the import check in the Windows venv; Claude
wrote the change, the verification and this entry.

**`cells_correct()` is fixed — judged and deterministic audit cells are now
counted separately.** It iterated all three fields per record, so every
`N/225` and `N/360` figure it produced credited the model with the
deterministic `text_legible` cells. Same defect `probe_fixture_stability.py`
carried until Sep 11, and it got the same fix.

- `cells_correct()` is replaced by `cell_counts()`, returning a `CellCounts`
  NamedTuple: `judged_correct`, `judged_total`, `deterministic_correct`,
  `deterministic_total`. **It carries no combined total, deliberately** — not
  even as a convenience property. A combined number that can be reached for is
  a combined number that gets quoted.
- `MODEL_JUDGED_FIELDS` and `DETERMINISTIC_FIELDS` are now explicit module
  constants, matching `probe_fixture_stability.py`. An audit field in neither
  raises `ValueError` rather than defaulting to judged.

**Verified with no Azure calls**, against
`results/20260910-123321_orchestrator_stability.json` — which is what the
Sep 11 entry predicted, and why the deferral "that would require another
orchestrator run" was wrong when it was made:

| population | all 8 items | matrix (items 1-5) |
| --- | --- | --- |
| old combined | 357/360 | 222/225 |
| model-judged | 237/240 | 147/150 |
| deterministic | 120/120 | 75/75 |

The two populations partition the old total exactly, in both slices. **The
deterministic cells were 120/120**, so the old combined figure was padded by a
population that cannot vary: 357/360 reads as 99.2% where the model's own
score is 98.75%.

**The row figure is untouched: 117/120, as the Sep 11 entry predicted.** A row
matches only if all three fields match, so an always-true conjunct cannot
inflate a conjunction.

**Results JSON keys changed.** `cells_correct`, `cells_total`,
`matrix_cells_correct` and `matrix_cells_total` are replaced by
`model_judged_*`, `deterministic_*` and the two field lists. Runs written
before today keep the old keys, so anything that later reads across runs must
handle both shapes. No script reads them today — checked.

**One verification caveat.** The check that loaded the whole module ran on the
Linux VM behind the folder bridge, which has no azure SDK, so the azure
imports were stubbed. Gerard ran `python -c "import m7_orchestrator"` in the
Windows venv, which closes that gap.

**The rest of this file was swept for the old name, and annotated rather than
rewritten.** Three past entries referenced `cells_correct()`, which no longer
exists in the code: the Sep 11 open-defect pointer, the Sep 11 "never needed a
run" lesson, and the Sep 8 unmeasured-items note. Each now carries a dated
bracket saying what changed on Sep 18; none of the original sentences were
altered, because each was true on the date it was written. **The standing figure
rule in Key Lessons was updated in place**, since that section is live guidance
rather than history: a combined `N/225` or `N/360` is no longer merely
forbidden, it is now unobtainable from the orchestrator.

**Not touched, deliberately.** `probe_orchestrator_stability.py`'s `agreement`
counter still counts passes rather than matches. Separate backlog entry,
separate session.

## Archived sessions

August 10 – September 16, 2026 — the M7 build through its acceptance test, and
the Sep 16 Phase 2 planning session, plus the superseded Aug 12–20 "Next action"
appendix — lives in `STATUS-archive-m7.md` in this same folder. Split out
2026-09-24 (moved verbatim) because this file had grown to about 5,500 lines, 80%
of them closed history. A "see the <date> entry" for those dates resolves there.


July 27 – August 7, 2026 — the M2–M6 build, all milestones complete — lives in
`STATUS-archive-phase1.md` in this same folder. Split out 2026-09-06 to keep this
file to the live milestone. Same repo, nothing lost; open it when you need the
history behind M2–M6.
