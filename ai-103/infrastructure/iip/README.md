# IIP dev — Bicep (M8 baseline, M9 identity and RBAC)

Bicep describing `rg-iip-dev-wus-01` **as it already exists**. This is not a
greenfield deployment and not a disaster-recovery template (see the caveat at
the bottom). Its job is to make `az deployment group what-if` boring, so that
a real change stands out against a known-quiet background.

Baselined from the live resources on **2026-09-21**. **First deployed the same
day** by M9, which is what moved this from a prediction to a tested description.

```powershell
cd C:\Users\gerar\geoste-portfolio\ai-103\infrastructure\iip
az bicep build --file main.bicep --stdout | Out-Null
az deployment group what-if `
  --resource-group rg-iip-dev-wus-01 `
  --template-file main.bicep `
  --parameters dev.bicepparam
```

## Accepted diffs — the register

`what-if` does not report zero changes against this resource group, and it
cannot. The lines below are the **complete** expected output. Anything else
appearing in a future run is a real change and should be treated as one.

| Resource | Diff | Why it is accepted |
|---|---|---|
| `aif-dev-wus-01` | `- properties.armFeatures` | The RAI legal-terms acceptance record. Appears nowhere in `AccountProperties` in the `2025-06-01` schema, so no template can declare it. |
| `.../projects/proj-iip-dev-wus-01` | `- kind: "AIServices"` | `kind` does not exist on `accounts/projects` in the `2025-06-01` schema, although ARM populates it. Unsettable. |
| `.../projects/proj-iip-dev-wus-01` | `- properties.agentIdentity`, `.endpoints`, `.internalId`, `.isDefault` | All flagged `ReadOnly`, or absent from the schema entirely (`agentIdentity`). |
| `srch-iip-dev-wus-01` | `- properties.endpoint` | Not flagged `ReadOnly`, but a search endpoint is not choosable. **Settled empirically 2026-09-21:** the M9 deployment left it as `https://srch-iip-dev-wus-01.search.windows.net`. Confirmed a schema inaccuracy, not a real setting. |
| `srch-iip-dev-wus-01` | ~~`+ tags.managed-by`~~ | **Applied 2026-09-21** by the M9 deployment. No longer expected; if it reappears, something removed the tag. |
| `stiipdevwus01/blobServices/default` | `- properties.deleteRetentionPolicy` | **Fixed, not accepted.** M9 declared `blobServices/default` with no properties, and `deleteRetentionPolicy` is writable — the same class of real diff as `defaultProject` in M8. Now declared as found (`enabled: false`). Should not reappear. **It partly did, 2026-09-24:** `- deleteRetentionPolicy.allowPermanentDelete: false`. That sub-property is writable too, so it's now declared as found. The record can't tell whether it was there after M9's deploy or appeared later. **Changed on purpose, 2026-09-29:** soft delete is now ON (blob and container, 7 days; Gerard's decision), deployed as `m11-softdelete-20260929`. The pre-deploy what-if showed exactly one new Modify here (`enabled: false => true`, `+ days: 7`, `+ containerDeleteRetentionPolicy`), with totals 7 modify, 21 no change, 11 Unsupported, 2 to ignore. **Expected from now on:** back to the stage 2b totals (6 modify, 22 no change). **Confirmed 2026-09-30** by the first what-if on the new machine (the tower): 6 modify, 22 no change. |
| `stiipdevwus01/.../containers/uploads`, `/results` | `- properties.defaultEncryptionScope`, `.denyEncryptionScopeOverride` | **Fixed, not accepted (2026-09-24).** Both are writable in the provider schema, and M9 declared the containers with only `publicAccess`. Now declared as found (`$account-encryption-key`, `false`). Should not reappear. |
| `appi-iip-dev-wus-01` | `+ properties.Flow_Type: "Bluefield"`, `+ properties.Request_Source: "rest"` | **Registered 2026-09-25** (first what-if after the M11 deploy). Not in the template, which sets only `Application_Type`, and not returned on read. The provider fills them in when it normalizes the request, so no template can make the diff go away. |
| `func-iip-dev-wus-01` | `+ siteConfig.localMySqlEnabled`, `+ siteConfig.minTlsVersion`, `+ siteConfig.netFrameworkVersion` | **Registered 2026-09-25.** A read-back gap: Flex doesn't return these on GET, so what-if always shows them as additions. The M11 deploy already sent the same template. |
| `func-iip-dev-wus-01` | `~ functionAppConfig.deployment.storage.value` | **Registered 2026-09-25.** The live value is the literal URL. The template's is `format(reference(stiipdevwus02).primaryEndpoints.blob, …)`, which what-if can't evaluate. It resolves to the same URL. |
| `func-iip-dev-wus-01/config/appsettings` | `+ properties` (the whole block) | **Registered 2026-09-25.** What-if can't read app settings (it would expose secrets), so the full block always shows as `+`. It carries no information. **Check app settings with `az functionapp config appsettings list`, never with what-if.** |
| `stiipdevwus02/blobServices/default` | ~~`- deleteRetentionPolicy`~~ | **Fixed, not accepted (2026-09-25).** Writable, the same class as `stiipdevwus01`'s. Declared as found in `app.bicep` (`enabled: false`, `allowPermanentDelete: false`). Should not reappear. |
| `stiipdevwus02/.../containers/app-package-func-iip-dev-wus-01` | ~~`- defaultEncryptionScope`, `- denyEncryptionScopeOverride`~~ | **Fixed, not accepted (2026-09-25).** Declared as found in `app.bicep`, with the same values as `uploads`/`results`. Should not reappear. |

Storage also shows `x properties.encryption.services` (Noeffect). That symbol
means ARM accepts the property and it changes nothing. The resource itself
reports `=` No change.

**Also expected, and not changes (recorded 2026-09-24):**
- `x properties.principalType: "User"` on RBAC row 2's role assignment
  (`d527a76f-…`), which reports `=`. It's a Noeffect marker: the property is
  sent on create, and the read-back doesn't compare it.
- **4 "Unsupported" diagnostics**, one each for rows 4, 5, 6 and 9. These are
  the role assignments whose `principalId` comes from `reference()` on an
  identity, so their resource ID can't be computed until the deployment runs.
  That's a structural what-if limitation (aka.ms/WhatIfUnidentifiableResource),
  so these four are never analysed. Their correctness rests on M9's
  `az role assignment list` check, not on what-if.
- An empty `Scope: /` header and the Bicep "new release available" warning.
  Neither is a resource diff.
- **Added 2026-09-25:** `x sku.tier: "FlexConsumption"` on `asp-iip-dev-wus-01`
  (Noeffect), and **2 "to ignore"** (`*`): the Smart Detection alert rule and
  action group that App Insights creates for itself. Neither is in the template.
- **Unsupported diagnostics are 11 as of 2026-09-28:** rows 4, 5, 6, 9, 7×2, 8,
  12, 14, 16, plus row 15's one custom-role assignment on `upload-events`.
  *(13 on 2026-09-25; stage 2b removed row 15's two built-ins. Confirmed by the
  stage 2b what-if, 2026-09-28: 6 modify, 22 no change, 11 unsupported, 2 to
  ignore, all as registered.)*

## How the register was built, and why it matters

Five properties in the first `what-if` run looked exactly like the noise above
and were not. Each was **writable** in its resource provider's schema, and
declaring it closed the diff:

| Property | Looked like | Actually |
|---|---|---|
| `accounts/properties.defaultProject` | provider bookkeeping | writable — omitting it risked clearing the data-plane default |
| `accounts/properties.associatedProjects` | derived from the child resource | writable — omitting it risked detaching the project |
| `deployments/properties.currentCapacity` (×4) | a status field | writable |
| `searchServices/properties.computeType` | a status field | writable — it is the Default vs confidential-compute choice |
| `searchServices/properties.networkRuleSet.bypass` | preview-only, unsupported | present and writable in `2025-05-01` GA; the module had been pinned to a stale API version |

**Nothing in the `what-if` output distinguished those from the genuine noise.**
Both arrive as a `-` on a property that reads like status. The only reliable
test is the resource provider's own schema:

```
az bicep build --file main.bicep --stdout | Out-Null   # catches version drift
```

plus checking the property's `ReadOnly` flag in the provider schema before
accepting any `-` as a false positive. `what-if`'s own "may contain false
positive predictions (noise)" banner is an invitation to dismiss real findings,
and should be read as a reason to check rather than a reason to relax.

## M11 pass 1 — the app (written and DEPLOYED 2026-09-24)

Claude wrote it. The decisions are Gerard's, recorded in `m11-prep.md`. It
compiles cleanly with Bicep 0.47.16 (`bicep build` and `bicep build-params`,
no warnings), which proves syntax and nothing more.

**New modules:**
- `app.bicep`: host storage `stiipdevwus02` (shared keys off from birth),
  `log-`/`appi-` (Entra-only ingestion, 1 GB/day cap), the Flex plan, and
  `func-iip-dev-wus-01` (Python 3.14, at most 2 instances, 2 GB). It also
  holds the system topic `egst-iip-dev-wus-01` with a **system-assigned**
  identity.
- `eventsub.bicep`: BlobCreated under `uploads/` goes to the queue
  `upload-events`, delivered with the topic's own identity. It deploys after
  `rbac.bicep`.

**Changed modules:**
- `storage.bicep` declares the queues `upload-events` and
  `upload-events-poison`. The queue *service* is `existing` on purpose, so
  this template doesn't take ownership of its CORS or other settings.
- `rbac.bicep` adds rows 7 (Blob Data Owner + Table Data Contributor on host
  storage), 8, 12, 14, 15 and 16. That brings the declared assignments to 13.

**Pre-deploy checks (Gerard):**
1. **Only one Event Grid system topic can exist per storage account.** If
   `stiipdevwus01` already has one (Defender for Storage can create one), the
   create fails and `app.bicep` must reference that topic instead.
2. `Microsoft.EventGrid` must be registered on the subscription.

**Deployed** as `m11-app-pass1-20260924` after one fix. The event subscription
failed 3/3 with a "Managed Identity Authorization Error" until row 14 moved
from queue scope to **account** scope; see `modules/rbac.bicep`. The orphaned
queue-scoped grant was then deleted by hand, because Incremental mode never
deletes anything. **Register additions from here on:** 8 more "Unsupported"
diagnostics (rows 7×2, 8, 12, 14, 15×2 and 16, whose principals are computed at
deploy time), which makes 12 in total. Confirm against the next post-deploy
`what-if`.

**Expected `what-if` (as written before the deploy):**
- The register above, unchanged.
- **Creates** for everything listed under "New modules", plus the two queues
  and the new role assignments.
- More "Unsupported" diagnostics. Every new role assignment whose principal
  comes from `reference()` falls in the same structural blind spot as rows
  4/5/6/9.
- **Nothing may show `~` or `-` on an existing resource.**

This section becomes a register entry after the first deploy.

## M11 pass 2 — sign-in (2026-09-30 to 2026-10-07; built and proven; group swap done, M11 closed)

Claude wrote it. Gerard made the decisions on 2026-09-30: Entra objects go in
**Graph Bicep, in a separate file**; RBAC row 10 starts with a **user**
assignment and swaps to the group on the P2 trial's first day (a group
assignment to an app needs Entra ID P1/P2).

**Step A, `main.bicep` (ARM, what-if applies):** `identity.bicep` adds
`id-iip-dev-wus-03` (tag `purpose: easyauth-fic`, no Azure role, RBAC row 17).
Compiles cleanly with Bicep 0.47.16 (`build` and `build-params`), which proves
syntax only. **Expected what-if:** the register unchanged (6 modify, 22 no
change, 11 Unsupported, 2 to ignore) **plus exactly 1 Create**, the identity.
Nothing else may move. **Result, 2026-09-30:** exactly that (1 create, 6
modify, 22 no change, 11 Unsupported, 2 to ignore). Deployed as
`m11-signin-id-20260930`: Succeeded. `az identity show` gives the tag
`purpose: easyauth-fic`, and `az role assignment list --all` for its principal
returns nothing, as row 17 requires. **Register from now on:** the same
totals, with 23 no change (the identity joins them).

**Step B, `entra.bicep` + `entra.bicepparam` (Microsoft Graph, NO what-if):**
the app registration **IIP Results (dev)** with its federated credential
`fic-id-iip-dev-wus-03`, the service principal ("Assignment required" = Yes),
tenant-wide admin consent for `openid profile email` only, and the group **IIP
Results Viewers (dev)** (no members). `bicepconfig.json` pins the Graph types to
`microsoftgraph/v1.0:1.0.0`. **Not compiled by Claude:** the types restore from
mcr.microsoft.com, which Claude's workspace can't reach, so `az bicep build` on
the tower is the first compile check.

**Step B result, 2026-09-30.** It took two fixes, both Claude's errors:
1. **`owners` takes plain object IDs in types version `1.0.0`**
   (`relationships: [ '<id>' ]`). Microsoft's current reference page shows
   `{ id: '<id>' }` objects, which belongs to a later types version. The build
   flagged it as warning BCP034 on all three `owners` blocks.
2. **The federated credential's `name` must be `'{parent}/{child}'`**, here
   `iip-results-dev/fic-id-iip-dev-wus-03`, even though the resource is nested.
   The compiler accepted a one-part name. The server rejected it, so the first
   deployment, `m11-entra-20260930`, **failed** on that resource.

Redeployed as `m11-entra-20260930b`: **Succeeded**. It updated in place, and
no duplicates appeared (the `uniqueName` keys did their job). **Read back and
matched the template:**
- exactly one app **IIP Results (dev)**, appId `16565c24-5afd-4581-8430-c615ded0291a`,
  `AzureADMyOrg`, redirect `https://func-iip-dev-wus-01.azurewebsites.net/.auth/login/aad/callback`,
  implicit ID tokens off;
- credential `fic-id-iip-dev-wus-03`: issuer `https://login.microsoftonline.com/e0249b00-…/v2.0`,
  subject `1030295e-…` (the principal ID of `id-iip-dev-wus-03`), audience `api://AzureADTokenExchange`;
- enterprise app: assignment required;
- consent grant: `AllPrincipals`, `openid profile email` only;
- exactly one group, **IIP Results Viewers (dev)**: security-enabled, not mail-enabled;
- owner of the app and of the group: `djeemunee@letter7.onmicrosoft.com`.

Nobody is assigned yet, so no **non-admin** can sign in (see step C for why
that qualifier matters).

**Step C, `app.bicep` (ARM, what-if applies), 2026-09-30.** It attaches
`id-iip-dev-wus-03` to `func-iip-dev-wus-01`, adds the app setting
`OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID` = `-03`'s client ID, and turns on
`authsettingsV2`: Microsoft provider with the app's client ID, the v2.0 issuer,
`clientSecretSettingName` = that setting, require authentication, redirect to
login, token store off, HTTPS only. `main.bicep` takes the app's client ID as
the parameter `resultsAppClientId` (in `dev.bicepparam`).
- **What-if:** 7 modify, 23 no change, 11 Unsupported, 2 to ignore.
  `authsettingsV2` showed as a **Modify** (`platform.enabled: false => true`
  plus the new blocks), not a Create. The Function's existing Modify gained
  exactly one line, `+ identity.userAssignedIdentities.../id-iip-dev-wus-03`.
  **Register from now on (corrected 2026-09-30, next run):** 6 modify, 24 no
  change, 11 Unsupported, 2 to ignore. Once deployed, `authsettingsV2`
  reports `=` No change. Claude had guessed it might stay a Modify because of
  the masked setting name. It doesn't.
- **Deployed** as `m11-signin-easyauth-20260930`: Succeeded. App settings:
  `OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID` = `2544a963-…` (`-03`), and
  `AZURE_CLIENT_ID` is unchanged (`efc6dd4a-…`, `-01`).

**Browser test 1: AADSTS700054** (`response_type 'id_token' is not enabled`).
Built-in authentication always asks `/authorize` for an ID token: the hybrid
flow (`code id_token`) when it has a credential, and the implicit flow
(`id_token`) when it doesn't. So `entra.bicep` now turns ID-token issuance
**on**, with access tokens still off. It was Claude's error: the first version
turned both off. Redeployed as `m11-entra-20260930c`: Succeeded.

**Browser test 2 (private window, as `djeemunee`, a Global Administrator):**
- The authorize URL carried **`response_type=code+id_token`**, so built-in
  authentication treated the `-03` setting as a credential. It did not fall
  back to the implicit flow.
- **Sign-in completed** and the Functions default page loaded. The code was
  redeemed with `-03`'s federated assertion and **no secret exists anywhere**.
  **D-M11-2 (b) is proven end to end.**
- **Not proven: the assignment gate.** Nobody is assigned, yet the sign-in
  succeeded. Microsoft's AADSTS50105 troubleshooting page says why: *"The
  assignment requirement doesn't apply to Global Administrators."* The gate has
  to be tested with a **non-admin** account (the CA test user, RBAC row 11):
  first unassigned (expect AADSTS50105), then assigned (expect the page).
  The same bypass matters for the Conditional Access design, because admin
  accounts skip this gate.

**The gate, tested with a non-admin (2026-09-30).** Gerard created the RBAC row
11 user by CLI: `iip-ca-test@letter7.onmicrosoft.com`, display name **IIP CA
Test User (dev)**, a member with no directory role. The password was generated
locally, changed at first sign-in, and never recorded here or seen by Claude.
Users are created by CLI because a Graph Bicep user needs its password in the
template.
- **Unassigned:** sign-in refused with **AADSTS50105** ("…blocked because they
  are not a direct member of a group with access, nor had access directly
  assigned…"). **The assignment gate holds.**
- **Assigned:** `entra.bicep` gained the INTERIM row 10 assignment,
  `iip-ca-test` → **IIP Results (dev)** with Default Access (`00000000-…`),
  deployed as `m11-entra-20260930d`: Succeeded. `appRoleAssignedTo` shows
  exactly one row. Sign-in as `iip-ca-test` then **reached the Functions
  default page.**
- **Interim, by decision:** letter7 has no Entra licences (`subscribedSkus` is
  empty), so a group can't be assigned yet. On the P2 trial's day 1: assign
  **IIP Results Viewers (dev)**, add `iip-ca-test` to it, delete the direct
  assignment, and re-run both tests.

**The results page (2026-09-30).** `app.bicep` adds the app setting
`RESULTS_BLOB_ENDPOINT` (the endpoint of `stiipdevwus01`, read from the
resource). What-if: 6 modify, 24 no change, 11 Unsupported, 2 to ignore. The
new setting is visible in the `appsettings` block, which what-if always prints
whole, as additions. Deployed as `m11-results-setting-20260930`: Succeeded.
The code (`function/results_page.py` and two routes in `function_app.py`) was
deployed by `config-zip --build-remote true`: 14 files, "Deployment was
successful", and 3 functions registered.

**M11's sign-in half, seen working:** as `iip-ca-test` (a non-admin, assigned
directly), `/api/results` listed all 5 result files with topic, status and
verdicts, including one `error` row rendered with dashes. The detail page
for `item4-key-cutting-FLAW-brand/20260924T191158Z` showed the facts, the
three audit verdicts and the final drafted copy. **Qualifier:** the done-when
says "a group member". The interim is a direct assignment until the P2 trial
(see above).

**The group swap, P2 trial day 1 (2026-10-07). M11 closed.** Claude edited
`entra.bicep` and wrote the commands; Gerard ran every command and made both
decisions named here.
- **The deploy command**, recorded because no doc had it. From the repo root:
  ```powershell
  az deployment group create `
    --resource-group rg-iip-dev-wus-01 `
    --name <deployment-name> `
    --template-file ai-103/infrastructure/iip/entra.bicep `
    --parameters ai-103/infrastructure/iip/entra.bicepparam
  ```
- **`m11-entra-20261007a`: Succeeded.** It assigned **IIP Results Viewers
  (dev)** to the app (Default Access; assignment ID `IWuSisJl…`).
  `appRoleAssignedTo` then listed two rows: the Sep 30 User row and the new
  Group row (created 17:31:42Z).
- **The User row was deleted by CLI** (`az rest --method delete
  …/servicePrincipals/{sp}/appRoleAssignedTo/{id}`), because removing a
  resource from Graph Bicep never deletes it. **The test caught a missed
  step:** on the first pass the delete command wasn't run, the list still
  showed two rows, and `iip-ca-test` reached the page through the leftover
  User row (sign-in log: Success at 17:37:17Z, Correlation ID
  `9405e225-1618-4b63-8422-9ab5fa408aeb`). Run again, the list showed the
  Group only.
- **Gate test 1** (Incognito, with every Incognito window closed first, since
  Chrome shares one session across them): **AADSTS50105**, *"not a direct
  member of a group with access, nor had access directly assigned"*.
  Sign-in log: 2026-10-07T17:43:23Z, error 50105,
  Correlation ID `6a3aaa06-6190-441f-a6da-3f60416c8cdf`.
- **`m11-entra-20261007b`: Succeeded**, with the same assignment ID (updated
  in place). The group's `members` lists `iip-ca-test` with
  **`relationshipSemantics: 'replace'`** (Gerard's decision): the template is
  the whole membership, so a member added by hand is removed on the next
  deploy. The Graph default, `append`, only ever adds (Microsoft Learn, "Model
  relationships in Microsoft Graph Bicep types"). Owners stay on the default.
  `az ad group member list` shows exactly `iip-ca-test`.
- **Gate test 2:** `iip-ca-test` reached `/api/results` ("Signed in as IIP CA
  Test User (dev)"). Sign-in log: 2026-10-07T17:53:18Z, Success,
  Correlation ID `f3e78331-3d8e-421d-95dd-14383249ccc5`. **M11's done-when is met:** a group member can
  sign in and see the results.
- **Not tested:** what an existing group assignment does once P1/P2 lapses
  (the trial ends 2026-11-06). Tracked in Todoist, due Nov 2.

**Why a separate file:** Graph resources are extensible resources, and what-if
does not support them. Inside `main.bicep` they would sit unanalysed in the one
deployment whose what-if is registered line by line. Kept apart, `main.bicep`'s
register stays exact, and `entra.bicep` is verified by **reading the objects
back** (`az ad app show`, `az ad app federated-credential list`, `az ad sp
show`, `az ad group show`) against the template.

**Not in pass 2 step B, on purpose:** built-in authentication
(`Microsoft.Web/sites/config` `authsettingsV2`), attaching `-03` to the Function,
and the `OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID` app setting. Those are ARM, so
they go in `main.bicep` as step C, where what-if covers them. Step C takes the
app's client ID as a parameter (an `entra.bicep` output) rather than referencing
a Graph resource from `main.bicep`, which would drag an unsupported type into
the registered what-if.

## M12 — networking (written 2026-10-09 and 2026-10-10)

Claude wrote the Bicep to the design in `../../m12-prep.md`; Gerard made the
decisions (D-M12-1 to -7) and runs every what-if and deploy.

**One switch, `networkStage` in `dev.bicepparam`:** 0 = the free skeleton
(VNet, two subnets, two NSGs); 1 = + the private endpoints and DNS zones
(billed); 2 = + the Function in the VNet; 3 = + the storage firewall. All
four are written (stage 3 on 2026-10-10). Setting it lower never deletes anything (the default
deployment mode only adds and changes), so the teardown deletes the endpoints
and zones by CLI.

**New files:** `modules/network.bicep` (skeleton, always deployed) and
`modules/privatelink.bicep` (endpoints, zones, VNet links, zone groups; only
when `networkStage >= 1`). `main.bicep` passes the private-link module IDs
built with `resourceId()`, not module outputs, so what-if can analyse them on
the first run.

**Before the first deploy, once:** the Function subnet is delegated to
`Microsoft.App/environments`, so the `Microsoft.App` resource provider should
be registered in the subscription:
```powershell
az provider show --namespace Microsoft.App --query registrationState -o tsv
# only if that doesn't print Registered:
az provider register --namespace Microsoft.App --wait
```

**Expected stage 1 what-if** (written before the run): **11 to create**, and
the register otherwise unchanged (6 modify, 24 no change, 11 Unsupported, 2 to
ignore, per the Sep 30 totals):
- `nsg-func-iip-dev-wus-01`, `nsg-pep-iip-dev-wus-01`
- `vnet-iip-dev-wus-01` (both subnets inline, `defaultOutboundAccess: false`)
- `privatelink.blob.core.windows.net`, `privatelink.queue.core.windows.net`
- `…/link-vnet-iip-dev-wus-01` on each zone
- `pep-stiipdevwus01-blob`, `pep-stiipdevwus01-queue`
- `…/default` zone group on each endpoint

Any line not in that list or in the register is a finding, not noise.

**Stage 1, DEPLOYED 2026-10-09 (`m12-stage1-20261009`, Succeeded).** The
what-if matched exactly: 11 to create, 6 modify, 24 no change, 11 Unsupported,
2 to ignore. Checks (Gerard ran them): both endpoint connections **Approved**
on `stiipdevwus01`; `privatelink.blob…` holds `stiipdevwus01 → 10.20.0.36`,
`privatelink.queue…` holds `stiipdevwus01 → 10.20.0.37`; from the tower,
`stiipdevwus01.blob.core.windows.net` now resolves through
`stiipdevwus01.privatelink.blob.core.windows.net` but still to the public
`57.150.229.161`, so nothing changed outside the VNet. The cost clock started
here.

**Stage 2 (written 2026-10-09): the Function joins the VNet.** `app.bicep`
takes `virtualNetworkSubnetId`; `main.bicep` passes the Function subnet when
`networkStage >= 2`. **Expected what-if:** `func-iip-dev-wus-01` (already one
of the 6 modify) gains `+ properties.virtualNetworkSubnetId`. The 11 stage 1
resources are compared against live for the first time, so any read-back
noise on them is new and gets checked against the schema before it's
registered. **First stage 2 what-if (2026-10-09), read as data by Claude:** 13 modify,
28 no change, 11 Unsupported, 4 to ignore. The function app showed exactly
the registered lines plus `+ virtualNetworkSubnetId`. The 11 new resources:
- **Fixed, not accepted:** `- properties.privateEndpointVNetPolicies:
  "Disabled"` on the VNet and `- properties.resolutionPolicy: "Default"` on
  both zone links. Both writable (they compile in the schema), so now declared
  as found.
- **Registered:** `- properties.isIPv6EnabledPrivateEndpoint: false` on both
  endpoints. Not in the `2024-05-01` schema or any newer version this Bicep
  knows (BCP037/BCP081), so no template can declare it.
- **Registered:** on both zone groups, `- etag`, `- id`, `-
  properties.provisioningState`, `- type` inside `privateDnsZoneConfigs[0]`.
  All read-only.
- **2 new "to ignore":** `nic-pep-stiipdevwus01-blob` and `-queue`, the
  network cards Azure creates for the endpoints. Not in the template.
- **Expected after the fix:** 10 modify, 31 no change, 11 Unsupported, 4 to
  ignore.

**If the upload test fails after the deploy**, the quick way back
is `az functionapp vnet-integration remove -g rg-iip-dev-wus-01 -n
func-iip-dev-wus-01`.

**Stage 2, DEPLOYED 2026-10-09 (`m12-stage2-20261009`, Succeeded).** The
re-run what-if matched the prediction exactly: **10 modify, 31 no change, 11
Unsupported, 4 to ignore**. That is the register from now on. **Upload test:**
`item4-m12-stage2-20261009.png` → result `20261009T205847Z.json` in 42 s,
first delivery; status ok, run completed, all three tools ran (fact sheet,
evaluator, vision audit), copy passed first time, audit = item4's answer key
(saved as `scripts/results/20261009-205847_function_item4_m12_stage2.json`).
**So no NAT gateway is needed:** with all its traffic forced through a subnet
with `defaultOutboundAccess: false`, the Function still reaches Foundry, Entra
and its host storage. That's measured; the mechanism (Flex's platform
gateways keep their own way out) is Claude's inference. **Not yet proven:**
that its storage calls use the private endpoints. Stage 3's firewall proves
that.

**Stage 3 (written 2026-10-10): the storage firewall.** Claude wrote it;
Gerard made the two choices marked. `storage.bicep` takes `firewallEnabled`
(`main.bicep` passes `networkStage >= 3`) and `homeIpAddress`. At stage 3,
`networkAcls` becomes `defaultAction: Deny`, one `ipRules` entry for the home
IPv4 and `bypass: AzureServices` (Event Grid's delivery to `upload-events`).
Below stage 3 it keeps the M8 values exactly. `publicNetworkAccess: 'Enabled'`
is now declared at **every** stage: unset, its value since M8, behaves the
same, and adding it only at stage 3 with `union()` would have switched off
Bicep's type checking for the whole properties block (tested).
- **The home IP never enters the repo (D-M12-4).** `homeIpAddress` (7-15
  characters) is read from `IIP_HOME_IP` by `readEnvironmentVariable()` with no
  default, so it's **required at every stage** (Gerard): in a window where
  `.\set-home-ip.ps1` hasn't run, what-if and deploy fail at compile time and
  nothing reaches Azure. The script looks the address up live (`curl.exe -4`,
  api.ipify.org), checks it's IPv4, prints it and sets the variable for that
  window; **nothing is stored** (Gerard, amending D-M12-4's "untracked file").
  Tested by Claude with Bicep 0.48.1: unset → BCP427, empty → BCP333, an IPv6
  address → BCP332. Bicep evaluates `readEnvironmentVariable()` even inside an
  untaken ternary branch, which is why "required only at stage 3" would have
  needed a placeholder value.
- **Lockout is bounded.** The firewall gates data (blob, queue), not Azure
  Resource Manager, so a wrong IP never blocks a what-if or a redeploy at
  stage 2.
- **Expected what-if** (written before the run): `stiipdevwus01` moves from No
  change to **Modify**: `~ networkAcls.bypass: "None" => "AzureServices"`,
  `~ networkAcls.defaultAction: "Allow" => "Deny"`, `networkAcls.ipRules` gains
  one entry (the home IP), and `+ publicNetworkAccess: "Enabled"` (missing if the
  live account already reports it). Totals **11 modify, 30 no change, 11
  Unsupported, 4 to ignore**. Any other line is a finding.
- **The what-if output contains the home IP.** Save it outside the repo
  (`$env:TEMP`), and redact the address before quoting it in any doc.

**Stage 3, DEPLOYED 2026-10-10 (`m12-stage3-20261010`, Succeeded).** The
what-if (saved as JSON outside the repo, read entry by entry by Claude) matched
the prediction exactly: **11 modify, 30 no change, 11 Unsupported, 4 to
ignore**, 0 diagnostics. `stiipdevwus01` showed only bypass, defaultAction,
`+ ipRules` (one entry) and `+ publicNetworkAccess: "Enabled"`, so the live
account had not reported it; every other line was already registered. **That
is the register from now on.** Tests (Gerard ran them; Claude read the results):
- **(a) Regression upload, PASS.** `item4-m12-stage3-20261010.png`, uploaded
  from the tower at 17:25:25Z → result `20261010T172611Z.json` in 46 s, first
  delivery; status ok, run completed, all three tools ran, copy passed first
  time, audit = item4's answer key, the same contrast figures as stage 2 (saved
  as `scripts/results/20261010-172611_function_item4_m12_stage3.json`).
- **(b) Results page on the phone, PASS** (`iip-ca-test`, passkey): the new
  result is listed and opens.
- **(c) Negative control, PASS.** From Azure Cloud Shell (outbound IP not the
  home address), `az storage blob list ... --container-name uploads` was
  refused, and the CLI blamed the account's network rules. The same command
  with the same identity from the tower listed the container (a first run
  went to Git Bash on the tower by mistake, and became the positive control).
- **(d) M3 `--blob`, FAILS, as predicted.** `400 InvalidRequest`, inner
  `ContentSourceNotAccessible`: "Error occurred while trying to read from the
  content source." Content Understanding fetches the user-delegation SAS link
  from Microsoft's network, which the firewall refuses; a SAS link isn't a
  trusted-service path. **Control:** `--file` (the same PDF sent inline) passed
  all 5 steps (`20261010-105147`). **While the firewall is on, use `--file`.**
- **Found on the way (Claude):** `m3_analyze.py` printed only "400 Bad
  Request". Its comment said `raise_for_status()` "raises with the real error
  body"; it doesn't. `_raise_with_body()` now carries the body in the error.

**What stage 3 proves:** with the account closed to everyone but the home IPv4
and trusted services, the Function still reads and writes `uploads`, `results`
and `upload-events`. It isn't the home IP and it isn't a trusted service, so
it can only be using the private endpoints. Event Grid's delivery (trusted
service, system-assigned identity) also works.

## Load-bearing lines — do not edit casually

**`foundryCustomSubDomainName = 'aif-iip-dev-wus-01'`** (`dev.bicepparam`).
The account is named `aif-dev-wus-01` — the documented CAF exception — but the
subdomain carries the `iip` token, and every endpoint the `scripts/` tooling
calls is built from the subdomain, not the resource name. Left to default, ARM
derives it from the account name, the endpoint host changes, and every script
fails at once with errors that point nowhere near the cause.

**`sku.name = 'free'`** (`modules/search.bicep`). An Azure AI Search tier
cannot be changed after creation — free to basic or standard means delete and
recreate the service.

*Corrected 2026-09-21, same day: an earlier draft of this file said that would
"destroy the indexes M5 built". That overstated it.* `scripts/m5_index.py`
creates the index and uploads from a tracked source document
(`iip-docs/Loan_Agreement_Promissory_Note-CUPortal-Custom-Schema.json`), so a
recreate is a script re-run costing embedding calls, not lost work. The real
constraints of the free tier are: **no private endpoint support** (so Search
can never sit behind one while it stays free — M12 does not currently ask it
to), 3 indexes, 50 MB, fixed at 1 replica and 1 partition, and no SLA.

**`versionUpgradeOption: 'OnceCurrentVersionExpired'`** on every model
deployment (`dev.bicepparam`, decided by Gerard 2026-09-24). Until then
`modules/foundry.bicep` hardcoded `OnceNewDefaultVersionAvailable`, the portal
default that M8 described rather than chose. It sat right next to a pinned
`modelVersion`, so the template said two contradictory things: pin this build,
and move off it whenever a new default ships. gpt-5-4 is both the drafter and
the judge, and its value is longitudinal comparison. So the build now moves only
at retirement, never on a new default. `NoAutoUpgrade` was rejected because the
deployment **stops working** at retirement. A forced move is still detectable,
because `model_builds` provenance records the build on every measured run since
2026-09-23. **Note:** Azure CLI cannot update this property (Microsoft Learn,
*Working with models*). Bicep or REST can.
**Pending apply:** until the next deployment, `what-if` shows
`~ properties.versionUpgradeOption` on all four deployments. That is this
intended change, not a register entry, and it should be gone after the deploy.

**`@batchSize(1)`** on the model deployment loop (`modules/foundry.bicep`).
Cognitive Services rejects concurrent writes to deployments on one account.
Deployed in parallel they fail intermittently, which reads as a flaky template
rather than a documented constraint.

## Deliberately not declared

| Property | Why | Owner |
|---|---|---|
| `storage/allowSharedKeyAccess` | unset on the live account (keys enabled) | **Decide at M11, alongside `disableLocalAuth`** *(was "M10"; moved 2026-09-24. Nothing in `scripts/` uses an account key since `08bc35c`; `--blob` signs with a user delegation key)* |
| `foundry/disableLocalAuth` | unset on the live account | **Decide at M11** *(was "M10"; moved 2026-09-24, see `phase2-orientation.md` Phase 2 Backlog — the VS Code poll is the one known consumer left)* |
| `keyvault/enablePurgeProtection` | off, and cannot be undone once on — stays a decision, never a side effect | explicit decision only |
| `storage/networkAcls.resourceAccessRules` | Defender for Storage injects its own `storageDataScanner` rule; a template that owns this array fights the security provider on every deploy | not ours |
| `storage/allowCrossTenantDelegationSas` | `false`, which is the default, and absent from the `2023-05-01` schema | — |

## Settled question — `searchServices/properties.endpoint`

`properties.endpoint` is not flagged `ReadOnly` in the `2025-05-01` schema, so
by the rule used everywhere else in this register it should have been declared.
It was not, on the reasoning that a search endpoint is derived from the service
name and cannot be chosen.

**The M9 deployment settled it on 2026-09-21: the endpoint is unchanged.** The
reasoning held, the missing `ReadOnly` flag is a schema inaccuracy, and this is
now a verified fact rather than an argument.

Recording how the call was made, because the method generalises better than the
answer: the decision rested on asymmetry, not confidence. If the reasoning were
wrong, a derived URL is regenerated to an identical value. If the property had
been declared and the reasoning were wrong the other way, the template would
carry a hardcoded literal that goes stale silently after any rename. When a
property's writability is genuinely ambiguous, prefer the error that self-corrects.

## Caveat — this is not a recovery template

`associatedProjects` on the account names a project the same template creates
beneath it. That is correct for a baseline over resources that already exist.
On an empty resource group it is a chicken-and-egg and the account would need
deploying twice. M8 does not claim otherwise.

## Inputs

`live-resources.json.output` and `live-deployments.json.output` are the raw ARM
dumps this baseline was written from. Both are gitignored via `*.json.output`.
Regenerate them before re-baselining rather than trusting this file's dates.
