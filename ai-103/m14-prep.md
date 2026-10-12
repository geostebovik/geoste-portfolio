# M14 prep: operate (CI/CD over OIDC, alerts, tracing)

*Drafted by Claude, 2026-10-12, from Microsoft Learn and the repo. Gerard made
the decisions marked D-M14. Nothing here is built yet.*

**M14's done-when** (`phase2-orientation.md`, Milestones table): *a push
deploys the Function, and a trace and an alert can each be shown.* No
deadline, and it doesn't depend on M13.

## Decisions (Gerard, 2026-10-12)

- **D-M14-1, order: CI/CD over OIDC first, then alerts, then tracing.**
  Deploys need no new packages and are the most visible portfolio item;
  alerts need no code; tracing is the least certain (see Part 3).
- **D-M14-2, OIDC trust limited to branch `main`.** The federated credential's
  subject is `repo:geostebovik/geoste-portfolio:ref:refs/heads/main`. A GitHub
  environment with an approval step was the stronger option, and was turned
  down for now: Gerard is the only committer.
- **D-M14-3, tracing now, on the classic agent API.** It meets the done-when
  ("a trace can be shown") without waiting for the classic-API migration. The
  exporter and the Function-level spans survive the migration; the agent-level
  spans get redone with it.

## Part 1: CI/CD over OIDC (first)

**How it deploys today:** by hand from the tower. `function/build_package.py`
copies `function/` (5 files), 8 modules from `scripts/` and the fact sheet into
`function/.build/` in the repo's own layout, and zips it. Then
`az functionapp deployment source config-zip --build-remote true`. Flex
installs the pinned `requirements.txt` on Linux (remote build).

**What already exists (M9):** `id-iip-dev-wus-02`, a user-assigned identity
with **Website Contributor on `func-iip-dev-wus-01`** (RBAC model). Microsoft
Learn's three steps ("Deploy to Azure Functions by using GitHub Actions") are:
1. ~~an identity with Website Contributor on the app~~ (done in M9);
2. a **federated credential** on that identity that trusts the repo;
3. the identity's client, tenant and subscription IDs as GitHub repository
   secrets, and a workflow using `azure/login` (OIDC) and
   `Azure/functions-action@v1`.

**What gets added:**
- **Bicep, `identity.bicep`:** `Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials`
  on `id-iip-dev-wus-02`. Issuer `https://token.actions.githubusercontent.com`,
  subject per D-M14-2, audience `api://AzureADTokenExchange`. Expected what-if:
  the register plus **1 to create**.
- **GitHub (Gerard, in the repo's Settings):** secrets
  `IIP_AZURE_CLIENT_ID`, `IIP_AZURE_TENANT_ID`, `IIP_AZURE_SUBSCRIPTION_ID`.
  They're identifiers, not passwords; they're kept as secrets because Learn
  says so, and it keeps the subscription ID out of public logs (the same call
  as the M12 evidence).
- **Workflow, `.github/workflows/iip-function-deploy.yml`:**
  - triggers on a push to `main` that touches what goes in the package:
    `ai-103/function/**`, the 8 modules in `build_package.py`'s
    `SCRIPT_MODULES`, the fact sheet and the workflow file itself. That list
    is a second copy of `SCRIPT_MODULES`, so the workflow checks that they
    agree and fails if they don't. Also `workflow_dispatch`, for a deploy by
    hand.
  - `permissions: id-token: write, contents: read`; one deploy at a time
    (`concurrency`).
  - steps: checkout → `python build_package.py` (it only copies files and
    checks imports, so the runner's Python version doesn't change the
    package) → `azure/login` with the three secrets →
    `Azure/functions-action@v1` with `package: ai-103/function/.build` and
    **`remote-build: true`**, the Flex parameter Learn names. Flex doesn't
    support `slot-name`; no `sku` with OIDC.

**Proof for the done-when:** a small, harmless change pushed to `main` →
the workflow goes green → the Function's latest deployment is the workflow's →
a **regression upload** (item4, as in M12) gives the answer key. Also record
that the workflow used no secret except the three IDs.

**Things to settle while building:**
- The existing SWA workflow (`azure-static-web-apps-...yml`) runs on every
  push to `main` and publishes the whole repo. A Function push runs both.
  That's harmless, but it's worth knowing when reading the Actions tab.
- **The Oct 19 Ubuntu runner migration** (Todoist, logged Oct 5) now affects
  two workflows, not one. Both use `ubuntu-latest`.
- Pass 1's open follow-up (Todoist: deployed-package provenance). Inside the
  Function, `git_head` is `None`. A workflow deploy knows its commit SHA, so
  this is the natural moment to stamp it into the package. That could close
  the follow-up for free, and it's a small change to `build_package.py`.

**Cost:** $0 in Azure (a federated credential and a role that already
exists). GitHub Actions minutes are free for a public repo.

## Part 2: alerts (second)

**Done-when:** "an alert can be shown". **The plan says: reuse the $90 budget
alert.** It isn't in any Bicep here, and the repo doesn't record how it was
made, so the survey starts by reading it (Cost Management → Budgets) and checking whether it
already has an **action group**, which is the "who gets told, and how" object
an alert rule points at.

**Candidate alerts** (to choose from after the survey, not decided):
- **An upload parked in `upload-events-poison`**, meaning it failed twice
  (row 16's behaviour). This is the one alert that means "the app is broken".
  **It can't be a storage metric alert:** `QueueMessageCount` has no per-queue
  dimension (it counts every queue in the account together), and Learn says
  it's refreshed daily (Microsoft Learn, queue metrics reference and
  "Best practices for monitoring Azure Queue Storage"; checked 2026-10-12).
  So it has to be a **log search alert** in App Insights, on the Function's
  failed executions or on the host's log line when it moves a message to the
  poison queue. Which line to match comes from a real failure in the logs,
  not from guessing.
- **Function failures** in general, from App Insights (the same log search
  alert, widened).
- The budget threshold itself.

**Proof for the done-when:** a fired alert. The poison alert can be fired on
purpose with Sep 29's failure-path test (an upload without `topic`).

**Cost:** an email action group is free at this volume. A log search alert
is billed per rule by how often it runs, and costs more than a metric alert,
so check the retail price list before choosing the frequency.

## Part 3: Foundry tracing (third)

**Today:** the Function's App Insights shows each run as one request ("Executed
process_upload, Succeeded, 44 s"). The agent run inside it is a black box.

**What tracing adds:** spans for the agent run, each tool call
(`get_fact_sheet` → `evaluate_draft` → `audit_thumbnail`) and each model call,
with timings and token counts, under one trace ID.

**From Learn, and what it means here:**
1. **The tracing guide for this SDK (`azure-ai-agents` 1.1.0) is in the
   *classic* docs and is marked preview.** The classic API retires 2027-03-31.
   D-M14-3 accepts that the agent spans get redone at the migration.
2. **App Insights takes Entra-authenticated telemetry only** (M11). The Azure
   Monitor exporter builds its credential from
   `APPLICATIONINSIGHTS_AUTHENTICATION_STRING`, which the Function already
   has. So authentication should need no new setup. Verify it, don't assume
   it.
3. **New packages in a fully pinned build:** `azure-monitor-opentelemetry` and
   the OpenTelemetry SDK, plus whatever they pull in. They've never been
   measured. Pin them the same way (venv first, then `requirements.txt`), and
   do a regression upload after.
4. **Learn's Functions caveats:** the Functions worker already sends logs, so
   `configure_azure_monitor()` can **duplicate log entries** unless the
   worker's handler is removed; and incoming requests aren't correlated with
   the code's own spans automatically, so the trace context has to be picked
   up by hand.
5. Message content stays **off** by default
   (`AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED`). Keep it off: the
   prompts carry the store's fact sheet, and the traces don't need it.

**A side benefit:** model-call spans count tokens independently of
`run.usage`, which may settle the M7 backlog's "token count ~40% low" item.

**Cost:** ingestion goes to `log-iip-dev-wus-01` (1 GB/day cap, 30 days).
Expected volume is small. Measure it after the first traced runs.

## Size

Claude's estimate: Part 1, about one session; Part 2, half a session (most of
it the survey); Part 3, about one session including the regression upload.
That fits the plan's "1–2 sessions" only if Part 2 stays small.

## Next step

**Part 1, step 1:** Claude writes the federated credential into
`identity.bicep` and predicts the what-if; Gerard runs it.
