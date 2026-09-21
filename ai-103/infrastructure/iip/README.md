# IIP dev — Bicep baseline (M8)

Bicep describing `rg-iip-dev-wus-01` **as it already exists**. This is not a
greenfield deployment and not a disaster-recovery template (see the caveat at
the bottom). Its job is to make `az deployment group what-if` boring, so that
a real change stands out against a known-quiet background.

Baselined from the live resources on **2026-09-21**.

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
| `srch-iip-dev-wus-01` | `- properties.endpoint` | Not flagged `ReadOnly`, but a search endpoint is not choosable — it is always `https://{serviceName}.search.windows.net`. Treated as a schema inaccuracy. See "Open question" below. |
| `srch-iip-dev-wus-01` | `+ tags.managed-by: "bicep"` | **Intended.** Real drift: the other four resources carry this tag and Search did not. Disappears after the first deployment. |

Storage also shows `x properties.encryption.services` (Noeffect). That symbol
means ARM accepts the property and it changes nothing. The resource itself
reports `=` No change.

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

**`@batchSize(1)`** on the model deployment loop (`modules/foundry.bicep`).
Cognitive Services rejects concurrent writes to deployments on one account.
Deployed in parallel they fail intermittently, which reads as a flaky template
rather than a documented constraint.

## Deliberately not declared

| Property | Why | Owner |
|---|---|---|
| `storage/allowSharedKeyAccess` | unset on the live account (keys enabled) | **M10** |
| `foundry/disableLocalAuth` | unset on the live account | **M10** |
| `keyvault/enablePurgeProtection` | off, and cannot be undone once on — stays a decision, never a side effect | explicit decision only |
| `storage/networkAcls.resourceAccessRules` | Defender for Storage injects its own `storageDataScanner` rule; a template that owns this array fights the security provider on every deploy | not ours |
| `storage/allowCrossTenantDelegationSas` | `false`, which is the default, and absent from the `2023-05-01` schema | — |

## Open question

`searchServices/properties.endpoint` is not flagged `ReadOnly` in the
`2025-05-01` schema, so by the rule used everywhere else in this register it
should be declared. It is not, on the reasoning that the endpoint is derived
from the service name and cannot be chosen.

That is reasoning, not a verified read. The asymmetry is what decided it: if
the reasoning is wrong, a derived URL is regenerated to an identical value; if
the property were declared and the reasoning were wrong in the other direction,
the template would carry a hardcoded literal that goes stale silently. The
first real deployment settles it, and the current value is recorded above so a
change would be visible.

## Caveat — this is not a recovery template

`associatedProjects` on the account names a project the same template creates
beneath it. That is correct for a baseline over resources that already exist.
On an empty resource group it is a chicken-and-egg and the account would need
deploying twice. M8 does not claim otherwise.

## Inputs

`live-resources.json.output` and `live-deployments.json.output` are the raw ARM
dumps this baseline was written from. Both are gitignored via `*.json.output`.
Regenerate them before re-baselining rather than trusting this file's dates.
