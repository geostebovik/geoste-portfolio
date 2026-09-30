# IIP Function (M11): one upload in, one result out

Written by Claude, 2026-09-24. Gerard approved the design and made its
decisions: the queue trigger (D-M11-1 (b)), the topic carried as blob metadata,
and one agent per upload (D-M11-3). Deployed 2026-09-24 (pass 1). The results
page was added 2026-09-30 (pass 2; see "The results page").

## The upload contract

Upload the thumbnail to `uploads` **with a `topic` metadata value**. The agent
drafts from the topic, so without one the Function writes an error result and
does no work.

```powershell
az storage blob upload `
  --account-name stiipdevwus01 --auth-mode login `
  --container-name uploads `
  --file .\item4-key-cutting-FLAW-brand.png `
  --name item4-key-cutting-FLAW-brand.png `
  --metadata topic="Key Cutting While You Wait"
```

The result lands in `results/<upload name without extension>/<UTC timestamp>.json`
as `{status, upload, provenance, record}`. `record` is exactly what
`m7_orchestrator.run_item()` returns. `expected_audit` is `null` for an upload,
which means **not scored**, never "failed".

## Files

| File | What it is |
|---|---|
| `function_app.py` | The queue trigger and the two results-page routes. A thin adapter over `upload_handler.process()` and `results_page.py`. |
| `upload_handler.py` | All the per-upload logic. It never imports `azure.functions`, so it runs on the laptop. |
| `results_page.py` | What a signed-in viewer sees: the list and detail pages. It never imports `azure.functions` either. |
| `host.json` | Queue settings. **Read the next section before changing any of them.** |
| `requirements.txt` | The Function's own dependencies, not the lab's. **Fully pinned** to the measured venv, plus `azure-functions` and `werkzeug`, which are new and unmeasured. |
| `build_package.py` | Builds `.build/` and `iip-function.zip`, mirroring the repo layout so the tools' `../iip-docs` paths resolve. It refuses to build if a packaged module imports an unpackaged sibling. |
| `local_run.py` | Runs `process()` on the laptop against a real blob already in `uploads`. |

## The results page (pass 2, 2026-09-30)

Written by Claude to Gerard's decisions: a list plus a detail view, at
`/api/results`, with `host.json` unchanged.

- `GET /api/results` shows the newest 25 results: upload, time, topic, status,
  the three audit verdicts and whether the copy passed.
- `GET /api/results/{upload}/{timestamp}` shows one result: the same facts
  plus the agent's final drafted copy, or the error.

**Security:**
- **The gate is built-in authentication** (`app.bicep`). Only users assigned to
  **IIP Results (dev)** get in (RBAC rows 10, 11).
- **Function auth level is anonymous on purpose.** A function key would put a
  shared secret in every URL.
- **Second lock:** `require_principal()` refuses with 401 when the
  `X-MS-CLIENT-PRINCIPAL-*` headers are absent. Built-in authentication sets
  them and strips any a client sends, so if sign-in were ever switched off,
  the page fails closed.
- **Every value is HTML-escaped**, because the drafted copy is model output.
- **Only names shaped like `_write_result()`'s are accepted**, so a crafted URL
  can't read another blob.
- **Headers:** a CSP with no scripts at all, `nosniff` and `no-store`.
- **Reads with the Function's identity** (`-01`, RBAC row 6) from
  `RESULTS_BLOB_ENDPOINT`. The viewer holds no Azure role (RBAC principle 3).

**Tested offline (Claude, 2026-09-30),** against fake result files through the
real `function_app` handlers (21 checks, all passing):
- 401 without a principal, on both routes;
- script tags escaped in the topic, the copy and the error;
- URL-encoded links;
- 404 for `..`, a slash in a name, a bad timestamp or a missing result;
- unreadable files shown as "unreadable", not a crash;
- the security headers present.

**Not tested offline:** the real storage calls and the real headers from
built-in authentication. That's the Azure test.

## host.json: why each value

| Setting | Value | Why |
|---|---|---|
| `queues.batchSize` / `newBatchThreshold` | 1 / 0 | **Correctness, not tuning.** The orchestrator keeps `TOOL_CALLS` and `_item_deadline` at module level, so two uploads processed at once in one worker would record each other's tool calls. Microsoft: the maximum concurrent per function is batchSize + newBatchThreshold, so these values give 1. |
| `queues.maxDequeueCount` | 2 | Each retry is a full agent run, and `run_item()` already retries transport failures 4 times internally. After 2 attempts the message goes to `upload-events-poison` (RBAC row 16). |
| `queues.messageEncoding` | `none` | Written before we knew which encoding Event Grid uses. **Settled 2026-09-24 (run 2): Event Grid writes base64 JSON** (`upload.message_encoding` in every result). The host default `base64` would therefore also have worked. `none` plus `parse_event()`'s tolerance for both forms works either way, so it stays. |
| `functionTimeout` | 45 min | The worst case inside `run_item()` is 4 attempts × `ITEM_DEADLINE_SECONDS` (600 s) plus backoff (5 + 10 + 20 s) = 2,435 s, about 40.6 min. That's over the 30-minute Flex default, which would have killed the orchestrator's own retries. |
| sampling | off | At this volume every trace is worth keeping. |

## App settings the Bicep must set (no keys, no connection strings)

- `UploadEvents__queueServiceUri` = `https://stiipdevwus01.queue.core.windows.net`
- `UploadEvents__credential` = `managedidentity`
- `UploadEvents__clientId` = the client ID of `id-iip-dev-wus-01`
- `AZURE_CLIENT_ID` = the client ID of `id-iip-dev-wus-01`. **Required:** the app
  carries two user-assigned identities (-01, and -03 for sign-in), and without
  this `DefaultAzureCredential` can't tell which to use.
- `AIF_ENDPOINT` (the pinned `aif-iip-dev-wus-01` subdomain endpoint),
  `AIF_PROJECT_ENDPOINT`, `AIF_ACCOUNT`, `AIF_RESOURCE_GROUP`,
  `CHAT_DEPLOYMENT_GPT_5_4`, `CHAT_DEPLOYMENT_GPT_5_4_MINI`, `CHAT_API_VERSION`.
  The same names as `scripts/.env`.

## Verified before any Azure resource exists (2026-09-24, Claude)

Checked against the **built package**, on Python 3.14.7 with this
`requirements.txt` installed:

- `function_app` imports in 0.19 s and registers `process_upload`.
- Event parsing works for plain JSON, base64 JSON and a one-element list. It
  skips BlobDeleted, other containers and non-images.
- `m7_orchestrator` imports in 1.19 s from the packaged layout, and the fact
  sheet resolves to `iip-docs/...` inside the package.
- `build_toolset()`'s wrapper-schema check passes.
- `run_item()` on a mocked client, for an upload item: `expected_audit` is
  `None`, `audit_matches_expected` is `None`, and the agent receives the
  absolute temp path. A fixture item still records its answer key unchanged.

**Verified in Azure since (2026-09-24):** two end-to-end runs through the
queue trigger, the identity-based connection and a real agent run inside the
Function. Both matched item4's key. See `m11-prep.md`. **Still not verified:**
telemetry (RBAC row 8) and the poison path (row 16).
