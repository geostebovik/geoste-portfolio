# Session Summary — AZ-104 Phase 4 Completion + ostebovik.net Portfolio Build

> **Scope:** Projects 14 & 15 (Capstone) completion + design and live deployment of production portfolio site at ostebovik.net.  
> **Merge target:** Master reference document combining all session summaries.

---

## 1. AZ-104 Lessons Learned / Gotchas

### CLI Command Structure
- **`az web create appserviceplan` is wrong.** Correct: `az appservice plan create`. Correct: `az webapp create`. Pattern is always `az {service} {noun} {verb}`.
- **`--help` is your primary reference.** `az appservice plan create --help` and `az webapp create --help` show all flags, required vs optional, and examples — faster than googling, always matches your installed CLI version.
- **`--is-linux` is required** for Linux App Service Plans. The SKU alone (`P0v3`) does not imply the OS. Missing this flag will silently deploy a Windows plan.
- **`--assign-identity "[system]"` at creation time** is the correct pattern for provisioning system-assigned managed identity on a Web App. Assigning after creation introduces a timing window where you may attempt RBAC assignment before the identity GUID exists.
- **`--sku` alone is sufficient** for App Service Plan — `--tier` is redundant and not a valid flag.

### Naming Issues
- **Typo: `rg-az104-dev-wus3-o1`** (letter "o") instead of `rg-az104-dev-wus3-01` (zero). Will silently create or fail on a wrong RG. Always verify `01` vs `o1` in resource names.
- **`app-dev-wus-01` vs `app-dev-wus3-01`** — missing the region digit `3`. Produces a 404 or creates a resource in the wrong name.
- **`kv-dev-wus3-01` vs `kv-az104-dev-wus3-01`** — Key Vault retained the `az104` segment from earlier naming convention. Always confirm actual deployed names vs notes.
- **`acrdevwus301` vs `acraz104devwus301`** — ACR was deployed without the `az104` workload segment. Notes were inaccurate; actual deployed name wins.
- **Storage accounts are globally unique across all of Azure.** `stprodwus301` and `stgeostwus301` were already taken by other tenants. Final working name: `stgeostewus301`. Add owner-specific prefix to all storage names.
- **Key Vault soft delete is on by default.** Deleted secrets are retained 7 days. You cannot immediately reuse a secret name after deletion — plan secret names accordingly.

### PowerShell / Bash Variable Capture
- **PowerShell subexpression syntax:** `$VAR = $(az command --query field -o tsv)` — not `$VAR=$OBJECT.output.field`.
- **`--query` + `-o tsv` are required** to extract a single value cleanly from JSON output. Without them you get a full JSON blob that cannot be stored in a variable.
- **Triple-P typo:** `$APPP_PRINCIPAL` (three P's) will silently fail when referenced later. Spell variable names carefully.
- **Backtick (`` ` ``) for PowerShell line continuation; backslash (`\`) for Bash.** Do not mix these — Git Bash / WSL on Windows will sometimes interpret backtick-continued commands incorrectly.

### Azure Behaviors
- **Local Bash in VS Code can corrupt Azure CLI commands** involving long resource IDs passed as flag values (Windows path interpolation). Use Azure Cloud Shell for `az monitor diagnostic-settings create` and similar commands with long ID arguments.
- **`identity_claim_oid_g` KQL column** is not present in all LAW versions. Safer query: `project TimeGenerated, CallerIPAddress, OperationName, ResultType`.
- **KV diagnostic logs take 5–15 minutes** to appear in Log Analytics after the diagnostic setting is created. Trigger a `az keyvault secret show` read, wait, then rerun KQL.
- **App Gateway must be stopped (not deleted) to stop billing** unless you are fully done with it. Public IP addresses bill independently even when the AppGW is stopped — delete the PIP separately.
- **Azure Bastion Standard SKU** bills ~$0.19/hr even when not actively used. Delete when the lab phase is complete.
- **`skipGithubActionWorkflowGeneration: false`** in Bicep SWA resource requires Azure to have write access to GitHub at deployment time. If the repo wasn't connected during deployment, the workflow file is never created — must be added manually.

### Bicep Behaviors
- **Front Door route `dependsOn` must be explicit.** Bicep cannot always infer the dependency chain for nested Front Door resources (profile → endpoint → route). Adding `dependsOn: [origin]` on the route resource fixes the timing failure. The linter will correctly flag `originGroup` as unnecessary since that dependency is inferred via `parent:`.
- **Bicep is idempotent** — re-running after a partial failure is safe. It skips resources that already exist and only creates missing ones.
- **Bootstrap preflight check for storage/KV names** must distinguish between "taken by someone else" and "taken by a previous run in my own subscription." Solution: check if the resource already exists in the subscription first; only run the name-availability check for net-new resources.
- **`environment` and `appName` params declared in main.bicep but not wired to any module** produce linter warnings. Remove unused params or wire them. Clean linter output before production deployments.
- **Front Door module should not accept a `location` param** — Front Door is a global resource and hardcodes `'global'`. Passing location to the module produces an unused-params warning.
- **Cloud Shell stale file problem:** When you've committed changes locally but Cloud Shell has an older clone, always run: `cd ~ && rm -rf geoste-portfolio && git clone https://github.com/geostebovik/geoste-portfolio && cd geoste-portfolio && chmod +x bootstrap.sh`. Don't trust `git pull` alone when you suspect file corruption or stale state.
- **`sed -i 's/\r//' bootstrap.sh`** strips Windows CRLF line endings that cause Cloud Shell (Linux) to fail on `./bootstrap.sh` with cryptic errors.

### Project 14 — Key Vault Sequence (Correct Order)
1. Deploy ASP + Web App with `--assign-identity "[system]"` 
2. Store secrets: `az keyvault secret set`
3. Get managed identity principal ID: `az webapp identity show --query principalId -o tsv`
4. Get KV resource ID: `az keyvault show --query id -o tsv`
5. Assign RBAC: `az role assignment create --role "Key Vault Secrets User" --scope $KV_ID`
6. Configure KV references: `az webapp config appsettings set` with `@Microsoft.KeyVault(SecretUri=...)` syntax
7. Verify green resolved status in portal: Settings → Environment variables → Source = "Key vault"
8. Enable diagnostic settings (from Cloud Shell, not local Bash)
9. Run KQL in LAW → Logs, screenshot the results
10. Teardown: delete App Service and ASP; leave secrets in KV for Project 15

---

## 2. Portfolio Site — ostebovik.net

### What Was Built
A production portfolio site at **ostebovik.net** using Azure-native services, deployed via modular Bicep IaC with a bootstrap pattern. The site documents AZ-104 lab work organized by skill domain.

### Infrastructure Stack (Resource Group: `rg-geoste-prod-wus3-01`)

| Resource | Name | Purpose |
|---|---|---|
| Log Analytics Workspace | `law-prod-wus3-01` | Centralized logging |
| Application Insights | `appi-prod-wus3-01` | Frontend telemetry |
| Storage Account | `stgeostewus301` | Static assets (diagrams, screenshots) |
| Key Vault | `kv-geoste-prod-wus3-01` | Secrets (RBAC model) |
| Static Web App | `swa-prod-wus3-01` | Site hosting, GitHub CI/CD |
| WAF Policy | `wafafdprodwus301` | Web Application Firewall |
| Azure Front Door | `afd-prod-wus3-01` | CDN, custom domain, HTTPS |
| Front Door Endpoint | `ep-portfolio-bbgjdthdagbvawhc.z01.azurefd.net` | DNS target |

### Key Architecture Decisions
- **No VNet** — Static Web Apps don't live inside a VNet. Front Door handles the perimeter. Eliminates the networking module entirely vs. a traditional 3-tier pattern.
- **Bootstrap pattern** — `bootstrap.sh` creates the RG (imperative, since Bicep can't create its own RG), then calls `main.bicep` via `az deployment group create`. This is the production IaC pattern.
- **`.bicepparam` file** (`prod.bicepparam`) — all environment-specific values in one place. Enables future staging environment with `staging.bicepparam` against the same templates.
- **Modular Bicep** — five modules: `monitoring.bicep`, `keyvault.bicep`, `storage.bicep`, `staticwebapp.bicep`, `frontdoor.bicep`. One module per resource domain, orchestrated by `main.bicep`.
- **WAF policy deployed** but operating hours enforcement is a JavaScript check on page load (not a WAF time-based rule, which Front Door doesn't natively support). Displays a styled maintenance page outside 6am–9pm MST.
- **Managed TLS cert** — `certificateType: 'ManagedCertificate'` on the Front Door custom domain. Free, auto-renewed by Azure.
- **RBAC model on Key Vault** — `enableRbacAuthorization: true`. Access Policies are deprecated; never use them.
- **GitHub Actions CI/CD** — workflow file `azure-static-web-apps.yml` manually added after Bicep deployment didn't auto-generate it (GitHub write access wasn't granted at deploy time). Secret `AZURE_STATIC_WEB_APPS_API_TOKEN` added to repo settings. Push to `main` = deployed in <60 seconds.

### DNS Configuration
- Registrar: CNAME `@` → `ep-portfolio-bbgjdthdagbvawhc.z01.azurefd.net` (TTL: 300)
- Removed old ALIAS and CNAME records pointing to `lively-water-03cc5611e.7.azurestaticapps.net` (FamilyTreeRG — old site)
- `nslookup ostebovik.net` resolves to Front Door edge IP `132.220.38.112`

### Current State
- **Live:** `ostebovik.net` resolves via Front Door → Static Web App. Landing page (`index.html`) is deployed and serving.
- **Landing page design:** Giants color palette (black `#0a0a0a`, orange `#FD5A1E`, cream `#EFE4B0`), Barlow Condensed display font, IBM Plex Mono for code. Skill domain cards with IaaS/PaaS/IaC badges, stats bar (14 projects, 5 domains), scroll reveal animations.
- **GitHub Actions:** Working. Push to `main` triggers deployment.
- **Pending:** No skill domain content pages are live yet. Storage account populated but content not yet uploaded.

---

## 3. Content Organization Decision — Phase-Based → Skill-Domain-Based

### The Shift
The original portfolio structure organized work by **phases** (Phase 2, Phase 3, Phase 4) matching the AZ-104 study guide structure. This was replaced entirely with **skill domains**.

### Five Skill Domains (Final)
| Domain | URL Path | Projects |
|---|---|---|
| Identity & Governance | `/identity-governance/` | Phase 1 content (backfill pending) |
| Networking | `/networking/` | P3, P5, P6, P13 |
| Compute & Storage | `/compute-storage/` | P4, P7, P8, P12 |
| Infrastructure as Code | `/infrastructure-as-code/` | P11, P12, P14, P15/Capstone |
| Monitoring & Security | `/monitoring-security/` | P9, P10, P14 |

A sixth card, **AI & Automation**, is present on the landing page marked "Coming Soon."

### Reasoning
- **Phases have no meaning to a hiring manager.** "Phase 3" conveys nothing. "Networking" conveys competency area immediately.
- **Projects map naturally to skill domains.** Some projects appear in two domains (P12 in both Compute & Storage and IaC; P14 in both IaC and Monitoring & Security) — this is correct and honest.
- **Skill domains are inviting and scannable.** A technical interviewer can click directly to the domain relevant to the role.
- **Phase numbering is preserved as detail**, not navigation. Inside each domain page, projects are listed with their original numbers (e.g., "Project 13 — App Gateway & Bastion") for context and chronology.
- **`/resources/` path reserved** for standalone reference documents: RPO vs RTO write-up, PowerShell vs Bash syntax reference, AZ-104 whiteboard, other study documents that don't belong inside a specific domain.

### Networking Is the Heaviest Domain
P3, P5, P6, P13 — four projects. Identity & Governance is currently the lightest (Phase 1 content not yet migrated). Uneven volume across domains is expected and acceptable; lean into depth over breadth in thinner sections.

---

## 4. Pending Work

### Immediately Actionable
- [ ] **Populate skill domain pages** — build `az-104/networking/index.html`, `az-104/infrastructure-as-code/index.html`, etc. Infrastructure-as-code is the strongest content and highest interviewer-impact; start there.
- [ ] **Upload assets to storage account** (`stgeostewus301`) — diagrams, screenshots, write-ups for all completed projects. Use `az storage blob upload-batch` (CLI), not portal drag-and-drop.
- [ ] **Repo folder restructure** — finalize:
  ```
  geoste-portfolio/
  ├── index.html
  ├── .github/workflows/
  ├── infrastructure/          ← bootstrap.sh, main.bicep, prod.bicepparam, modules/
  └── az-104/
      ├── identity-governance/
      ├── networking/
      ├── compute-storage/
      ├── infrastructure-as-code/
      └── monitoring-security/
  ```
- [ ] **Wire "View projects" links** on landing page to actual skill domain pages.
- [ ] **Add Certifications section** to landing page — Credly badges for AZ-900, CC (ISC2), AZ-104 (in-progress), AI-900 (planned). Between Skills and footer.
- [ ] **Add resume link** — dedicated page or linked PDF.
- [ ] **Capture all portfolio evidence** from `rg-az104-dev-wus3-01` before deleting the RG: Container App screenshots, VNet topology, ACR, all Phase 4 project artifacts.
- [ ] **Phase 1 content backfill** — Identity & Governance domain has no projects mapped yet; Phase 1 work needs to be added.
- [ ] **Phase 2 guide reformatting** — reformat the Phase 2 guide to match Phase 3 & 4 format (was started but not completed this session — requires Phase 4 guide as the template reference).

### Bootstrap Improvement (Deferred)
- [ ] **Implement Option A preflight check** — smart name-availability check that skips resources already owned in the subscription. Currently commented out workaround is in place.

### Future / Planned
- [ ] **Add `www` CNAME** at registrar → same Front Door endpoint, for `www.ostebovik.net`.
- [ ] **Operating hours WAF rule** — currently JS-based. Upgrade to proper Front Door Rule Set when appropriate.
- [ ] **Dynamic log display page** — Application Insights / LAW data surfaced on a portfolio page (concept identified, not yet designed).
- [ ] **Delete `rg-az104-dev-wus3-01`** — after all evidence is captured and skill domain pages are populated. Target: next week.
- [ ] **AZ-104 exam** — projects complete; schedule the exam.

---

## 5. Key Files Produced This Session

| File | Description |
|---|---|
| `bootstrap.sh` | Creates `rg-geoste-prod-wus3-01`, runs preflight name checks, calls `main.bicep` via `az deployment group create` |
| `main.bicep` | Orchestrates all five Bicep modules in dependency order (monitoring → keyvault → storage → staticwebapp → frontdoor) |
| `prod.bicepparam` | All environment-specific parameter values for the production portfolio deployment |
| `modules/monitoring.bicep` | Deploys Log Analytics Workspace (`law-prod-wus3-01`) and Application Insights (`appi-prod-wus3-01`) |
| `modules/keyvault.bicep` | Deploys Key Vault (`kv-geoste-prod-wus3-01`) with RBAC model, soft delete, purge protection, diagnostic settings |
| `modules/storage.bicep` | Deploys Storage Account (`stgeostewus301`) for static site assets |
| `modules/staticwebapp.bicep` | Deploys Static Web App (`swa-prod-wus3-01`) connected to GitHub repo |
| `modules/frontdoor.bicep` | Deploys Front Door profile, WAF policy, endpoint, origin group, origin, route, custom domain (`ostebovik.net`), TLS cert, diagnostic settings |
| `index.html` | Portfolio landing page — Giants color palette, skill domain cards, stats bar, scroll reveal animations, certifications placeholder |
| `.github/workflows/azure-static-web-apps.yml` | GitHub Actions CI/CD workflow for Static Web App — triggers on push to `main`, deploys in <60 seconds |
| `project14-deployment.sh` | Full Azure CLI script for Project 14: ASP + Web App with managed identity, secrets in KV, RBAC assignment, KV references, diagnostic settings, teardown commands |
| `project14-architecture.svg` | SVG architecture diagram showing the KV + Managed Identity pattern (App Service → Key Vault → Log Analytics) |
| `project14-writeup.md` | Markdown write-up for Project 14 covering design decisions, lessons learned, and portfolio evidence list |

---

*Session date: May 8, 2026 | Conversation: `56069b72-9edc-4a52-8904-35bd75019f0e`*
