# PHASE03-NOTES
## AZ-104 Master Reference — Extracted from Session History
### Covers Phase 3 (Projects 7–10) and Phase 4 Project 11 (Bicep Fundamentals)

---

## 1. PENDING BICEP UPDATES

Items identified as needed but deferred — file locations noted.

### modules/vm-win.bicep
- **computerName parameter** — currently uses `take(vmName, 15)` or hardcoded `win-dev-01`. For multi-VM deployments this produces duplicate computer names. Fix: pass `computerName` as an explicit parameter from `main.bicep` so the caller controls uniqueness. Pattern: `computerName: 'win-${env}-${instance}'` resolves to `win-dev-01`, `win-dev-02` etc.
- **NSG attachment** — NIC-level NSG removed in favour of subnet-level attachment. Confirm no `--nsg` flag remains on VM create calls. Module currently creates NIC with subnet reference only — subnet NSG provides protection automatically.
- **Tags via parameter** — module hardcodes some tag values. Should receive `param tags object` from caller and apply uniformly. *(Partially done — verify all three modules use `param tags object` with no hardcoded overrides.)*

### modules/vm-linux.bicep
- **SSH key rotation** — SSH key was generated fresh in Cloud Shell session and stored in Key Vault as `vm-ssh-key`. If Cloud Shell session resets, a new key is generated. Update Key Vault secret and redeploy if VMs need to be reprovisioned with a different key.
- **Tags via parameter** — same as vm-win.bicep above.

### modules/storage.bicep
- **Tags consistency** — tag key was `wkld` instead of `project` at one point. Verify final file uses `project` as the key name to match policy expectations.
- **stdevwus301 cleanup** — a second storage account `stdevwus301` exists from early bootstrap runs with incorrect naming. Should be deleted — it has no active use and adds cost. Note: verify no resources depend on it before deletion.

### main.bicep
- **`project` parameter unused** — linter warning `no-unused-params` on `param project string`. Either remove it or wire it into tags/names. If tags object already includes `project: 'az104'` as a literal, the parameter is redundant and should be removed.
- **Subnet NSG assignments for Phase 4 tiers** — `snet-web`, `snet-api`, `snet-data`, `snet-appgw` all have NSGs attached but no custom rules. When App Gateway and the 3-tier app are deployed, specific inbound/outbound rules are required. Add to `modules/networking.bicep` (capstone) or via CLI before Project 13:
  - `nsg-appgw-dev-wus3-01`: must allow GatewayManager service tag inbound, AzureLoadBalancer inbound
  - `nsg-web-dev-wus3-01`: allow HTTPS inbound from App Gateway subnet
  - `nsg-api-dev-wus3-01`: allow inbound from web subnet only
  - `nsg-data-dev-wus3-01`: allow inbound from api subnet only, SQL port 1433

### az104-bootstrap.sh
- **Tags variable format** — was causing all tags to collapse into single `env` key. Fix applied: use `$TAGS` without quotes, store `TODAY=$(date +%Y-%m-%d)` separately before building TAGS string.
- **Key Vault flag** — `--soft-delete-retention-days` renamed to `--retention-days` in recent CLI. Script updated but verify on next run.
- **VM names** — corrected to `vm-win-dev-wus3-01` and `vm-linux-dev-wus3-01` with region segment included. Old names `vm-win-dev-01` / `vm-linux-dev-01` were missing region.
- **OS disk names** — corrected to `disk-os-win-dev-wus3-01` and `disk-os-linux-dev-wus3-01`.
- **stdevwus301** — second storage account created by early bootstrap run, not needed. Remove from bootstrap or rename to CAF standard.

### dev.bicepparam
- **String interpolation not supported** — bicepparam files cannot reference other parameters within the same file. All values must be literals. Tag values like `env: env` must be written as `env: 'dev'`.
- **getSecret() references** — `adminPassword` and `sshPublicKey` must use `getSecret()` not literal values. ARM requires `--enabled-for-template-deployment true` on the vault for this to work.

---

## 2. LESSONS LEARNED / GOTCHAS

### Azure CLI Behaviour

**CRLF line endings on Windows**
- Cause: VS Code on Windows saves files with `\r\n` (CRLF). Bash expects `\n` (LF) only.
- Symptom: `$'\r': command not found` on every line when running .sh in Cloud Shell.
- Fix: `sed -i 's/\r//' script.sh` before every run after uploading from Windows.
- Prevention: Set `"files.eol": "\n"` in VS Code settings globally.

**Shell detection — PowerShell vs Bash**
- PowerShell line continuation: backtick `` ` ``
- Bash line continuation: backslash `\`
- `az vm show` uses `--name` (VM is subject). `az vm extension set` uses `--vm-name` (extension is subject, VM is parent). Pattern: `--name` always refers to the direct subject of the command.
- `-g` and `-n` are valid shorthand for `--resource-group` and `--name` in most commands but not all. `az monitor data-collection rule association create` does not accept `-g` — scope derives from `--resource` ID.

**Variable naming in Bash — no hyphens**
- `VNET-01="..."` fails — Bash treats `-` as subtraction operator.
- Fix: `VNET01="..."` or `VNET_01="..."`.

**Tags format in Bash**
- Quoting the TAGS variable causes all tags to collapse into a single key.
- Wrong: `--tags "$TAGS"` when TAGS contains spaces between pairs.
- Right: `--tags $TAGS` (no quotes around variable reference).
- Store dynamic values separately: `TODAY=$(date +%Y-%m-%d)` then include in TAGS string.

**az role assignment create requires --scope not --resource-group**
- `--resource-group` is not accepted. Must use full ARM resource ID in `--scope`.
- Pattern: `--scope "/subscriptions/{sub}/resourceGroups/{rg}"` for RG-level scope.

**Policy definition IDs change between CLI versions**
- Never hardcode policy definition GUIDs in scripts.
- Always query first: `az policy definition list --query "[?displayName=='Allowed locations'].name" -o tsv`
- One-character difference between versions caused 30 minutes of debugging.

**Policy remediation — managed identity propagation delay**
- Symptom: remediation tasks fail immediately after policy assignment.
- Cause: managed identity created for the policy assignment needs 30–60 seconds to propagate through Azure AD before it can write tags.
- Fix: wait 60 seconds after assignment before triggering remediation. Use unique names for retry attempts (`remediate-inherit-tag-env-2`).
- Alternative: tag resources directly with `az resource tag --is-incremental` as a fallback when remediation consistently fails.

**Subnet tagging**
- `az network vnet subnet create` does not accept `--tags` flag. Tags are not supported on subnets — they inherit from the VNet.

### VM and Compute

**Windows VM computerName — 15 character limit**
- The Azure resource name can be any valid length but Windows OS hostname (computerName) is hard-limited to 15 characters.
- `vm-win-dev-wus3-01` = 18 characters — fails at provisioning with `InvalidParameter: osProfile.computerName`.
- Fix: pass `computerName` as a separate explicit parameter. Use `win-${env}-${instance}` = `win-dev-01` (10 chars).
- Do not rely on `take(vmName, 15)` for multi-VM deployments — produces duplicate computer names.

**Windows Server 2025 Azure Edition — hotpatch requirements**
- Azure Edition images are Hotpatch-compatible. Using `patchMode: 'AutomaticByOS'` fails with `InvalidParameter`.
- Required configuration:
  ```bicep
  patchSettings: {
    patchMode: 'AutomaticByPlatform'
    assessmentMode: 'AutomaticByPlatform'
    enableHotpatching: true
    automaticByPlatformSettings: {
      rebootSetting: 'IfRequired'
    }
  }
  ```
- `enableHotpatching` belongs inside `patchSettings`, not in `windowsConfiguration` directly (API version dependent).

**Linux data disk — never mount at /mnt**
- Azure Linux agent mounts the temporary disk (sdb) at `/mnt` by default via cloud-init.
- Mounting a data disk at `/mnt` creates a conflict — after reboot the temp disk wins.
- Fix: always use `/data` or any other custom path for persistent data disks.
- fstab: always use UUID not device name. Device names (sda, sdb, sdc) can shift on reboot. UUID never changes.
- Get UUID after format: `sudo blkid -s UUID -o value /dev/sdc`

**Linux disk device names shift**
- Azure does not guarantee device assignment order. A disk named `/dev/sdc` may appear as `/dev/sdb` after reboot or after another disk is added.
- Always use UUID in fstab: `UUID=xxxx /data ext4 defaults,nofail 0 2`
- `nofail` flag is critical — without it, a missing disk can prevent VM from booting.

**Disk resize is two separate steps**
1. `az disk update --size-gb N` — expands the block device (Azure level)
2. `resize2fs /dev/sdX` — expands the filesystem to use new space (OS level)
- Azure resizes the disk; the OS must be told to use the new space separately.
- Online resize possible for ext4 without unmounting: `sudo resize2fs /dev/sda`

**VM auto-created NSGs and NICs**
- When `--nsg ""` is passed incorrectly or omitted on `az vm create`, Azure auto-creates NSGs named `{vmName}NSG` and NICs named `{vmName}VMNic`.
- These orphaned NSGs are attached to the NIC, not the subnet.
- Delete sequence: detach from NIC first (`az network nic update --remove networkSecurityGroup`), then delete NSG.
- Prevention: use subnet-level NSG attachment via `az network vnet subnet create --nsg` — then omit `--nsg` from `az vm create` entirely.

**Custom Script Extension — SAS token type**
- CSE agent makes an anonymous HTTP fetch to download the script blob.
- User delegation SAS tokens require the requester to present an Azure AD token — CSE agent has no AD context, returns 403.
- Fix: use service SAS (account key auth), not user delegation SAS.
- Production alternative: managed identity on VM + Storage Blob Data Reader role — no SAS token needed.

**BGInfo extension — no longer in portal marketplace**
- Guide step "Extensions + Applications → Add → BGInfo" no longer works — BGInfo is not listed in the portal extension marketplace.
- Deploy via CLI: `az vm extension set --name BGInfo --publisher Microsoft.Compute --version 2.1 --settings '{}'`

**Azure Diagnostics (LAD/IaaSDiagnostics) deprecated March 2026**
- Guide steps referencing "Diagnostic settings → Add diagnostic setting → send to workspace" for VMs use the deprecated LAD/MMA agent path.
- Current correct approach: Azure Monitor Agent (AMA) + Data Collection Rule (DCR).
- Remove legacy extensions before installing AMA to avoid conflicts.
- DCR association command: `az monitor data-collection rule association create` — does not accept `-g` flag. Uses `--resource` with full VM resource ID.
- DCR creation requires JSON file (`--rule-file dcr.json`) — inline JSON flags removed in recent CLI versions.

**MDE.Windows / MDE.Linux auto-deployed**
- Microsoft Defender for Endpoint extensions appear on VMs automatically via Defender for Cloud on Visual Studio subscriptions.
- Do not remove — leave in place. They provide security telemetry.

### Storage and Key Vault

**Storage account — no hyphens, lowercase, 3–24 chars, globally unique**
- CAF convention adapts: concatenate segments instead of hyphenating.
- `st-az104-dev-wus3-01` → invalid. `staz104devwus301` → correct.

**Key Vault RBAC — ARM deployment access**
- Creating Key Vault with `--enable-rbac-authorization true` means even the creator needs an explicit role assignment to write secrets.
- Role needed to write: `Key Vault Secrets Officer`
- For Bicep deployments using `getSecret()`: ARM service principal needs access.
- Fix: `az keyvault update --enabled-for-template-deployment true`
- This is separate from user role assignment — both are needed.

**Key Vault soft delete blocks reuse of secret names**
- Deleted secrets are retained for the soft-delete retention period (7 days in lab).
- Cannot reuse a secret name during retention period without purging first.
- `az keyvault secret purge --vault-name kv-az104-dev-wus3-01 --name secret-name`

**Bicepparam getSecret() — BCP258 linter warning**
- `@secure()` parameters without assignment in bicepparam trigger BCP258.
- This is a known false positive when secrets come via `getSecret()`.
- Does not block deployment. Can be suppressed by ensuring `getSecret()` references are present in the params file.

**Bicepparam string interpolation not supported**
- Cannot reference other parameters within same bicepparam file.
- `param tags = { env: env }` fails — `env` is not resolvable.
- Fix: use literal values only: `param tags = { env: 'dev' }`.

### Backup and Recovery

**Recovery Services Vault — RG deletion blocked by backup data**
- `az group delete` fails if RSV contains protected items or backup data.
- Correct teardown sequence:
  1. `az backup protection disable ... --delete-backup-data true --yes` (per VM)
  2. Verify no protected items remain
  3. `az group delete`
- Container name format is exact and case-sensitive: `IaasVMContainer;iaasvmcontainerv2;{rg};{vm-name}`
- Always query exact container name: `az backup container list ... --query "[].name"`

**Restore point collections block RG deletion**
- Azure Backup creates a separate RG (`rg-backup-1` or similar) with restore point collections.
- These cannot be deleted while the vault holds references.
- Wait 10–30 minutes after stopping protection, then retry.
- Azure will auto-clean these within 24 hours if deletion fails.

### Logic Apps and Automation

**Logic App consumption tier — API connections tied to user auth**
- Pre-built connectors (Azure VM, Office 365) create API connection resources authenticated as the deploying user.
- Cannot be switched to managed identity without moving to Standard tier (~$50+/mo) or using HTTP action with manual token handling.
- For VM start/stop automation: use Automation Account with PowerShell runbook instead. Native managed identity, free tier (500 min/mo).

### Networking

**AzureBastionSubnet — exact name required**
- Subnet must be named exactly `AzureBastionSubnet` — no variation, no CAF naming.
- Minimum size: /26
- Requires specific NSG rules — wrong rules cause silent failures.

**Application Gateway — dedicated subnet required**
- Cannot share subnet with any other resource type.
- Minimum subnet size: /24 for production, /27 acceptable for lab.
- NSG on App Gateway subnet must explicitly allow:
  - Inbound: GatewayManager service tag on ports 65200–65535
  - Inbound: AzureLoadBalancer service tag
  - Without these rules, App Gateway provisioning fails or health probes break.

**VNet peering — two directions required**
- Peering must be created in both directions: hub→spoke AND spoke→hub.
- Single-direction peering appears to work but traffic is asymmetric.
- Bash CLI equivalent of PowerShell `Add-AzVirtualNetworkPeering`:
  ```bash
  az network vnet peering create -g $RG -n peer-hub-to-spoke \
    --vnet-name vnet-hub --remote-vnet $SPOKE_ID --allow-vnet-access true
  ```

---

## 3. KEY DESIGN DECISIONS

### Naming Convention — CAF Standard
**Decision:** Adopt Microsoft Cloud Adoption Framework naming throughout: `{type}-{workload}-{env}-{region}-{instance}`
**Reasoning:** Standard in enterprise environments, enables filtering by resource type, self-documenting at scale. The `type` prefix first (not company abbreviation first) allows `az resource list` results to sort meaningfully.
**Exceptions documented:**
- Storage accounts / ACR: no hyphens, lowercase only — concatenate segments
- Windows VMs: 15-char computerName limit — use shorter pattern for OS hostname
- AzureBastionSubnet: Azure-mandated exact name, no CAF compliance possible

### Security Posture — No Public IPs on VMs
**Decision:** All VMs deployed with `--public-ip-address ""`. Access via `az vm run-command` for automation, Bastion for interactive sessions.
**Reasoning:** Eliminates attack surface. RDP/SSH exposure on public internet is a leading cause of compromise. `az vm run-command` provides all necessary automation capability without network exposure.

### Managed Identity — Always System-Assigned
**Decision:** All VMs and App Services deployed with `--assign-identity "[system]"`. No stored credentials anywhere.
**Reasoning:** System-assigned identity ties to resource lifecycle — deleted with the resource, no orphaned identities. User-assigned appropriate when multiple services share an identity or identity must pre-exist the resource.
**Applied to:** VMs (both), App Service (Phase 3 Project 8), Container Apps (Phase 4 Project 12).

### NSG Placement — Subnet Level Not NIC Level
**Decision:** NSGs attached to subnets via `az network vnet subnet create --nsg`. Not passed to `az vm create --nsg`.
**Reasoning:** Subnet-level NSG protects all resources in the subnet including future additions. NIC-level NSG requires configuration per VM. Single point of management at subnet level.

### Key Vault — RBAC Model Not Access Policies
**Decision:** All Key Vaults created with `--enable-rbac-authorization true`.
**Reasoning:** Access Policies are deprecated for new vaults. RBAC provides granular per-secret control, full audit trail, and integrates with Azure AD role management. Access Policies grant broad vault-level permissions.

### Storage — Private Container, Public Network Access Enabled for Lab
**Decision:** Storage account containers set to private (no anonymous blob access). Network access enabled to allow uploads during lab work.
**Reasoning:** Container privacy is the meaningful security control — it requires authentication for all access. Network-level restriction adds operational friction in a lab without meaningful security benefit given the authenticated access requirement.

### Monitoring — AMA + DCR Instead of Legacy Agents
**Decision:** Azure Monitor Agent with Data Collection Rules instead of Log Analytics Agent (MMA) or Linux Diagnostic Extension (LAD).
**Reasoning:** LAD and MMA deprecated March 2026. AMA supports Python 3 (Ubuntu 24.04 incompatible with LAD's Python 2 dependency). DCR model decouples data collection definition from agent — one DCR can feed multiple workspaces.

### Bicep — Modular Pattern with Key Vault Secret References
**Decision:** IaC split into main.bicep (orchestrator) + purpose-specific modules. Secrets via `getSecret()` in bicepparam, never in template or CLI args.
**Reasoning:** Modular structure enables reuse and independent testing. Secrets in `getSecret()` means they never appear in deployment logs, git history, or portal output. ARM retrieves them directly from Key Vault at deploy time.

### Bootstrap vs Bicep — Complementary Not Competing
**Decision:** Keep bash bootstrap script for pre-flight tasks (RG creation, Key Vault secret seeding, CLI extension installation). Use Bicep for all infrastructure resources.
**Reasoning:** Bicep cannot create its own target resource group at RG-scope deployment. Bootstrap does one-time setup that Bicep doesn't handle. Bicep handles idempotent infrastructure that needs what-if, drift detection, and version control benefits.

### Tags — Policy-Enforced Inheritance Not Manual
**Decision:** Tags enforced via Azure Policy (require-tag-env, require-tag-owner, inherit-tag-* assignments). Resources inherit from RG rather than tagging each resource manually.
**Reasoning:** Manual tagging is inconsistent and breaks when people forget. Policy enforcement is auditable, automatic for new resources, and survives team turnover.

### App Service — P0v3 Minimum for Slots
**Decision:** App Service Plan at Premium v3 P0v3 (~$41/mo) despite higher cost than Basic.
**Reasoning:** Standard and Basic tiers do not support deployment slots. Slots are required for zero-downtime deployments (staging→production swap). P0v3 is the smallest non-legacy tier supporting slots. Standard S1 costs more (~$58/mo). Free/Basic tier documented as "Legacy" in current portal.

---

## 4. RESOURCE INVENTORY

### Phase 3 Resources (deployed and torn down per project, redeploy from scripts)

| Resource | Type | Key Properties |
|---|---|---|
| `rg-az104-dev-wus3-01` | Resource Group | westus3, tags: env=dev owner=ostebovik project=az104 |
| `vnet-az104-dev-wus3-01` | Virtual Network | 10.0.0.0/16, westus3 |
| `snet-win-az104-dev-wus3-01` | Subnet | 10.0.1.0/24, NSG: nsg-win-dev-wus3-01 |
| `snet-linux-az104-dev-wus3-01` | Subnet | 10.0.2.0/24, NSG: nsg-linux-dev-wus3-01 |
| `snet-web-dev-wus3-01` | Subnet | 10.0.3.0/24, NSG: nsg-web-dev-wus3-01 |
| `snet-api-dev-wus3-01` | Subnet | 10.0.4.0/24, NSG: nsg-api-dev-wus3-01 |
| `snet-data-dev-wus3-01` | Subnet | 10.0.5.0/24, NSG: nsg-data-dev-wus3-01 |
| `snet-appgw-dev-wus3-01` | Subnet | 10.0.6.0/24, NSG: nsg-appgw-dev-wus3-01 |
| `AzureBastionSubnet` | Subnet | 10.0.7.0/26, no NSG (Bastion manages own rules) |
| `nsg-win-dev-wus3-01` | NSG | attached to snet-win, no custom rules yet |
| `nsg-linux-dev-wus3-01` | NSG | attached to snet-linux, no custom rules yet |
| `nsg-web-dev-wus3-01` | NSG | attached to snet-web, rules needed for App Gateway |
| `nsg-api-dev-wus3-01` | NSG | attached to snet-api, rules needed for capstone |
| `nsg-data-dev-wus3-01` | NSG | attached to snet-data, rules needed for capstone |
| `nsg-appgw-dev-wus3-01` | NSG | attached to snet-appgw, GatewayManager rules needed |
| `vm-win-dev-wus3-01` | Virtual Machine | Windows Server 2025 Azure Edition, B2s, system identity, 10.0.1.4 |
| `vm-linux-dev-wus3-01` | Virtual Machine | Ubuntu 24.04 LTS, B2s, system identity, 10.0.2.4 |
| `disk-os-win-dev-wus3-01` | Managed Disk | OS disk, Premium LRS, deleteOption=Delete |
| `disk-os-linux-dev-wus3-01` | Managed Disk | OS disk, Premium LRS, deleteOption=Delete |
| `staz104devwus301` | Storage Account | Standard LRS, no public blob, TLS1_2, container: scripts |
| `stdevwus301` | Storage Account | Standard LRS — legacy naming, candidate for deletion |
| `law-az104-dev-wus03-01` | Log Analytics Workspace | 30-day retention, PerGB2018 |
| `dcr-az104-dev-wus3-01` | Data Collection Rule | Microsoft-Perf, Microsoft-Syslog, Microsoft-Event → LAW |
| `acraz104devwus301` | Container Registry | Basic SKU, admin disabled, westus3 |
| `kv-az104-dev-wus3-01` | Key Vault | standard SKU, RBAC auth, soft-delete 7 days, template-deployment enabled |
| `rsv-az104-dev-wus3-01` | Recovery Services Vault | LRS, soft-delete enabled, used in Project 10 then torn down |
| `pol-az104-daily-7day` | Backup Policy | daily 11pm UTC, 7d/4w/3m retention |
| `asp-az104-dev-wus3-01` | App Service Plan | Linux, P0v3, ~$41/mo |
| `app-az104-dev-wus3-01` | App Service (Web App) | Python 3.11, HTTPS only, system identity, staging slot |
| `ag-az104-dev-wus3-01` | Action Group | email: djeemunee@letter7.onmicrosoft.com |
| `alert-cpu-high-linux` | Metric Alert | CPU > 80%, 5min window, severity 2, vm-linux-dev-wus3-01 |
| `alert-heartbeat-vms` | Scheduled Query Alert | heartbeat < 1 per 5min, severity 1 |

### Phase 4 Resources (current, deployed via Bicep)

| Resource | Type | Key Properties |
|---|---|---|
| `vm-win-dev-wus3-01` | Virtual Machine | Windows Server 2025 Azure Edition, B2s, hotpatch enabled, principalId: 671ba5ec-b434-49da-aba2-7c7be53ab01d |
| `vm-linux-dev-wus3-01` | Virtual Machine | Ubuntu 24.04 LTS, B2s, SSH key auth, principalId: c71f4cd1-4296-4785-ab5d-4f6e92b38c87 |
| `vm-win-dev-wus3-01VMNic` | Network Interface | attached to snet-win-az104-dev-wus3-01, 10.0.1.4 |
| `vm-linux-dev-wus3-01VMNic` | Network Interface | attached to snet-linux-az104-dev-wus3-01, 10.0.2.4 |
| `kv-az104-dev-wus3-01` | Key Vault | secrets: vm-admin-password, vm-ssh-key |
| `acraz104devwus301` | Container Registry | images: az104-web:v1, az104-web:v2 (Project 12) |

### Policy Assignments (on rg-az104-dev-wus3-01)

| Assignment Name | Policy | Enforcement |
|---|---|---|
| `require-tag-env` | Require env tag | Default (deny) |
| `require-tag-owner` | Require owner tag | Default (deny) |
| `allowed-locations-wus3` | Allowed locations: westus3 | Default (deny) |
| `appsvc-https-only` | App Service HTTPS only | Default (deny) |
| `appsvc-managed-identity` | App Service managed identity required | Default (deny) |
| `appsvc-no-remote-debug` | App Service disable remote debugging | Default (deny) |
| `inherit-tag-env` | Inherit env from RG | Default + managed identity |
| `inherit-tag-owner` | Inherit owner from RG | Default + managed identity |
| `inherit-tag-project` | Inherit project from RG | Default + managed identity |
| `inherit-tag-phase` | Inherit phase from RG | Default + managed identity |

### Bicep Module Library (Phase04/11_Bicep_Fundamentals/)

| File | Purpose | Key Parameters |
|---|---|---|
| `main.bicep` | Orchestrator — calls all modules | azureRegion, regionCode, env, instance, adminUsername, @secure adminPassword, @secure sshPublicKey, tags |
| `dev.bicepparam` | Dev environment values | all params + getSecret() for adminPassword and sshPublicKey |
| `modules/storage.bicep` | Storage account | azureRegion, env, regionCode, instance, tags |
| `modules/vm-linux.bicep` | Linux VM + NIC | vmName, azureRegion, vmSize, adminUsername, @secure sshPublicKey, subnetId, osDiskName, tags |
| `modules/vm-win.bicep` | Windows VM + NIC | vmName, computerName, azureRegion, vmSize, adminUsername, @secure adminPassword, subnetId, osDiskName, tags |

---

## QUICK REFERENCE — COMMANDS TO REMEMBER

```bash
# Fix Windows line endings before running .sh in Cloud Shell
sed -i 's/\r//' script.sh

# Get exact backup container name (never construct manually)
az backup container list -g $RG --vault-name $RSV \
  --backup-management-type AzureIaasVM --query "[].name" -o tsv

# Get policy definition ID (never hardcode)
az policy definition list \
  --query "[?displayName=='Allowed locations'].name" -o tsv

# Tag all resources in RG at once
az resource list -g $RG --query "[].id" -o tsv | while read ID; do
  az resource tag --ids "$ID" --tags $TAGS --is-incremental 2>/dev/null || true
done

# Enable ARM to retrieve Key Vault secrets during Bicep deployment
az keyvault update -n $KV -g $RG --enabled-for-template-deployment true

# Assign Key Vault Secrets Officer to yourself
USER_OID=$(az ad signed-in-user show --query id -o tsv)
az role assignment create --assignee $USER_OID \
  --role "Key Vault Secrets Officer" --scope $KV_ID

# Get managed identity principal ID from VM
az vm show -g $RG -n $VM --query "identity.principalId" -o tsv

# DCR association (no -g flag — scope from resource ID)
az monitor data-collection rule association create \
  -n "dcra-name" --rule-id $DCR_ID --resource $VM_ID

# Bicep what-if (always before deploy)
az deployment group create -g $RG -f main.bicep -p dev.bicepparam --what-if

# Run command on VM without public IP
az vm run-command invoke -g $RG -n $VM \
  --command-id RunShellScript --scripts "your command here"
```

---

*Generated from AZ-104 Phase 3–4 session history · ostebovik.net*
