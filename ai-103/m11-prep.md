# M11 prep — the app, surveyed before building

> ## DECIDED AND PROBED SO FAR (2026-09-23) — read this box first
>
> | Item | Result |
> |---|---|
> | Probe 1, region | **`westus` supports Flex Consumption** (Gerard ran `list-flexconsumption-locations`), with Python **3.10–3.14** available there. The Function stays in the resource group's region; no naming or residency decision. |
> | D-M11-1, trigger | **(b) Event Grid → Storage queue → queue trigger** (Gerard). No webhook, no `blobs_extension` key; the M12 inbound-restriction question dissolves. |
> | D-M11-2, sign-in | **(b) managed identity as a federated credential**, dedicated identity `id-iip-dev-wus-03` (Gerard). No client secret. |
> | Laptop fix (1) | **Committed at `71b90b9`.** Verified: `get_endpoint('x','x')` returned the endpoint with no `az` call (a fallback would have failed on the bogus account), and `m6_probe.py` completed live through it. |
| Probe 2, import time | **4.57 s** for `import m7_orchestrator` on the laptop, with `az` out of the path. Heaviest: `openai` 2.07 s (its `types` package 1.43 s), `azure.ai.evaluation` 1.51 s, `azure.identity` 0.27 s, `azure.ai.agents` 0.24 s. Under the 10 s "proceed" line — but a laptop figure is a floor, and the 1-core instance plus the Functions host share the same 30 s. Cheap insurance at build time: import the tools inside the function body, not at the top of `function_app.py`. |
>
> | Probe 3, package size | **235 MB** installed (Windows wheels, `playwright` excluded). Under the 1 GB package limit Microsoft documents for run-from-package — but see the next row. |
> | Found while sizing probe 3 | Microsoft's Python build guide: **"Remote build has a 60-second timeout: If dependency installation exceeds the limit, the build fails."** 235 MB of dependencies is a real risk against 60 s. The documented fallback is a local build **on Linux** (never Windows) — e.g. a GitHub Actions `ubuntu` runner, which M14's OIDC pipeline would use anyway. The same guide gives Python **3.13+** a **2-minute** module-import window, where the Flex page says app initialization times out after 30 s; which ceiling governs is **unverified**. |
>
> | Item | Result (2026-09-24) |
> |---|---|
> | Build path | **Remote build first** (Gerard). A GitHub Actions `ubuntu` local build is the documented fallback, and M14 needs that runner anyway. Stand-in timing (Claude ran it; Linux, 2 cores, pip 26.2.1, `--no-cache-dir --only-binary=:all:`, `playwright` excluded): 3.12 **22.6 s**; 3.13 **21.1 / 23.4 / 21.8 s**; 3.14 **57.6 / 30.2 / 26.2 / 27.2 s**. **Caveat:** the first 3.14 run came within 3 s of the 60 s limit, so a cold network path can roughly double the time. This isn't Oryx: the first real remote build is the measurement, and a failed build costs minutes and changes nothing in Azure. |
> | 3.14 timings, corrected (same day) | The four 3.14 runs in the Build path row ran on **3.14.0rc2**, a release candidate. My workspace only had that build, and I didn't notice until pydantic failed on it. Re-measured on **3.14.7** with the Function's **actual** requirements file (`function/requirements.txt`): **24.3 s, 308 MB**. It's still a stand-in, not Oryx. (Claude) |
> | D-M11-3, agent lifecycle | **Per invocation** (Gerard): create, run, delete in `finally`, the path M7/M10 certified. |
> | Upload contract | **`topic` as blob metadata** (Gerard). A missing topic gives an error result with no retry. See `function/README.md`. |
> | **First live run of the handler** (2026-09-24, Gerard ran it, laptop, no Functions host) | `local_run.py item4-key-cutting-FLAW-brand.png`, uploaded with `topic` metadata: run COMPLETED; tools `get_fact_sheet`, `evaluate_draft`, `audit_thumbnail`; text passed first draft (groundedness 4.0, relevance 4.0, 0 redrafts); audit **text_legible true, brand_consistent false, info_accurate true** — item4's answer key, compared by eye (uploads are not scored); result written to `results/item4-key-cutting-FLAW-brand/20260924T175714Z.json`. Proves: metadata read, blob download, absolute-path hand-off, agent create/run/delete, result write — all under Gerard's identity. **Does not prove:** the queue trigger, Event Grid's encoding, the managed identity's roles, or anything inside the Function. n=1. |
> | **Priced** (Azure retail prices API, westus, 2026-09-24, Claude) | Flex on-demand execution **$0.000037/GB-s** once past the free grant (100,000 GB-s/month; whether a VSE subscription gets it is still unverified). Executions $0.40/million. Event Grid $0.60/million operations, first 100K free. Log Analytics **$2.99/GB** once past the free 5 GB/month. **100 uploads/month:** about 18,000 GB-s, so **$0.67 without the grant**. Telemetry and events are free-tier. Host storage is cents. **Model tokens are about $0.05-0.10 per upload and dominate**, roughly $5-10 per 100 uploads. Idle cost is **$0**: there are no always-ready instances. Guards: at most 2 instances, a 1 GB/day Log Analytics cap (worst case about $75/month), and maxDequeueCount 2. |
> | **First light in Azure** (2026-09-24; Gerard ran every command, Claude wrote the code and Bicep) | Deployment `m11-app-pass1-20260924` Succeeded after the row 14 fix (see the RBAC model). The remote build on Azure succeeded first time, and `process_upload` registered. item4 was re-uploaded with `topic` metadata at 19:11:12Z, and the Function's result was written at **19:11:58Z: 46 s end to end, cold start included**. `results/item4-key-cutting-FLAW-brand/20260924T191158Z.json` shows status ok, dequeue_count 1, run COMPLETED. The Function called all three tools itself (`evaluate_draft` 7.4 s, `audit_thumbnail` 2.9 s), so the judge, Vision Read and gpt-5-4-mini all worked under `id-iip-dev-wus-01`. The audit **matches item4's answer key** (compared by eye). The text passed on the first draft (4.0/4.0). `run.usage` 12,177 tokens. **Found in the result:** provenance recorded `git_dirty: false` inside the Function, where there is no git at all. The code now records None plus a reason (`provenance.py`, its own commit). **Still unproven:** which encoding Event Grid uses (the handler now records it), telemetry (row 8), the poison path (row 16), and sign-in (pass 2). |
> | Package size, corrected | **303–310 MB on Linux**, not probe 3's 235 MB, which was measured on Windows. Linux wheels carry bundled libraries (for example `numpy.libs`). Still well under 1 GB. Largest: `pandas` 77 MB, pulled in by `azure-ai-evaluation`, so it can't be trimmed. Every package has a 3.14 wheel, so nothing builds from source. |
> | Python version | **3.14**, matching the local venv (`Python 3.14.0`, Gerard). GA on Functions, expected end of support April 2029 (Microsoft Learn, supported languages). 3.13+ gets the 2-minute import window; the Flex 30 s initialization ceiling is still unresolved against it. |
> | Function requirements | `scripts/requirements.txt` covers the whole lab. The Function gets its **own** requirements file. Drop `playwright` and `azure-search-documents`: nothing in the M7 import chain uses them. **Keep `python-dotenv`.** *(Corrected 2026-09-24, same day: this row first said to drop it, but six modules in the chain import `load_dotenv` at module scope, so dropping it would break the app at import.)* **Add** `azure-functions` and `azure-storage-blob`, which the Function needs to read the uploaded blob and write the result. The lab file never needed them. |
>
> The survey below is unedited.

**Surveyed 2026-09-23,** straight after M10 closed. Claude read the M7 code
paths the Function will run, the RBAC model, and Microsoft Learn (Flex
Consumption hosting, the Event Grid blob trigger, Event Grid managed-identity
delivery, App Service built-in authentication). **Nothing here has been built or
run.** When the probes below run, record the results in a box at the top of this
page and keep the survey beneath it unedited — the M10 convention, so the gap
between a survey and a measurement stays visible.

M11's done-when (`phase2-orientation.md`): *an upload produces a result, and a
group member can sign in and see it; the RBAC model's VERIFY rows are recorded
as confirmed or changed.*

## The headline: the M7 code assumes a developer's laptop

The Function is not "deploy the orchestrator to Azure". Four things in the code
that M10 certified only work on a machine with Azure CLI, a `.env` file and the
repo checked out:

1. **Azure CLI at run time — and at import time.** `m3_analyze.get_endpoint()`
   shells out to `az cognitiveservices account show`. Three tools call it:
   `m7_cv_audit_tool.py`, `m7_legibility_check.py` — and `m7_evaluator_tool.py`,
   whose `build_judge_config()` runs **at module scope** (line 113). So merely
   *importing* the evaluator runs `az`. A Function has no `az`. **This breaks the
   app before its first invocation**, while the host is loading the code.
2. **The 30-second host start.** Flex Consumption: *"The app initialization
   times out after 30 seconds … You can't currently configure this timeout."*
   The orchestrator imports `azure-ai-evaluation`, `azure-ai-agents`, the Vision
   SDK, `openai`, `numpy` and `pydantic`. On a laptop that is several seconds; on
   a 2 GB / 1-core instance it is unmeasured. Module-scope work (item 1, the
   fact-sheet reads) adds to it.
3. **Repo-relative files.** `FACT_SHEET_PATH` resolves `../iip-docs/...` from
   `scripts/`; thumbnails are local paths. The deployment package must carry the
   fact sheet, and an uploaded thumbnail arrives as a blob, not a path.
4. **Provenance calls `git` and `az`.** `core_provenance()` and
   `deployment_builds()` never raise (their standing rule), so they will record
   errors rather than crash — but a Function run's provenance needs its own
   source: the deployed package version and app settings, not a git tree.

**The fix for (1) is small and can be done before anything is built:**
`get_endpoint()` reads an `AIF_ENDPOINT` setting when present and falls back to
`az` otherwise, so laptop runs are unchanged. The value is the pinned
custom-subdomain endpoint (`aif-iip-dev-wus-01`, see the project's naming
exception) — which, conveniently, removes a live `az` lookup from every run.
Testable locally with one smoke run; not model-facing.

## Two keys hiding in the textbook design

M10 made "no script reads a key" true. The standard M11 design would bring two
back, in places that do not look like keys:

- **The blob trigger's webhook key.** On Flex Consumption the blob trigger
  **only** supports the Event Grid source. Event Grid delivers to
  `/runtime/webhooks/blobs?...&code=<blobs_extension key>` — a function system
  key in the subscription URL. Two more costs: the key exists only after code
  is deployed, so the event subscription cannot be created until then (Bicep
  ordering), and this webhook is exactly what the open Todoist item says breaks
  under inbound access restrictions at M12.
- **The sign-in's client secret.** Built-in authentication (Easy Auth) with
  Microsoft Entra is a confidential client when a secret is configured, and
  falls back to the implicit flow without one. Microsoft documents a secretless
  alternative: a **managed identity as a federated identity credential** on the
  app registration (`OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID`). Microsoft says
  that identity *"should only be assigned to the App Service or Azure Functions
  application through this registration"* — so it is a **third** user-assigned
  identity, not `id-iip-dev-wus-01`.

Each has a keyless alternative. Both are decisions — see D-M11-1 and D-M11-2.

## Decisions (Gerard's)

**D-M11-1 — trigger shape.**
- **(a) Event Grid blob trigger** — the documented Flex pattern. Webhook +
  `blobs_extension` key; subscription created after first code deploy; conflicts
  with M12 inbound restrictions.
- **(b) Event Grid → Storage queue → queue trigger.** The system topic delivers
  `BlobCreated` events to a queue **using its own managed identity**
  (`deliveryWithResourceIdentity`; needs Storage Queue Data Message Sender). The
  Function reads the queue with an identity-based connection. No inbound
  endpoint, no key, no deploy-order problem, and the M12 Todoist question
  dissolves. Costs one queue (negligible) and a few RBAC rows.

**D-M11-2 — sign-in credential.** (a) client secret in an app setting; (b)
managed identity as a federated credential, via a dedicated `id-iip-dev-wus-03`.

**D-M11-3 — agent lifecycle** *(can wait until build).* The probes create one
agent per batch and delete it. The Function can create-and-delete per invocation
(stateless, slower) or reuse a long-lived agent id (faster, but a stored id and
drift between the agent's instructions and the code).

## Probes, before any build — in this order

1. **Region and runtime** (Gerard, ~1 min, free). Flex Consumption does not run
   in every region; `rg-iip-dev-wus-01` is `westus`.
   ```powershell
   az functionapp list-flexconsumption-locations --query "sort_by(@, &name)[].name" -o tsv
   az functionapp list-flexconsumption-runtimes --location westus --runtime python --query "[].version" -o tsv
   ```
   If `westus` is absent, the Function lives in another region — a naming,
   latency and data-residency decision to make *before* anything else.
2. **Import time** (Gerard, ~1 min, free). How long the orchestrator's imports
   take, against the 30-second ceiling. Run after the `AIF_ENDPOINT` fix, so
   `az` is out of the measurement:
   ```powershell
   python -X importtime -c "import m7_orchestrator" 2> importtime.txt
   ```
   A laptop figure is a floor, not the answer — the 1-core instance will be
   slower. Well under 10 s: proceed. Near or over 15 s: plan lazy imports first.
   (Those thresholds are Claude's judgment, not documented figures.)
3. **Package size** (Gerard, ~3 min, free). `pip install -r requirements.txt
   --target .pkg` into a scratch folder, then measure it. Drop build-only
   dependencies (`playwright`) from the Function's requirements.

## RBAC changes this implies (for the model, not yet applied)

- **Row 5** (Function → `uploads` read) stays a VERIFY. Under D-M11-1 (b) the
  trigger's connection is a **queue**, so the blob-trigger role guidance (Blob
  Data Owner) no longer applies; the Function reads the blob named in the event.
- **New, under (b):** system-topic identity → Storage Queue Data Message Sender
  on the queue; Function identity → Storage Queue Data Reader + Storage Queue
  Data Message Processor on the queue.
- **New, under D-M11-2 (b):** `id-iip-dev-wus-03` — no Azure RBAC at all; a
  federated credential on the app registration.
- **Row 7** (host storage) and **row 8** (App Insights, Entra-authenticated
  telemetry) unchanged; still VERIFY.

## Cost, sized

- **Function compute:** one item run is ~46–90 s. At 2 GB that is ≤180 GB-s;
  100 runs ≈ 18,000 GB-s. The Flex monthly free grant is 100,000 GB-s and
  250,000 executions, *"on paid, consumption subscriptions only"* — whether a VSE
  credit subscription qualifies is unverified. Without it, the execution cost is
  still cents per hundred runs. **Model tokens dominate, as they do today.**
- **Event Grid, one queue, App Insights, Log Analytics:** low single dollars a
  month at this volume. Price with the calculator before building, as M12 will.

## Parked here from the backlog (decide during M11)

- **`disableLocalAuth`** — after M10 and M3, the VS Code poll is the only known
  consumer of the account key. Identify the extension first.
- **Foundry Agent Consumer** for the Function identity — test once the
  Function's real call pattern exists.
- **Blob soft delete** on `stiipdevwus01` before the Function writes results.
- **`versionUpgradeOption`** — not M11 scope, but must be decided before the
  next measured pass.

## Sources (Microsoft Learn, read 2026-09-23)

Azure Functions Flex Consumption plan hosting (Considerations; Billing;
Supported language stack versions) · Create and manage function apps in the
Flex Consumption plan · Tutorial: Trigger Azure Functions on blob containers by
using an event subscription · Use managed identities to deliver events in Azure
Event Grid · Storage queue as an event handler for Azure Event Grid events ·
Configure your App Service or Azure Functions app to use Microsoft Entra sign-in
(Use a managed identity instead of a secret) · Authentication and authorization
in Azure App Service and Azure Functions. Pricing: Azure Functions pricing page
(free grant wording).
