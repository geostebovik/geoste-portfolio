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
| `stiipdevwus01/blobServices/default` | `- properties.deleteRetentionPolicy` | **Fixed, not accepted.** M9 declared `blobServices/default` with no properties, and `deleteRetentionPolicy` is writable — the same class of real diff as `defaultProject` in M8. Now declared as found (`enabled: false`). Should not reappear. **It partly did, 2026-09-24:** `- deleteRetentionPolicy.allowPermanentDelete: false`. That sub-property is writable too, so it's now declared as found. The record can't tell whether it was there after M9's deploy or appeared later. |
| `stiipdevwus01/.../containers/uploads`, `/results` | `- properties.defaultEncryptionScope`, `.denyEncryptionScopeOverride` | **Fixed, not accepted (2026-09-24).** Both are writable in the provider schema, and M9 declared the containers with only `publicAccess`. Now declared as found (`$account-encryption-key`, `false`). Should not reappear. |

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
