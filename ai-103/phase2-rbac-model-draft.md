# Phase 2 — RBAC model (on paper)

**Status: DESIGN AGREED ON PAPER, 2026-09-16.** This is the first item on
the Phase 2 entry checklist. Claude drafted it from the app design Gerard
chose on Sep 16 and from Microsoft Learn. **Gerard took option (a) on all
seven decisions (D1–D7) and ruled that new resources follow CAF naming,
even where existing names do not.** Rows marked **VERIFY** are what the docs
say and must be confirmed with a real call at build time. Nothing here is
deployed.

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

**Naming rule (Gerard, Sep 16): new resources follow CAF**, using
`{abbreviation}-{workload}-{env}-{region}-{instance}`. Storage accounts use
the same parts without hyphens. The abbreviations come from CAF's "Abbreviation
recommendations for Azure resources" page, checked on Sep 16. Existing
names that don't fit (`aif-dev-wus-01` has no workload token) are not
renamed; renaming would mean recreating the resources. Where two resources
of the same type differ only in purpose, the instance number tells them
apart and a `purpose` tag says what each is for. The tags on every new
resource are `owner`, `env`, `region`, `managed-by:bicep`, `project:iip` and
`purpose`.

| Resource | Status | Name | CAF abbreviation |
|---|---|---|---|
| Resource group | exists | `rg-iip-dev-wus-01` | `rg` |
| Foundry account / project | exists | `aif-dev-wus-01` / `proj-iip-dev-wus-01` | `aif` / `proj` |
| App data storage (containers `uploads`, `results`) | exists (new containers) | `stiipdevwus01` | `st` |
| Key Vault | exists | `kv-iip-dev-wus-01` | `kv` |
| Function app | planned | `func-iip-dev-wus-01` | `func` |
| Flex Consumption plan | planned | `asp-iip-dev-wus-01` | `asp` |
| Function host storage (D3) | planned | `stiipdevwus02` (purpose: function-host) | `st` |
| Function managed identity (D2) | planned | `id-iip-dev-wus-01` (purpose: function-runtime) | `id` |
| CI/CD managed identity (D6) | planned | `id-iip-dev-wus-02` (purpose: github-deploy) | `id` |
| Application Insights | planned | `appi-iip-dev-wus-01` | `appi` |
| Log Analytics workspace | planned | `log-iip-dev-wus-01` | `log` |
| Event Grid system topic (blob events) | planned | `egst-iip-dev-wus-01` | `egst` |

**Entra ID objects are outside CAF,** which only covers Azure resources.
Their proposed names are:
- the app registration for the results page: **IIP Results (dev)**;
- the viewers group: **IIP Results Viewers (dev)**.

These are display names, not resource names. An earlier draft of this page
used an `app-` prefix for the app registration. It was dropped, because
`app` is CAF's abbreviation for a web app and would have implied a resource
that doesn't exist.

## Role assignments

| # | Identity | Scope | Role | Why |
|---|---|---|---|---|
| 1 | Gerard (admin user) | Subscription **and two management groups** | Owner, plus Contributor at the tenant root *(all existing)* | Single-admin lab: creates resources and assigns roles. **A documented exception — see D1, which was corrected on 2026-09-21 because it understated this.** |
| 2 | Gerard | `aif-dev-wus-01` | Foundry User | Keyless local development runs (`DefaultAzureCredential`). Probably assigned automatically when the project was created; check before adding. |
| 3 | Gerard | `stiipdevwus01` | Storage Blob Data Contributor | Upload test inputs and read results once shared-key access is off. Owner is a control-plane role only and does **not** grant blob data access. |
| 4 | Function identity `id-iip-dev-wus-01` | `aif-dev-wus-01` | Foundry User | Runs the agent. The tools also make direct model calls: the judge (gpt-5-4), the image audit (gpt-5-4-mini) and Vision Read. Foundry Agent Consumer alone would cover calling the agent but not those model calls. **VERIFY** that Foundry User covers Vision Read and the Evaluation SDK. D5: scoped to the account. |
| 5 | Function identity | `stiipdevwus01` / `uploads` | Storage Blob Data Reader | Reads the blob that triggered the run. **VERIFY:** the identity-based blob-trigger docs list Blob Data Owner + Queue Data Contributor on the trigger's connection account. Try container-scoped Reader first, and widen only if the trigger fails. Record what was actually required. |
| 6 | Function identity | `stiipdevwus01` / `results` | Storage Blob Data Contributor | Writes results; the results page lists and reads them. |
| 7 | Function identity | Host storage `stiipdevwus02` | Storage Blob Data Owner, Storage Queue Data Contributor | Needed by the Functions host (`AzureWebJobsStorage`) and for the deployment package. Microsoft Learn also lists Storage Account Contributor when blob triggers are used. That is a broad control-plane role, so **VERIFY** it is really needed before assigning it. |
| 8 | Function identity | `appi-iip-dev-wus-01` | Monitoring Metrics Publisher | Telemetry authenticated with Entra ID, so Application Insights can also disable local auth. |
| 9 | Foundry project identity | `aif-dev-wus-01` | Foundry User *(automatic)* | Microsoft's minimum assignment. M7's tools run client-side, in the Function, so the project identity needs **nothing** on storage. |
| 10 | Group **IIP Results Viewers (dev)** | Enterprise app **IIP Results (dev)** | App assignment, with "Assignment required" = Yes | Only group members can sign in. **No Azure RBAC.** |
| 11 | CA test user | Member of row 10's group | — | The subject for Conditional Access in report-only mode, then enforced. |
| 12 | CI/CD identity `id-iip-dev-wus-02` (D6: in scope) | `func-iip-dev-wus-01` | Website Contributor | GitHub Actions deploys code over OIDC (federated credential). No stored secret, and no rights outside the Function app. |

## Build-time findings (M9, 2026-09-21)

This page promised that **VERIFY** rows and guesses would be confirmed with a
real call at build time. They were. Four corrections:

- **Row 9 is NOT automatic.** This page said "Foundry User *(automatic)* —
  Microsoft's minimum assignment." `az role assignment list` on
  `aif-dev-wus-01` returned **nothing** before M9. Microsoft Learn explains it:
  the automatic assignment happens only when the resource is created through the
  portal or Foundry UI, and "doesn't apply when deploying Foundry from SDK or
  CLI" — which is how this account was built. So the project managed identity
  had been running since July without one of the two assignments Microsoft calls
  the minimum. M7 never noticed, because its tools authenticate with account keys
  and the orchestrator runs as Gerard. **M10 would have walked into this**: the
  keyless migration removes the keys that were hiding it. Assigned by M9.
- **Row 3 already existed.** Gerard held Storage Blob Data Contributor at
  account scope on `stiipdevwus01` before M9. It is therefore NOT declared in
  `infrastructure/iip/modules/rbac.bicep` — Azure enforces uniqueness on the
  (principal, role, scope) triple, so declaring it under a generated name would
  have failed the deployment with `RoleAssignmentExists`. Row 3 is satisfied,
  just not by the template.
- **Row 2 is redundant today, and declared anyway.** Gerard holds Foundry User
  at **subscription** scope, which inherits to the account and is how
  `m7_orchestrator.py` authenticates keylessly. The account-scope grant adds
  nothing right now. Declared deliberately (Gerard, Sep 21) so the narrow grant
  lives in IaC and tightening the subscription later cannot silently break local
  development. Removing the subscription-scope grant is tracked in
  `phase2-orientation.md`'s Phase 2 Backlog, **after M10** — until then the broad
  grant is the load-bearing one.
- **Gerard also holds Storage Blob Delegator** on `stiipdevwus01`, which is not
  in the table above. It grants user-delegation SAS keys. Harmless, left alone,
  recorded so the next audit does not treat it as a surprise.

**Verified after deployment.** All five declared rows (2, 4, 5, 6, 9) exist at
the intended scope with the intended role and principal. Rows 5 and 6 are at
**container** scope, not account scope, as principle 2 requires. Rows 7, 8 and 12
are deferred to M11, which creates the resources they point at; `id-iip-dev-wus-02`
exists already, so row 12 is a one-line addition then.

**Still VERIFY, and still open:** whether Foundry User covers Vision Read and the
Evaluation SDK (row 4) — that needs a real keyless call, which is M10; and
whether container-scoped Blob Data Reader is enough for the event-based blob
trigger (row 5), which needs the trigger, so M11.

## Deliberately given nothing

- **Key Vault:** no data-plane assignments are planned, because nothing
  keyless needs a secret. D7: Key Vault is kept, empty on purpose, and still uses RBAC authorization.
- **No workload identity** holds Contributor or Owner anywhere.
- **Viewers** hold no Azure roles (principle 3).
- **AI Search** (`srch-iip-dev-wus-01`, from M5) is not used by the Phase 2
  app, so no assignments are made there.

## Decisions (Gerard chose option (a) on all seven, Sep 16)

| ID | Question | Options; **(a) was chosen for every one** |
|---|---|---|
| D1 | Your admin posture | (a) **Chosen.** Keep the existing standing access and document it as a single-admin exception. PIM is the enterprise answer and is out of scope. **See the correction below — what (a) actually keeps is broader than this row originally said.** (b) Day to day: Contributor plus **Role Based Access Control Administrator**, restricted to the roles in this table, at resource-group scope. Owner is kept only as break-glass. |
| D2 | Function identity type | (a) **User-assigned.** Bicep can create it and assign roles before the app exists, and it survives the app being recreated. (b) System-assigned: simpler, but tied to the app's lifetime. |
| D3 | Function host storage | (a) **Separate account.** It keeps the broad host roles (row 7) off the app data account. (b) Reuse `stiipdevwus01`: one less resource, but row 7's roles would land on the data account. |
| D4 | Where the results page runs | (a) An HTTP-triggered function on the same Function app, with built-in App Service Authentication: one compute resource. **VERIFY** that Flex Consumption supports it. (b) A separate App Service (Basic tier or higher), billed hourly. |
| D5 | Foundry role scope | (a) The account, which is what Microsoft Learn's minimum assignments use. (b) The project, which is narrower; confirm that model and Vision calls still work. |
| D6 | CI/CD in Phase 2? | (a) Yes: row 12, with GitHub OIDC. AI-103 names CI/CD integration. (b) Later: deploy from your account for now. |
| D7 | Key Vault after the keyless migration | (a) Keep it, still using RBAC authorization, for any third-party secret that comes up later, and document that it is empty on purpose. (b) Retire it. |

## D1 correction — the actual admin posture (2026-09-21)

**D1 originally described the exception as "keep subscription Owner."** Read from
`az role assignment list --assignee <gerard> --all` on 2026-09-21, the standing
access is broader:

| Role | Scope | Note |
|---|---|---|
| Owner | subscription `343a8a7e-…` | what D1 described |
| **Owner** | **management group `Non-Prod`** | not previously documented |
| **Contributor** | **management group `e0249b00-…`** — the tenant root | not previously documented |
| Foundry User | subscription | inherits to `aif-dev-wus-01`; how `m7_orchestrator.py` authenticates keylessly today |
| Storage Blob Data Contributor | `stgeostewus301` (portfolio prod) | outside this model's scope |
| Key Vault Secrets Officer | `kv-geoste-prod-wus3-01` (portfolio prod) | outside this model's scope |
| Storage Blob Data Contributor + Storage Blob Delegator | `stiipdevwus01` | row 3, plus the Delegator grant |

**Two of those are wider than subscription Owner.** Management-group Owner covers
every subscription under `Non-Prod`, and root-level Contributor reaches the whole
tenant.

**Nothing was changed.** For a lab with one administrator this access is
reasonable and the alternative — PIM, or day-to-day Contributor with a break-glass
Owner — is explicitly out of scope per D1(b). **The correction is to the
documentation, not the permissions.** The reason it matters: this page is resume
material, and a governance document that understates the privilege it exists to
disclose is worse than one that does not mention privilege at all. The point of
writing D1 down was to show the exception was deliberate; that only holds if the
exception described is the one actually held.

**Not on the Phase 2 Backlog as work.** There is nothing to do beyond this
section. The one related backlog item — removing the subscription-scope
`Foundry User` grant after M10 — is a narrowing that principle 2 calls for, and is
tracked separately in `phase2-orientation.md`.

## Open questions that affect this model

These are not waiting on Gerard today. They are recorded here so they are
not lost, and each one says when it gets acted on.

- **Event Grid–based blob trigger and inbound restrictions. This needs
  Gerard's decision at the networking design step, which comes before any
  private endpoint is built.** Microsoft
  Learn says this trigger does not work with inbound access restrictions on
  the Function, unless events are delivered using a managed identity. That
  choice changes the networking design (private endpoints), so it has to be
  settled before the Function's inbound access is locked down.
- **Migration order. This is a build-time rule, and no decision is
  needed.** Assign every role in this table first, migrate the
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
