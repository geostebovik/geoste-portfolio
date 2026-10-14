# M14 prep: operate (CI/CD over OIDC, alerts, tracing)

*Drafted by Claude, 2026-10-12, from Microsoft Learn and the repo. Gerard made
the decisions marked D-M14.* **Parts 1 and 2 are DONE (2026-10-12)**: see
"Part 1, the run" and "Part 2, the survey and the run". Part 3 (tracing) is
not started.

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
- *(D-M14-4 to -6 are recorded where they were made: Part 2 and Part 3.)*
- **D-M14-7 (2026-10-13), name each tool call with a span around the
  orchestrator's `logged()` helper**, patched at runtime, rather than
  settling for the SDK's spans, which don't name tools. See "Part 3, the
  build and the run".

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

### Part 1, the run (2026-10-12)

Claude wrote the Bicep and the workflow and read every result; Gerard added
the GitHub secrets, placed the workflow file, and ran every command and push.
1. **The federated credential**, `m14-oidc-fic-20261012`. The what-if was the
   register plus 1 create, exactly as predicted; read back with
   `az identity federated-credential list` (one entry, the main-branch
   subject).
2. **The workflow.** The remote tools may not write under `.github/workflows`
   (a protected location), so Claude left the file in Gerard's working folder
   and Gerard copied it into place. A person places every CI file, which is
   the right default anyway.
3. **First deploy: the push of `fd02de9` itself** (it touches the workflow
   file, which is in the path filter). Both workflows ran green (the SWA one
   runs on every push). The check step printed "OK: the path filter watches
   all 8 packaged modules", and the deploy step reported a remote build and a
   successful deployment (Gerard read both in the Actions log).
   **Who deployed:** the Function's activity log shows
   `Microsoft.Web/sites/publishxml/action` at 18:14:00Z with caller
   `3a770f3a-…`, which is `id-iip-dev-wus-02`'s principal ID, not Gerard.
4. **Regression upload, PASS.** `item4-m14-oidc-20261012.png` at 18:23:03Z →
   result in 49 s, first delivery; the same three tools; copy passed first
   time; audit = item4's answer key
   (`scripts/results/20261012-182352_function_item4_m14_oidc.json`).
   **Done-when clause 1, "a push deploys the Function", is met.**

**Found on the way: basic auth was ON** (Gerard ran the check, prompted by the
`publishxml` line). `basicPublishingCredentialsPolicies` `scm` and `ftp` both
read `allow: true`, the default for an app created by ARM. So the publish
profile that Website Contributor can fetch held a working username and
password for the deploy endpoint: a secret that sidestepped the secretless
deploy. **Fixed in `app.bicep`** (both `allow: false`), `m14-basicauth-off-20261012`;
what-if exactly as predicted (2 Modify, `true => false`); read back `false`
and `false`. **The OIDC deploy still works without it:** a `workflow_dispatch`
run went green. The register is now **6 modify, 30 no change, 11 Unsupported,
2 to ignore** (confirmed by a what-if after the deploy).

**Also found, and closed:** two `Microsoft.Web/sites/write` events under
Gerard's account that he hadn't run (17:25:11Z and 18:13:13Z). Claude
predicted, and the activity log confirmed, that each shares its correlation ID
with one of the day's CLI deploys (teardown `ea85e94d…`, credential
`213563d6…`), ten minutes later. They're the late completion records of
those deploys, not separate actions. All writes that day came from the Azure
CLI's app ID (`04b07795-…`).

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
purpose with Sep 29's failure-path test. *(Corrected 2026-10-12: that test's
failure comes from deleting the blob while the trigger is paused, not from
the missing `topic`. See the run below.)*

**Cost:** an email action group is free at this volume. A log search alert
is billed per rule by how often it runs, and costs more than a metric alert,
so check the retail price list before choosing the frequency.

### Part 2, the survey and the run (2026-10-12)

**Survey** (read-only; Gerard ran the commands, Claude read the results):
- **The budget `Credits_low`:** $90 a billing month; it emails at 75% actual
  and 111% forecast **straight to an address, with no action group**
  (`contactGroups` empty). The address is Gerard's backup inbox, which he uses
  for low-priority mail (Gerard, Oct 12). It's left as it is. Claude's note,
  not a decision: this is the only cost warning for the subscription that
  also hosts ostebovik.net, so a second address costs nothing.
- **No metric alerts, and one action group:** the auto-created "Application
  Insights Smart Detection", with 0 email receivers. Before today, nothing
  would have told anyone the app was broken.
- **The poison line is exact:** `Message has reached MaxDequeueCount of 2.
  Moving message to queue 'upload-events-poison'.` (AppTraces, severity 2),
  7 times since Sep 25.
- **14 of 24 `process_upload` runs failed in 20 days, and every one is
  explained:** 7 poisoned messages × 2 tries each, all from the deliberate
  Sep 25 and Sep 29 failure-path tests. So the alert keys on the poison line,
  not on failed runs. A failed try that a retry fixes isn't an outage.
- **Prices** (Azure retail price list, westus, per rule per month): log search
  alert $3.00 at 1 minute, $1.50 at 5, $1.00 at 10, **$0.50 at 15**.

**Decisions (Gerard):** **D-M14-4**, check every 15 minutes ($0.50 a month).
**D-M14-5**, the alert address lives in a persistent user environment
variable (`IIP_ALERT_EMAIL`), never in the public repo; like the home IP,
`main.bicep` fails at compile time without it.

**Built** (`modules/alerts.bicep`, Claude): `ag-iip-dev-wus-01` (one email
receiver, common alert schema) and `alert-iip-poison-dev-wus-01` (no CAF
abbreviation exists for a log alert rule, so the name is descriptive). The
rule checks every 15 minutes but **looks back 30**
(`overrideQueryTimeRange`), so a line ingested a few minutes late isn't
missed. That's free, because the price follows the frequency. It's
stateful, so one parked upload sends one email. Deployed as
`m14-alerts-20261012`; the what-if was the register plus 2 creates, exactly as
predicted. Gerard confirmed the action group's opt-in email.

**Proof** (Sep 29's method; Gerard ran it): `m14-alert-test-20261012.png`
uploaded at 19:05:29Z **with no `topic`**.
**The first attempt didn't fail, and that's by design:** a missing `topic`
makes the handler write an error result and return normally (no exception,
so no retry and no poison). That's correct behaviour, because a missing topic
is the uploader's mistake, not an outage. The test was Claude's error: Sep
29's failure came from **deleting the blob while the trigger was paused**,
not from the missing topic. **Redone that way:** paused `process_upload`
(confirmed with `appsettings list`), uploaded `m14-alert-test2-20261012.png`,
peeked it at `dequeueCount` 0 (19:14:41Z), deleted the blob, un-paused. Both
tries failed (blob not found), and the poison line landed at
**19:18:39Z**. **The alert fired at 19:22:56Z** (about 4 minutes after the line), and its
history shows "Action group ag-iip-dev-wus-01 executed" 0.2 s later. **But
the email for that firing never arrived** (Gerard searched every folder for
all three sender addresses Learn lists). The delivery path itself works: the
portal's action-group **Test** (Log search alerts V2 sample, at about 19:55Z)
reported Success and its email arrived (sender `azure-noreply@microsoft.com`).

**Two more real notifications, also not delivered:**
- **The resolve, 20:23:57Z.** A stateful log alert at a 15-minute frequency
  resolves after **3 quiet checks** (Learn, "Alerts and state"). The rule
  checks at :08/:23/:38/:53; the line left the 30-minute look-back at
  19:48:39, so the quiet checks were 19:53, 20:08 and 20:23. It resolved on
  the third, and the action group executed again. No "Resolved" email.
  (Claude first predicted 20:34-20:50 by adding slack instead of working out
  the rhythm.)
- **A re-fire, 20:37:57Z** (the same pause/delete method, line about 20:35):
  fired on the 20:38 check exactly as predicted, the action group executed,
  and no email.

**Ruled out, against Learn's "Missing email notification" checklist:** an
alert processing rule (`isSuppressed: false`; the history says "executed");
an ARM-role receiver (it's a plain email receiver); a mailbox that blocks
external mail (the test from the same sender arrived); inbox rules or spam
(`in:anywhere` searches for all three senders, and Gmail filters checked);
unsubscribed (receiver `Enabled`, OTP verified correctly, Gerard). Also
ruled out: verification still settling (80 minutes later at the resolve).

**So: 3 real notifications handed to the action group, 0 delivered; 1 test
delivered.** The cause is past what Learn documents. **Done-when "an alert
can be shown" is met** by the fired alerts and their history. *(The open
item this paragraph named, an ARM-role receiver cross-check, was dropped on
2026-10-13: the fault was found and fixed first. See the next section.)*

### Part 2, the delivery fault: found and closed (2026-10-12 to -13)

**Cause, from the action group's troubleshooter** (Gerard ran "Diagnose and
solve problems", 14:16 Phoenix, Oct 12): all 3 real notifications failed
with *"The group receiver AZURENOTIFICATIONGROUP:…/ag-iip-dev-wus-01 was
found to be empty after resolution"*. **No email was ever sent**, so the
mailbox checks above couldn't have found anything. The portal **Test** sends
to the receivers directly, without that resolution step, which is why it
arrived. Learn has no page for this message.

**Ruled out:** an unverified receiver. The portal shows `owner-email` as
"Email verification: Verified" (14:21).

**The fix: re-saving the action group** (14:27; `az monitor action-group
update --set enabled=true`; no property changed, so no Bicep drift).
Afterwards:
- **21:39Z, Oct 12:** the Resolved email for the 20:37:57Z alert arrived.
  This was the first real alert email ever delivered.
- **Oct 13, a deliberate re-fire:** the message reached `upload-events-poison`
  at 16:59:35Z, the alert fired at 17:07Z (10:07 Phoenix), and the email
  "Fired:Sev2 Azure Monitor Alert IIP: …" arrived by 10:09 Phoenix.

**0 of 3 delivered before the re-save, 2 of 2 after.** What this doesn't
prove: the re-save can't be separated from the time that passed, because
background propagation would look the same. Separating them would mean
breaking a working group on purpose. That isn't worth doing; the action
below is the same either way.

**Oct 12's first re-fire didn't fire, and that wasn't the alert's fault**
(Claude's errors, both found in AppTraces on Oct 13):
1. The upload was `m14-alert-refire-20261012.txt`. The handler skips anything
   that isn't `.png`/`.jpg`/`.jpeg` and returns normally, so nothing was
   retried and nothing was poisoned (`"skipped", "not an image"`, Succeeded,
   22:05:46Z).
2. The pause hadn't reached the running host. A host started at 22:05:45Z
   took the message 1 second later, and its queue listener only stopped at
   22:07:23Z. Seeing the setting in `appsettings list` proves it was saved,
   not that the host is obeying it.

**The method now** (Oct 13): pause; wait 5 minutes; upload a real `.png`
(`m14-alert-refire-20261013.png`); **peek twice, at least 2 minutes apart**,
and delete the blob only if the message is still there at `dequeueCount` 0
(09:53 and 09:56 Phoenix, both 0). Un-paused at 09:57; the message was
poisoned at 16:59:35Z, about 2.5 minutes later. The host checks the queue at
least once a minute, so a message that sits untouched for 2 minutes proves
the pause is holding.

**Lesson for any future action group:** the portal's Test doesn't prove that
real alerts are delivered. Prove it with one real fire. If the troubleshooter
reports "empty after resolution", re-save the group and fire again.

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
*(Corrected 2026-10-13, Claude: it doesn't. The undercount is the judge's
tokens, and the judge reaches its model through the `openai` package, which
the lean set doesn't instrument. Confirmed in the run: inside `execute_tool
evaluate_draft` only token requests appear. The agent's own spans read the same
service-side usage as `run.usage`, so they add nothing independent.)*

**Packages, resolved 2026-10-12** (Claude, `pip install --dry-run` against the
pinned `requirements.txt` for CPython 3.14 on manylinux, wheels only):
- **The distro** (`azure-monitor-opentelemetry` 1.8.11): **25 new packages**,
  13 of them instrumentation for frameworks the Function doesn't use (Django,
  Flask, FastAPI, psycopg2, DB-API, ASGI/WSGI and more).
- **The lean set:** `azure-monitor-opentelemetry-exporter` 1.0.0b58,
  `opentelemetry-sdk` and `-api` 1.45.1, `opentelemetry-semantic-conventions`
  0.66b1, `azure-core-tracing-opentelemetry` 1.0.0b13 (the bridge that makes
  Azure SDK calls emit spans) and `psutil` 7.2.2: **6 new packages.**
- **Neither changes any of the 61 existing pins.** Several are pre-release
  (b-versions), which is normal for this ecosystem.
- **D-M14-6 (Gerard): the lean set.** Claude writes the setup code that
  `configure_azure_monitor()` would have done.

**Cost:** ingestion goes to `log-iip-dev-wus-01` (1 GB/day cap, 30 days).
Expected volume is small. Measure it after the first traced runs.

### Part 3, the build and the run (2026-10-13)

**Found before building** (Claude, from the installed SDK's source, not the
docs): `azure-ai-agents` 1.1.0 has an `execute_tool` span helper that nothing
calls. With content recording off, the tool names aren't recorded anywhere
else either, so the three tools wouldn't have appeared by name.
**D-M14-7 (Gerard):** put a span around each tool by wrapping the
orchestrator's own `logged()` helper at runtime. No certified file changes, and
`build_toolset()`'s schema check proves the agent's tools didn't move.

**Built** (Claude): `function/tracing.py` (new), with one span per try in
`function_app.py` and one line in `upload_handler.py`. `build_package.py`
packages it, and `requirements.txt` gains the 6 pins.
- **Authentication:** the exporter's credential comes from
  `APPLICATIONINSIGHTS_AUTHENTICATION_STRING` (`id-iip-dev-wus-01`, RBAC row
  8). No new role or setting.
- **No log exporter**, so no duplicate log rows. Content recording is off in
  code, not by app setting.
- **Off switches:** no connection string (the laptop), or `IIP_TRACING=off`.

**Tested offline first** (Claude; CPython 3.14 with every pin plus the 6):
19/19 passed, covering:
- the spans join the host's trace under its span;
- tool spans carry names only;
- the certified `logged()` still records every call;
- a failure marks the span failed and still re-raises;
- the exporter builds a `ManagedIdentityCredential` from the auth string;
- the off switch works.

**A negative control:** a wrapper without `functools.wraps` is refused by
`build_toolset()`. Gerard installed the 6 in the local venv first (`pip
check`: no broken requirements).

**The run** (Gerard; commit `8b4dce6`, deployed by the workflow, green):
- **The upload:** `m14-trace-20261013.png` (item4) at 17:37:22Z. Result
  17:38:08Z (`process_upload` 31.9 s), first delivery, **item4's answer key**:
  copy passed first time, audit legible PASS / brand FAIL / info accurate PASS
  (`scripts/results/20261013-173808_function_item4_m14_trace.json`).
- **The trace:** 61 rows under one operation ID, all succeeded: the host's
  request, `iip.process_upload` (30.9 s), the agent's steps, and **`execute_tool
  get_fact_sheet` (0 ms), `evaluate_draft` (7.1 s) and `audit_thumbnail`
  (3.1 s)** in that order. Verbatim in
  `evidence/m14-tracing/trace-20261013T173737Z.txt`.
- **Done-when "a trace can be shown" is met. All three M14 done-when items
  are shown.**

**What the trace showed that the logs couldn't:**
- About 10 s of the 22.5 s agent run was our tools. Inside the audit's 3.1 s,
  the Vision call itself took 0.2 s.
- The judge's model call is invisible, as expected (see the corrected side
  benefit).

**Ingestion, measured** (one upload; Gerard ran Claude's query):
- **About 200 KB in total** (199,703 billed bytes): AppDependencies 76 KB
  (60 rows; these are the new spans), AppTraces 122 KB (99 rows), AppRequests
  1 KB.
- The 1 GB/day cap would take about **5,000 uploads a day** (10^9 / 199,703).
  The spans alone would take about 13,000.
- **The AppTraces rows are the bigger cost, not the tracing.** Claude's
  reading, not yet checked against a pre-tracing run: they're mostly the
  Azure SDK's HTTP logging. That's the existing "trim SDK HTTP logging"
  follow-up, now sized.

## Size

Claude's estimate: Part 1, about one session; Part 2, half a session (most of
it the survey); Part 3, about one session including the regression upload.
That fits the plan's "1–2 sessions" only if Part 2 stays small.

## Next step

**M14's three done-when items are all shown (2026-10-13).** Next, per the
plan: the Phase 2 write-up. *(The text below was the step before Part 3, kept
as history.)*

**Part 3, tracing**, with the lean set (D-M14-6). The packages are already
resolved, so don't redo that. Steps: install the 6 in the local venv, pin them
in `function/requirements.txt`, then Claude writes the tracing setup (exporter
with the Function's managed identity, the Azure SDK bridge, trace context from
the invocation, and no duplicate logs). Deploy goes through the workflow (a
push to `function/`), then a regression upload, then show the trace in App
Insights. *(The email open item is closed, 2026-10-13: see Part 2, "the
delivery fault".)*
