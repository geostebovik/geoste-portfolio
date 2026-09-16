# Phase 2 — RBAC model (on paper)

**Status: DRAFT, 2026-09-16.** This is the first item on the Phase 2 entry
checklist. Claude drafted it from the app design Gerard chose on Sep 16 and
from Microsoft Learn. Gerard owns the design decisions, which are marked
**DECIDE**. Rows marked **VERIFY** are what the docs say and must be
confirmed with a real call at build time. Nothing here is deployed.

## The app this model is for

A topic and thumbnail are uploaded to Blob storage, which triggers an Azure
Function (Flex Consumption plan). The Function runs the M7 agent and writes
the results to Blob. A small results page, behind an Entra ID sign-in, lists
the results. Conditional Access is enforced on that sign-in during a timed
Entra ID P2 trial.

## Principles

1. **Keyless.** Every workload identity uses a managed identity and RBAC.
   There are no account keys or connection strings. Once the migration is
   done, `disableLocalAuth` is set on the Foundry account and shared-key
   access is turned off on storage. Key Vault ends up with little or nothing
   to hold, and that is the intended result.
2. **Narrowest role at the narrowest scope.** Container before account,
   resource before resource group. Data roles, not Contributor.
3. **People get no Azure data access through the app.** Viewers sign in to
   the page. The page reads results through the Function's identity, so
   viewers never hold an Azure role.
4. **Foundry uses the Foundry roles.** Microsoft Learn says not to assign
   `Cognitive Services *` roles or `Azure AI Developer` for Foundry work. The
   Foundry roles were recently renamed; for example, **Foundry User** was
   **Azure AI User**, with the same role ID.

## Resources

| Resource | Status | Name |
|---|---|---|
| Resource group | exists | `rg-iip-dev-wus-01` |
| Foundry account / project | exists | `aif-dev-wus-01` / `proj-iip-dev-wus-01` |
| App data storage (containers `uploads`, `results`) | exists (new containers) | `stiipdevwus01` |
| Key Vault | exists | `kv-iip-dev-wus-01` |
| Function app + Flex Consumption plan | planned | `func-iip-dev-wus-01` / `asp-iip-dev-wus-01` (**DECIDE** names) |
| Function host storage | planned | `stiipfuncdevwus01` (**DECIDE** D3) |
| User-assigned managed identity for the Function | planned | `id-iip-dev-wus-01` (**DECIDE** D2) |
| Application Insights + Log Analytics | planned | `appi-iip-dev-wus-01` / `log-iip-dev-wus-01` |
| Event Grid system topic (blob events) | planned | `evgt-iip-dev-wus-01` |
| Entra app registration for the results page | planned | `app-iip-results-dev` (not an ARM resource) |
| Entra group for viewers | planned | `grp-iip-results-viewers` |

## Role assignments

| # | Identity | Scope | Role | Why |
|---|---|---|---|---|
| 1 | Gerard (admin user) | Subscription | Owner *(existing)* | Single-admin lab: creates resources and assigns roles. **A documented exception, see D1.** |
| 2 | Gerard | `aif-dev-wus-01` | Foundry User | Keyless local development runs (`DefaultAzureCredential`). Probably assigned automatically when the project was created; check before adding. |
| 3 | Gerard | `stiipdevwus01` | Storage Blob Data Contributor | Upload test inputs and read results once shared-key access is off. Owner is a control-plane role only and does **not** grant blob data access. |
| 4 | Function identity | `aif-dev-wus-01` | Foundry User | Runs the agent. The tools also make direct model calls: the judge (gpt-5-4), the image audit (gpt-5-4-mini) and Vision Read. Foundry Agent Consumer alone would cover calling the agent but not those model calls. **VERIFY** that Foundry User covers Vision Read and the Evaluation SDK. **DECIDE** D5 (account or project scope). |
| 5 | Function identity | `stiipdevwus01` / `uploads` | Storage Blob Data Reader | Reads the blob that triggered the run. **VERIFY:** the identity-based blob-trigger docs list Blob Data Owner + Queue Data Contributor on the trigger's connection account. Try container-scoped Reader first, and widen only if the trigger fails. Record what was actually required. |
| 6 | Function identity | `stiipdevwus01` / `results` | Storage Blob Data Contributor | Writes results; the results page lists and reads them. |
| 7 | Function identity | Host storage | Storage Blob Data Owner, Storage Queue Data Contributor | Needed by the Functions host (`AzureWebJobsStorage`) and for the deployment package. Microsoft Learn also lists Storage Account Contributor when blob triggers are used. That is a broad control-plane role, so **VERIFY** it is really needed before assigning it. |
| 8 | Function identity | `appi-iip-dev-wus-01` | Monitoring Metrics Publisher | Telemetry authenticated with Entra ID, so Application Insights can also disable local auth. |
| 9 | Foundry project identity | `aif-dev-wus-01` | Foundry User *(automatic)* | Microsoft's minimum assignment. M7's tools run client-side, in the Function, so the project identity needs **nothing** on storage. |
| 10 | `grp-iip-results-viewers` | Enterprise app `app-iip-results-dev` | App assignment, with "Assignment required" = Yes | Only group members can sign in. **No Azure RBAC.** |
| 11 | CA test user | Member of row 10's group | — | The subject for Conditional Access in report-only mode, then enforced. |
| 12 | CI/CD identity *(if in scope, D6)* | `func-iip-dev-wus-01` | Website Contributor | GitHub Actions deploys code over OIDC (federated credential). No stored secret, and no rights outside the Function app. |

## Deliberately given nothing

- **Key Vault:** no data-plane assignments are planned, because nothing
  keyless needs a secret. **DECIDE** D7: what, if anything, stays in it.
- **No workload identity** holds Contributor or Owner anywhere.
- **Viewers** hold no Azure roles (principle 3).
- **AI Search** (`srch-iip-dev-wus-01`, from M5) is not used by the Phase 2
  app, so no assignments are made there.

## Decisions for Gerard

| ID | Question | Options (Claude's lean first) |
|---|---|---|
| D1 | Your admin posture | (a) Keep subscription Owner and document it as a single-admin exception. PIM is the enterprise answer and is out of scope. (b) Day to day: Contributor plus **Role Based Access Control Administrator**, restricted to the roles in this table, at resource-group scope. Owner is kept only as break-glass. |
| D2 | Function identity type | (a) **User-assigned.** Bicep can create it and assign roles before the app exists, and it survives the app being recreated. (b) System-assigned: simpler, but tied to the app's lifetime. |
| D3 | Function host storage | (a) **Separate account.** It keeps the broad host roles (row 7) off the app data account. (b) Reuse `stiipdevwus01`: one less resource, but row 7's roles would land on the data account. |
| D4 | Where the results page runs | (a) An HTTP-triggered function on the same Function app, with built-in App Service Authentication: one compute resource. **VERIFY** that Flex Consumption supports it. (b) A separate App Service (Basic tier or higher), billed hourly. |
| D5 | Foundry role scope | (a) The account, which is what Microsoft Learn's minimum assignments use. (b) The project, which is narrower; confirm that model and Vision calls still work. |
| D6 | CI/CD in Phase 2? | (a) Yes: row 12, with GitHub OIDC. AI-103 names CI/CD integration. (b) Later: deploy from your account for now. |
| D7 | Key Vault after the keyless migration | (a) Keep it, still using RBAC authorization, for any third-party secret that comes up later, and document that it is empty on purpose. (b) Retire it. |

## Open questions that affect this model

- **Event Grid–based blob trigger and inbound restrictions.** Microsoft
  Learn says this trigger does not work with inbound access restrictions on
  the Function, unless events are delivered using a managed identity. That
  choice changes the networking design (private endpoints), so it has to be
  settled before the Function's inbound access is locked down.
- **Migration order.** Assign every role in this table first, migrate the
  scripts to keyless, and re-run the acceptance test. Only then set
  `disableLocalAuth` on the Foundry account and turn off shared-key access
  on storage. Doing it in any other order breaks the key-based scripts
  mid-migration.

## Sources (Microsoft Learn, 2026-09-16)

- Role-based access control for Microsoft Foundry (built-in roles, minimum
  assignments)
- Use identity-based connections with Azure Functions; Azure Functions
  storage considerations (Flex Consumption); Blob storage trigger
- Disable local authentication in Foundry Tools
