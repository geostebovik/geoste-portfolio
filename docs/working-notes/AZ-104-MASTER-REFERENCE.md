# AZ-104 Master Reference Document
### ostebovik.net Portfolio — Gerard Ostebovik

> **Compiled from:** Phase 2 session notes, Phase 3 session notes, Phase 4 session notes (PHASE04-NOTES.md), and the Phase 4 + Portfolio Build session summary.  
> **Status:** All AZ-104 projects complete (P3–P15). Portfolio live at ostebovik.net. Exam pending.  
> **Use this document:** Bring into every new session. Supersedes all individual phase notes.

---

## Table of Contents

1. [Environment & Identity](#1-environment--identity)
2. [Naming Conventions](#2-naming-conventions)
3. [Key Design Decisions](#3-key-design-decisions)
4. [Lessons Learned / Gotchas — by Domain](#4-lessons-learned--gotchas--by-domain)
   - [Azure CLI & Shell Behavior](#41-azure-cli--shell-behavior)
   - [Networking](#42-networking)
   - [Virtual Machines & Compute](#43-virtual-machines--compute)
   - [Storage & Key Vault](#44-storage--key-vault)
   - [Load Balancer](#45-load-balancer)
   - [DNS & Private Endpoints](#46-dns--private-endpoints)
   - [Bastion](#47-bastion)
   - [Container Apps & Registry](#48-container-apps--registry)
   - [Monitoring & Backup](#49-monitoring--backup)
   - [Bicep / IaC](#410-bicep--iac)
   - [Portfolio Infrastructure (ostebovik.net)](#411-portfolio-infrastructure-osteboviknet)
5. [Resource Inventory — AZ-104 Lab](#5-resource-inventory--az-104-lab)
6. [Resource Inventory — Portfolio Production](#6-resource-inventory--portfolio-production)
7. [Pending Bicep Updates](#7-pending-bicep-updates)
8. [Portfolio Site — Current State & Pending Work](#8-portfolio-site--current-state--pending-work)
9. [Content Organization — Skill Domains](#9-content-organization--skill-domains)
10. [Key Files & Deliverables](#10-key-files--deliverables)
11. [Exam Topic Coverage](#11-exam-topic-coverage)
12. [Quick Reference — Commands to Remember](#12-quick-reference--commands-to-remember)

---

## 1. Environment & Identity

| Item | Value |
|---|---|
| **Subscription ID** | `343a8a7e-9911-478d-b833-74110a11b3c2` (Visual Studio Enterprise, ~$150/mo) |
| **AZ-104 Lab RG** | `rg-az104-dev-wus3-01` (westus3) |
| **Portfolio RG** | `rg-geoste-prod-wus3-01` (westus3) |
| **AZ-104 Repo** | `C:\Users\gerar\az-104` on GitHub |
| **Portfolio Repo** | `https://github.com/geostebovik/geoste-portfolio` |
| **Local shell** | PowerShell — backtick `` ` `` line continuation |
| **Cloud Shell** | Bash — backslash `\` line continuation |
| **Certs held** | AZ-900 (Azure Fundamentals), CC (ISC2 Certified in Cybersecurity) |
| **Cert in progress** | AZ-104 Microsoft Azure Administrator |
| **Cert planned** | AI-900 (or successor) |
| **Portfolio design** | Giants palette: black `#0a0a0a`, orange `#FD5A1E`, cream `#EFE4B0` · Barlow Condensed display · IBM Plex Mono code |

---

## 2. Naming Conventions

### CAF Standard Pattern
`{type}-{env}-{region}-{instance}`

**Workload segment (`az104`) appears ONLY in the resource group name, not individual resources.**  
Exception: Legacy resources with `az104` in name (VM subnets `snet-win-az104-dev-wus3-01`, `snet-linux-az104-dev-wus3-01`) — accepted, cleanup deferred.

### Examples
| Resource | Pattern | Example |
|---|---|---|
| Resource Group | `rg-{wkld}-{env}-{region}-{instance}` | `rg-az104-dev-wus3-01` |
| Virtual Machine | `vm-{os}-{env}-{region}-{instance}` | `vm-win-dev-wus3-01` |
| Virtual Network | `vnet-{wkld}-{env}-{region}-{instance}` | `vnet-az104-dev-wus3-01` |
| Subnet | `snet-{tier}-{env}-{region}-{instance}` | `snet-web-dev-wus3-01` |
| NSG | `nsg-{tier}-{env}-{region}-{instance}` | `nsg-web-dev-wus3-01` |
| App Service Plan | `asp-{env}-{region}-{instance}` | `asp-dev-wus3-01` |
| Web App | `app-{env}-{region}-{instance}` | `app-dev-wus3-01` |
| Key Vault | `kv-{wkld}-{env}-{region}-{instance}` | `kv-az104-dev-wus3-01` |
| Log Analytics | `law-{wkld}-{env}-{region}-{instance}` | `law-az104-dev-wus03-01` ⚠️ |
| Storage / ACR | no hyphens, concatenated | `staz104devwus301`, `acrdevwus301` |
| OS Disk | `disk-os-{os}-{env}-{region}-{instance}` | `disk-os-win-dev-wus3-01` |

> ⚠️ **Note:** `law-az104-dev-wus03-01` uses `wus03` (three digits) not `wus3`. This inconsistency is baked into the deployed resource — do not assume it matches the VNet/subnet naming.

### File Naming (Repository)
Lowercase kebab-case: `{topic}-{descriptor}.{ext}` — e.g., `project14-architecture.svg`, `keyvault-managed-identity.sh`

### Portfolio RG Naming
Portfolio resources use `geoste` prefix (not `ostebovik`) for consistency and brevity:  
`rg-geoste-prod-wus3-01`, `kv-geoste-prod-wus3-01`, `stgeostewus301`

---

## 3. Key Design Decisions

### Architecture

**Hub-Spoke Topology** (Phase 2) — Two VNets connected via peering rather than a flat network. Hub holds shared services (Bastion, DNS). Each spoke is an independent blast radius. Maps to real Azure landing zone patterns.

**No Public IPs on VMs** — All VMs deployed with `--public-ip-address ""`. Access via `az vm run-command` for automation, Bastion for interactive sessions. Eliminates attack surface entirely.

**Standard SKU for All Networking Resources** — Basic SKU Load Balancer is being retired. Standard is zone-redundant, supports outbound rules and multiple frontend IPs. The extra configuration required teaches correct enterprise patterns.

### Security

**NSG Placement — Subnet Level, Not NIC Level** — NSGs attached to subnets via `az network vnet subnet create --nsg`. Protects all resources in the subnet including future additions. Single management point.

**Key Vault — RBAC Model, Never Access Policies** — All KVs created with `--enable-rbac-authorization true`. Access Policies are deprecated for new vaults. RBAC provides granular per-secret control with full audit trail.

**Managed Identity — System-Assigned on All Resources** — All VMs and App Services use `--assign-identity "[system]"`. No stored credentials anywhere. System-assigned ties to resource lifecycle — deleted with the resource, no orphaned identities.

**Service Tags Over IP Ranges in NSG Rules** — `AzureLoadBalancer`, `VirtualNetwork`, `Internet` instead of IP address ranges. Microsoft maintains these automatically; hardcoded IPs break when Azure infrastructure changes.

### IaC

**Bootstrap + Bicep, Complementary Pattern** — Bootstrap script (`az104-bootstrap.sh`) handles pre-flight tasks: RG creation (Bicep can't create its own target RG), Key Vault secret seeding, CLI setup. Bicep handles all infrastructure resources (idempotent, what-if capable, version-controlled).

**Modular Bicep — One Module Per Domain** — `main.bicep` orchestrates purpose-specific modules. Secrets via `getSecret()` in `.bicepparam`, never in templates or CLI args.

**Tags — Policy-Enforced Inheritance** — `require-tag-env`, `require-tag-owner`, `inherit-tag-*` policy assignments on the RG. Resources inherit from RG automatically. Manual tagging is inconsistent and breaks.

### Monitoring

**AMA + DCR Instead of Legacy Agents** — LAD and MMA deprecated March 2026. Azure Monitor Agent with Data Collection Rules is the current correct pattern. DCR decouples data collection definition from the agent.

### App Service

**P0v3 Minimum for Deployment Slots** — Deployment slots require Standard tier or higher. P0v3 is the smallest non-legacy tier that supports slots (~$41/mo). Free/Basic shown as "Legacy" in current portal.

**SAS Tokens — Policy-Linked Over Ad-Hoc** — Policy-linked SAS can be revoked by deleting the policy. Ad-hoc SAS cannot be revoked before expiry — compromise requires rotating the storage account key, disrupting all applications. Analogy: ad-hoc = cash (irrecoverable); policy SAS = credit card (can be cancelled).

---

## 4. Lessons Learned / Gotchas — by Domain

### 4.1 Azure CLI & Shell Behavior

**Command Structure Pattern**  
Always `az {service} {noun} {verb}`. Examples: `az appservice plan create`, `az webapp create`, `az keyvault secret set`. Use `az {command} --help` as primary reference — faster than googling, always matches installed CLI version, works offline.

**CRLF Line Endings on Windows**  
VS Code on Windows saves files with `\r\n`. Cloud Shell (Linux Bash) expects `\n` only.  
Symptom: `$'\r': command not found` on every line.  
Fix: `sed -i 's/\r//' script.sh` before every run after editing on Windows.  
Prevention: Set `"files.eol": "\n"` in VS Code settings globally.

**PowerShell vs Bash Variable Capture**  
- PowerShell: `$VAR = $(az command --query field -o tsv)`
- Bash: `VAR=$(az command --query field -o tsv)`  
`--query` + `-o tsv` are required to extract a single value from JSON output cleanly.

**Bash Variable Names — No Hyphens**  
`VNET-01="..."` fails — Bash treats `-` as subtraction. Use `VNET_01` or `VNET01`.

**Tags Variable in Bash — No Quotes**  
- Wrong: `--tags "$TAGS"` when TAGS contains spaces between pairs — collapses all tags into single key.  
- Right: `--tags $TAGS` (no quotes). Store dynamic values separately: `TODAY=$(date +%Y-%m-%d)` then include in TAGS string.

**`--name` vs `--vm-name`**  
`az vm show` uses `--name` (VM is the subject). `az vm extension set` uses `--vm-name` (extension is subject, VM is the parent). Pattern: `--name` always refers to the direct subject of the command.

**`-g` Shorthand Not Universal**  
`-g` works for most commands but not all. `az monitor data-collection rule association create` does not accept `-g` — scope derives from the `--resource` ID.

**Local Bash in VS Code Corrupts Complex Commands**  
Azure CLI commands involving long resource IDs as flag values can corrupt on local Bash (Git Bash/WSL) due to Windows path interpolation. Use Azure Cloud Shell for `az monitor diagnostic-settings create` and any command passing long ARM IDs as values.

**`az role assignment create` Requires `--scope`, Not `--resource-group`**  
`--resource-group` flag is not accepted. Must use full ARM resource ID: `--scope "/subscriptions/{sub}/resourceGroups/{rg}"` for RG-level scope.

**Policy Definition IDs Change Between CLI Versions**  
Never hardcode policy definition GUIDs. Always query: `az policy definition list --query "[?displayName=='Allowed locations'].name" -o tsv`. One character difference between versions caused 30 minutes of debugging.

**Policy Remediation — Managed Identity Propagation Delay**  
Remediation tasks fail immediately after policy assignment because the managed identity needs 30–60 seconds to propagate through Entra ID. Wait 60 seconds, use unique names for retry attempts (`remediate-inherit-tag-env-2`). Fallback: `az resource tag --is-incremental`.

**Cloud Shell Stale Files**  
When you've committed changes locally but Cloud Shell has an older clone, always start fresh:  
```bash
cd ~ && rm -rf geoste-portfolio && git clone https://github.com/geostebovik/geoste-portfolio
cd geoste-portfolio && chmod +x bootstrap.sh
```

---

### 4.2 Networking

**Azure Subnet Gateways Do Not Respond to ICMP**  
The `.1` address in each subnet (e.g., `10.0.1.1`) is an Azure infrastructure address and never responds to ping. Always test peering by pinging a VM's private IP, never the subnet gateway.

**`ip route show` Is Not a Valid Peering Diagnostic Tool**  
Azure SDN handles peered VNet routes at the hypervisor layer. Guest OS routing tables will never show peering routes — they will always appear missing even when peering is fully functional. Use actual connectivity tests (ping a real VM IP across the peering).

**VNet Peering Requires Two Separate Objects**  
Hub→Spoke AND Spoke→Hub must each be created. Single-direction peering shows `peeringState: Initiated`, not `Connected`. Traffic does not flow. Both must include `allowForwardedTraffic: true`.

**NSG Rule with Source `*` Blocks Azure Bastion**  
`*` matches all sources including `VirtualNetwork`, which encompasses Bastion connections. Use `Internet` to block public RDP/SSH while leaving Bastion connections intact.  
- `*` = everything (internet + VNet + peered VNets + Bastion)  
- `Internet` = public internet only

**NSG Rule Priorities Are Per-Direction**  
Priority 130 inbound and priority 130 outbound do not conflict — Azure evaluates them in separate queues.

**`--nsg null` vs `--nsg ""`**  
`--nsg null` detaches an NSG from a subnet. `--nsg ""` fails. `--remove networkSecurityGroup` also works.

**Application Gateway — Dedicated Subnet Required**  
Cannot share subnet with any other resource type. Minimum /27 for lab, /24 for production. Three non-negotiable inbound NSG rules or provisioning fails:  
1. `GatewayManager` service tag → ports 65200–65535 (priority 100)  
2. `AzureLoadBalancer` service tag → any (priority 200)  
3. `Internet` → ports 80, 443 (priority 300)

**Bastion Target VM NSG Rule Required**  
Bastion can connect but cannot reach the VM without an inbound NSG rule allowing SSH (22) or RDP (3389) from the AzureBastionSubnet range (`10.0.7.0/26`). No clear error message — just a failed connection.

**Static Private IPs — Declared in Two Places**  
Must be declared in Bicep (`privateIPAllocationMethod: 'Static'`) AND set via CLI on existing NICs. CLI alone is overwritten on next Bicep deploy. NIC IP config name is `ipconfig1` (not the VM name).

**Subnet Tagging Not Supported**  
`az network vnet subnet create` does not accept `--tags`. Subnets inherit tags from the VNet.

---

### 4.3 Virtual Machines & Compute

**Windows VM `computerName` — 15 Character Limit**  
Azure resource name can be any valid length, but Windows OS hostname is hard-limited to 15 characters. `vm-win-dev-wus3-01` = 18 chars → fails at provisioning with `InvalidParameter: osProfile.computerName`.  
Fix: pass `computerName` as a separate explicit parameter. Use `win-${env}-${instance}` = `win-dev-01` (10 chars). Do not rely on `take(vmName, 15)` for multi-VM deployments — produces duplicate computer names.

**Windows Server 2025 Azure Edition — Hotpatch Settings**  
Using `patchMode: 'AutomaticByOS'` fails with `InvalidParameter`. Required configuration:
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
`enableHotpatching` belongs inside `patchSettings`, not in `windowsConfiguration` directly.

**Linux Data Disk — Never Mount at /mnt**  
Azure Linux agent mounts the temporary disk (sdb) at `/mnt` by default via cloud-init. Mounting a data disk at `/mnt` creates a conflict — after reboot the temp disk wins. Use `/data` or any other path.

**Linux Disk Mount — Always UUID, Never Device Name**  
Device names (`/dev/sda`, `/dev/sdb`) can shift on reboot or when another disk is added. UUID never changes. Always use UUID in fstab: `UUID=xxxx /data ext4 defaults,nofail 0 2`. The `nofail` flag is critical — without it a missing disk can prevent the VM from booting. Get UUID: `sudo blkid -s UUID -o value /dev/sdc`.

**Disk Resize Is Two Separate Steps**  
1. `az disk update --size-gb N` — expands the block device (Azure level)  
2. `sudo resize2fs /dev/sdX` — expands the filesystem to use the new space (OS level)  
Online resize is possible for ext4 without unmounting.

**VM Auto-Created NSGs and NICs**  
When `--nsg` is passed incorrectly or omitted on `az vm create`, Azure creates orphaned NSGs named `{vmName}NSG` attached to the NIC, not the subnet. Delete sequence: detach from NIC first (`az network nic update --remove networkSecurityGroup`), then delete NSG. Prevention: use subnet-level NSG and omit `--nsg` from `az vm create` entirely.

**Custom Script Extension — SAS Token Type**  
CSE agent makes an anonymous HTTP fetch to download script blobs. User delegation SAS tokens require Entra ID token — CSE has no AD context, returns 403. Use service SAS (account key auth), not user delegation SAS. Production: managed identity + Storage Blob Data Reader role.

**BGInfo Extension — No Longer in Portal Marketplace**  
Deploy via CLI only: `az vm extension set --name BGInfo --publisher Microsoft.Compute --version 2.1 --settings '{}'`

**MDE.Windows / MDE.Linux — Auto-Deployed, Do Not Remove**  
Microsoft Defender for Endpoint extensions appear automatically via Defender for Cloud on Visual Studio subscriptions. Leave in place — they provide security telemetry.

**`--assign-identity "[system]"` at Creation Time**  
Correct pattern for provisioning system-assigned managed identity on a Web App or VM. Assigning after creation introduces a timing window where RBAC assignment may be attempted before the identity GUID exists in Entra ID.

---

### 4.4 Storage & Key Vault

**Storage Account Names — Globally Unique, No Hyphens**  
Names must be lowercase, 3–24 chars, no hyphens, globally unique across all of Azure (not just your subscription). `st-az104-dev-wus3-01` → invalid. `staz104devwus301` → correct. Add owner-specific prefix to avoid collisions with other tenants.

**Key Vault Soft Delete — Blocks Secret Name Reuse**  
Soft delete is on by default. Deleted secrets are retained for the soft-delete retention period (7 days in lab). Cannot reuse a secret name during retention without purging: `az keyvault secret purge --vault-name kv-az104-dev-wus3-01 --name secret-name`.

**Key Vault RBAC — Two Separate Access Grants Required**  
Creating KV with `--enable-rbac-authorization true` means even the creator needs an explicit role assignment to write secrets (`Key Vault Secrets Officer`). For Bicep deployments using `getSecret()`, ARM also needs access: `az keyvault update --enabled-for-template-deployment true`. Both are required independently.

**KV Reference Strings in PowerShell — Use Cloud Shell**  
The `@` symbol and parentheses in Key Vault reference values (`@Microsoft.KeyVault(...)`) cause parsing failures in PowerShell even inside quotes. Switch to Cloud Shell Bash for any `az webapp config appsettings set` commands containing KV references.

**Storage Public Access — Disable After Private Endpoint Confirmed**  
Disable only after nslookup confirms private IP resolution is working. Confirm-then-lockdown sequence:
1. Deploy private endpoint  
2. Verify private connectivity from inside VNet  
3. Disable public access  
4. Verify public access is blocked  
**Re-enable before teardown** — CLI delete commands from Cloud Shell cannot reach a storage account with public access disabled.

**Disabling Storage Public Access Returns 404, Not 403**  
Intentional Azure behavior. When public network access is disabled, Azure Storage does not acknowledge the endpoint exists from the public internet. 404 reveals nothing; 403 would reveal the resource exists. This is the stronger security posture.

**SSH Keys — Cloud Shell Generates Ephemeral Keys**  
`--generate-ssh-keys` in Cloud Shell saves to `~/.ssh/id_rsa` in the session — lost when private browsing closes. Always store private key in Key Vault immediately: `az keyvault secret set --name vm-ssh-private-key --file ~/.ssh/id_rsa`. Key Vault stores public key at one secret name — store private key under a distinct name.

**Windows SSH Key Location**  
Writing to `C:\Users\gerar\.ssh\` may fail due to deny-only Administrators group. Use alternate path: `C:\Users\gerar\az-104\az104_id_rsa`. Keep out of git via `.gitignore`.

---

### 4.5 Load Balancer

**Standard LB Health Probes Blocked by NSG by Default**  
Standard SKU health probe traffic arrives tagged with the `AzureLoadBalancer` service tag. Without an explicit NSG allow rule for this tag, probes are silently dropped. Both VMs register as Unhealthy and LB drops all traffic. Basic SKU allowed this implicitly — Standard does not. Always include `allow-azure-lb` rule (priority 120, source: `AzureLoadBalancer`, port 80) in NSG from day one.

**Standard LB Provides No Implicit Outbound SNAT**  
Backend pool VMs with no public IP and no outbound rule have zero outbound internet connectivity. `apt install` appeared to complete successfully but nginx was not installed — apt does not always exit non-zero when downloads fail silently. Always include a second public IP (`pip-lb-outbound`) and outbound rule at initial deployment. Verify with `systemctl status`, never trust package manager exit status alone.

**LB Object Model: PIP → Frontend IP Config → Rule**  
Outbound rules and inbound rules must reference a **frontend IP configuration** object, not a public IP directly. Create the frontend IP config before creating the rule that references it. Portal outbound rule dropdown only populates after the frontend IP config exists.

**Round-Robin LB Is Not Strictly Alternating**  
Azure Standard LB uses a 5-tuple hash. Browser HTTP keep-alive reuses TCP connections — same VM serves multiple requests. Correct test:
```bash
for i in {1..20}; do curl -s http://<LB-IP> | grep "Served by"; done | sort | uniq -c
```
Expect uneven distribution (e.g., 13/7) not exactly 10/10.

**Browsers Silently Upgrade Bare IPs to HTTPS**  
Chrome/Edge automatically prepend `https://` to bare IPs. Always type `http://` explicitly when testing HTTP-only backends.

---

### 4.6 DNS & Private Endpoints

**Private DNS Zone Must Be Linked to ALL VNets That Need Resolution**  
Linking only to vnet-hub means vnet-spoke VMs query Azure DNS without the private zone override and receive the public IP. DNS resolution and network routing are independent — peering establishes the route; VNet DNS zone links determine DNS resolution. Both must be configured.

**Private DNS Zone Names Are Fixed**  
The zone name for each Private Link service is mandated by Azure and not configurable. Using any other name prevents automatic A record creation.

| Service | Required Zone Name |
|---|---|
| Blob Storage | `privatelink.blob.core.windows.net` |
| File Storage | `privatelink.file.core.windows.net` |
| SQL Database | `privatelink.database.windows.net` |
| Key Vault | `privatelink.vaultcore.azure.net` |
| Container Registry | `privatelink.azurecr.io` |
| App Service | `privatelink.azurewebsites.net` |

**AzureBastionSubnet — Exact Name Required**  
Must be named exactly `AzureBastionSubnet`. No CAF naming, no variations. Minimum size /26.

**Policy Evaluation Delay After Assignment**  
Azure Policy evaluation runs asynchronously. Allow 5–15 minutes after assignment before compliance dashboard updates. Trigger immediate evaluation: `az policy state trigger-scan --resource-group rg-az104-dev-wus3-01`.

---

### 4.7 Bastion

**NSG Compliance Check Fires at Subnet Attachment Time**  
Attaching a non-compliant NSG to `AzureBastionSubnet` fails the compliance check even if Bastion isn't being deployed.

**Inline NSG Rules Required for Bastion**  
Define rules inside `properties.securityRules: [...]` on the NSG resource, not as separate child resources. Separate child resources deploy in parallel and may not be complete when the compliance check runs.

**Protocol Must Be `'*'` on Bastion VirtualNetwork Rules**  
`AllowBastionHostCommunication` (inbound) and `AllowBastionCommunication` (outbound) must use `protocol: '*'`, not `'Tcp'`. Bastion internal comms use both TCP and UDP.

**Source `'*'` Required on Bastion Outbound Rules**  
`AllowSshRdpOutbound`, `AllowAzureCloudOutbound`, `AllowHttpOutbound` use `sourceAddressPrefix: '*'`, not `'VirtualNetwork'`.

**Two-Pass Deployment Required**  
Even with correct rules, deploying Bastion in the same pass as NSG/subnet attachment can fail. Use `deployBastionHost bool` condition flag in Bicep. Pass 1: NSG + rules + subnet attachment. Pass 2: Bastion host.

**Bastion Standard SKU Cost**  
~$0.19/hr (~$140/mo). No equivalent of AppGW stop command — delete and redeploy, or use the condition flag. Stop/delete when the lab phase is complete.

---

### 4.8 Container Apps & Registry

**Subnet Delegation Required for Container Apps**  
`snet-capp-dev-wus3-01` must be delegated to `Microsoft.App/environments` before Container Apps Environment can deploy. Add `--delegations Microsoft.App/environments` to subnet create command.

**Minimum Subnet Size /23**  
Container Apps Environment requires at least 512 addresses (/23).

**AcrPull Role Assignment Timing with System-Assigned MI**  
System-assigned managed identity only exists after the Container App is created. Role assignment in the same deployment pass fails. Prefer user-assigned MI created as infrastructure ahead of time with the role pre-assigned.

**`activeRevisionsMode: 'Multiple'` Required for Traffic Splitting**  
Required for traffic splitting between revisions.

**Traffic Weights in Bicep Require Hardcoded Revision Names**  
Revision names are auto-generated at deploy time. Manage traffic weights via CLI post-deploy: `az containerapp ingress traffic set`. Do not attempt to set traffic weights in Bicep.

**`minReplicas: 0` — Scale to Zero**  
Pays nothing when idle. First request cold-starts in seconds.

**Internal CAE Cannot Be Changed to External**  
After creation, this property is immutable. Redeploy required.

---

### 4.9 Monitoring & Backup

**Azure Diagnostics (LAD/IaaSDiagnostics) Deprecated March 2026**  
Guide steps referencing legacy "Diagnostic settings → Add diagnostic setting → send to workspace" for VMs use the deprecated LAD/MMA path. Current correct approach: Azure Monitor Agent (AMA) + Data Collection Rule (DCR). Remove legacy extensions before installing AMA to avoid conflicts.

**DCR Association — No `-g` Flag**  
`az monitor data-collection rule association create` does not accept `-g`. Uses `--resource` with full VM resource ID.

**DCR Creation Requires JSON File**  
`--rule-file dcr.json` — inline JSON flags removed in recent CLI versions.

**KQL — `identity_claim_oid_g` Column Varies by LAW Version**  
Column name not present in all Log Analytics Workspace versions. Use a safer query:
```kql
AzureDiagnostics
| where ResourceType == "VAULTS"
| where OperationName == "SecretGet"
| project TimeGenerated, CallerIPAddress, OperationName, ResultType
| order by TimeGenerated desc
```

**KV Diagnostic Logs — 5–15 Minute Lag**  
Logs take 5–15 minutes to appear in LAW after the diagnostic setting is created. Trigger a read first (`az keyvault secret show`), wait, then query.

**Recovery Services Vault — RG Deletion Blocked by Backup Data**  
`az group delete` fails if RSV contains protected items. Teardown sequence:
1. `az backup protection disable ... --delete-backup-data true --yes` (per VM)
2. Verify no protected items remain
3. Wait 10–30 minutes (restore point collections must clear)
4. `az group delete`

Container name format is exact and case-sensitive: `IaasVMContainer;iaasvmcontainerv2;{rg};{vm-name}`. Always query exact name: `az backup container list ... --query "[].name"`.

**Logic Apps Consumption Tier — API Connections Tied to User Auth**  
Pre-built connectors (Azure VM, Office 365) authenticate as the deploying user, not managed identity. For VM start/stop automation: use Automation Account with PowerShell runbook (free tier 500 min/mo, native managed identity).

**Network Watcher — Auto-Created by Azure**  
Created automatically in `NetworkWatcherRG` when first network resource is deployed in a region. No manual creation needed. `NetworkWatcherAgentLinux` extension required on VM before `az network watcher test-connectivity` works. The `--preview` flag in output is expected, not an error.

---

### 4.10 Bicep / IaC

**`existing` Keyword**  
References a resource already in Azure without creating it. Returns a handle for dot-accessing properties (`law.properties.customerId`, `vnet.id`).

**`listKeys()` Function**  
Retrieves sensitive values not exposed as plain properties. Used for Log Analytics shared key: `listKeys(law.id, '2023-09-01').primarySharedKey`.

**`if (condition)` on Resources**  
Conditional resource deployment. The condition must evaluate using params known at deployment start, not module outputs.

**`dependsOn` — Legitimate Use Cases**  
When Bicep can't infer a dependency because the dependent resource doesn't reference the dependency in its properties (e.g., Bastion host depending on NSG rules, Front Door route depending on origin). The Bicep linter will flag `dependsOn` entries that are already inferred via `parent:` relationships — trust the linter on those.

**Front Door Route — Explicit `dependsOn` Required**  
Bicep cannot always infer the dependency chain for nested Front Door resources. Add `dependsOn: [origin]` to the route resource. Linter correctly removes `originGroup` from `dependsOn` since it's inferred via `parent: originGroup`.

**Bicep Is Idempotent**  
Re-running after a partial failure is safe. It skips resources that already exist and only creates missing ones. What-if always before deploy.

**What-if Verbosity — NIC Properties**  
NIC properties (`privateIPAddress`, `privateIPAddressVersion`, `allowPort25Out`) show as modifies in what-if but don't actually change. Azure-managed defaults. Known behavior, not a concern.

**`.bicepparam` — No String Interpolation**  
Cannot reference other parameters within the same `.bicepparam` file. `param tags = { env: env }` fails — `env` is not resolvable inside the same file. Use literals only: `param tags = { env: 'dev' }`.

**`.bicepparam` `getSecret()` — BCP258 Linter Warning**  
`@secure()` parameters without assignment trigger BCP258. Known false positive when secrets come via `getSecret()`. Does not block deployment.

**Role Assignment `name` — Use `guid()` with Stable Inputs**  
Use stable param values, not module outputs, as inputs to `guid()`. Module outputs aren't known at deployment start.

**Bootstrap Preflight — Smart Name Availability Check**  
Distinguish "taken by someone else" from "taken by a previous run." Check if resource already exists in the subscription first; only run the name-availability check for net-new resources:
```bash
ST_EXISTS=$(az storage account show --name $ST_NAME --query "name" -o tsv 2>/dev/null)
if [[ -z "$ST_EXISTS" ]]; then
  # run availability check
fi
```

---

### 4.11 Portfolio Infrastructure (ostebovik.net)

**GitHub Actions Workflow Not Auto-Generated by Bicep SWA Resource**  
`skipGithubActionWorkflowGeneration: false` requires Azure to have write access to the GitHub repo at deployment time. If not granted, the workflow file is never created. Add manually: `.github/workflows/azure-static-web-apps.yml`, add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret to repo settings.

**Static Web App Serves from GitHub, Not Storage Account**  
SWA requires at least an `index.html` at the repo root to serve content. Storage account holds static assets (images, diagrams) that pages reference. Push content to GitHub repo → CI/CD deploys it. Upload assets to storage via `az storage blob upload-batch`.

**Front Door Custom Domain — DNS Record Type**  
Use CNAME `@` (root domain) pointing to Front Door endpoint. Some registrars use `@`, others want the bare domain. Delete old ALIAS/CNAME records before adding the new one — they cannot coexist.

**Front Door WAF Does Not Natively Support Time-Based Rules**  
Operating hours enforcement implemented as a JavaScript check on page load (styled maintenance page outside 6am–9pm MST). Upgrade to a proper Front Door Rule Set when adding that feature production-properly.

**Storage Account Global Uniqueness — Add Owner Prefix**  
`stprodwus301` and `stgeostwus301` were both taken by other tenants. Final working name: `stgeostewus301`. Always include owner-specific string in storage account names.

**Browsing to `ostebovik.net` After DNS Cutover May Show Old Site**  
Old SWA content cached by browser. Test in incognito/private window with `Ctrl+Shift+R`. `nslookup ostebovik.net` resolving to a Front Door edge IP (`132.220.38.112`) confirms DNS is pointing correctly regardless of cached content.

---

## 5. Resource Inventory — AZ-104 Lab

### Resource Group: `rg-az104-dev-wus3-01` (westus3)
  note: rg-az104-dev-wus3-01 deleted May 8, 2026
> Phase 2 resources were torn down in East US. Phase 3–4 resources are in westus3 in this RG.

**Networking**

| Resource | Name | Key Properties |
|---|---|---|
| Virtual Network | `vnet-az104-dev-wus3-01` | 10.0.0.0/16 |
| Subnet | `snet-win-az104-dev-wus3-01` | 10.0.1.0/24 · `nsg-win-dev-wus3-01` · legacy name |
| Subnet | `snet-linux-az104-dev-wus3-01` | 10.0.2.0/24 · `nsg-linux-dev-wus3-01` · legacy name |
| Subnet | `snet-web-dev-wus3-01` | 10.0.3.0/24 · `nsg-web-dev-wus3-01` |
| Subnet | `snet-api-dev-wus3-01` | 10.0.4.0/24 · `nsg-api-dev-wus3-01` |
| Subnet | `snet-data-dev-wus3-01` | 10.0.5.0/24 · `nsg-data-dev-wus3-01` |
| Subnet | `snet-appgw-dev-wus3-01` | 10.0.6.0/24 · `nsg-appgw-dev-wus3-01` |
| Subnet | `AzureBastionSubnet` | 10.0.7.0/26 · `nsg-bastion-dev-wus3-01` · exact name required |
| Subnet | `snet-capp-dev-wus3-01` | 10.0.8.0/23 · no NSG · delegated: `Microsoft.App/environments` |
| NSG | `nsg-win-dev-wus3-01` | attached to snet-win |
| NSG | `nsg-linux-dev-wus3-01` | attached to snet-linux |
| NSG | `nsg-web-dev-wus3-01` | attached to snet-web · AppGW rules needed |
| NSG | `nsg-api-dev-wus3-01` | attached to snet-api · capstone rules needed |
| NSG | `nsg-data-dev-wus3-01` | attached to snet-data · capstone rules needed |
| NSG | `nsg-appgw-dev-wus3-01` | attached to snet-appgw · GatewayManager rules added |
| NSG | `nsg-bastion-dev-wus3-01` | on AzureBastionSubnet · inline rules required |

**Compute**

| Resource | Name | Key Properties |
|---|---|---|
| Virtual Machine | `vm-win-dev-wus3-01` | Windows Server 2025 Azure Edition · B2s · 10.0.1.4 · hotpatch · principalId: `671ba5ec-b434-49da-aba2-7c7be53ab01d` |
| Virtual Machine | `vm-linux-dev-wus3-01` | Ubuntu 24.04 LTS · B2s · SSH key auth · 10.0.2.4 · principalId: `c71f4cd1-4296-4785-ab5d-4f6e92b38c87` |
| NIC | `vm-win-dev-wus3-01VMNic` | attached to snet-win · 10.0.1.4 |
| NIC | `vm-linux-dev-wus3-01VMNic` | attached to snet-linux · 10.0.2.4 |
| OS Disk | `disk-os-win-dev-wus3-01` | Premium LRS · deleteOption=Delete |
| OS Disk | `disk-os-linux-dev-wus3-01` | Premium LRS · deleteOption=Delete |

**App Service / Container**

| Resource | Name | Key Properties |
|---|---|---|
| App Service Plan | `asp-az104-dev-wus3-01` | Linux · P0v3 · ~$41/mo |
| Web App | `app-az104-dev-wus3-01` | Python 3.11 · HTTPS only · system identity · staging slot (Phase 3) |
| Container Registry | `acrdevwus301` | `acrdevwus301.azurecr.io` · Basic · admin disabled · images: `az104-web:v1`, `az104-web:v2` |
| Container App Env | `cae-dev-wus3-01` | internal · snet-capp · 10.0.8.0/23 |
| Container App | `ca-dev-wus3-01` | `hello-project12:v2` · 80/20 traffic split |

> ⚠️ **ACR naming note:** Notes previously referenced `acraz104devwus301` but the deployed resource is `acrdevwus301`. The deployed name is authoritative.

**Shared Services**

| Resource | Name | Key Properties |
|---|---|---|
| Key Vault | `kv-az104-dev-wus3-01` | RBAC model · soft-delete 7d · `vm-admin-password`, `vm-ssh-key` secrets |
| Log Analytics | `law-az104-dev-wus03-01` | ⚠️ `wus03` not `wus3` · 30-day retention · PerGB2018 |
| Data Collection Rule | `dcr-az104-dev-wus3-01` | Microsoft-Perf, Microsoft-Syslog, Microsoft-Event → LAW |
| Storage Account | `staz104devwus301` | Standard LRS · container: scripts |
| Storage Account | `stdevwus301` | Standard LRS · legacy naming · candidate for deletion |
| App Gateway | `appgw-dev-wus3-01` | 20.125.120.212 · Standard_v2 · stop when not in use |

**Monitoring / Alerting (Phase 3)**

| Resource | Name | Key Properties |
|---|---|---|
| Action Group | `ag-az104-dev-wus3-01` | email: djeemunee@letter7.onmicrosoft.com |
| Metric Alert | `alert-cpu-high-linux` | CPU > 80% · 5min window · severity 2 · vm-linux-dev-wus3-01 |
| Scheduled Query Alert | `alert-heartbeat-vms` | heartbeat < 1 per 5min · severity 1 |

**Policy Assignments (on `rg-az104-dev-wus3-01`)**

| Assignment | Policy |
|---|---|
| `require-tag-env` | Require env tag (deny) |
| `require-tag-owner` | Require owner tag (deny) |
| `allowed-locations-wus3` | Allowed locations: westus3 (deny) |
| `appsvc-https-only` | App Service HTTPS only (deny) |
| `appsvc-managed-identity` | App Service managed identity required (deny) |
| `appsvc-no-remote-debug` | App Service disable remote debugging (deny) |
| `inherit-tag-env` | Inherit env from RG |
| `inherit-tag-owner` | Inherit owner from RG |
| `inherit-tag-project` | Inherit project from RG |
| `inherit-tag-phase` | Inherit phase from RG |

**Subnet Map**

| Subnet | CIDR | NSG |
|---|---|---|
| `snet-win-az104-dev-wus3-01` | 10.0.1.0/24 | `nsg-win-dev-wus3-01` |
| `snet-linux-az104-dev-wus3-01` | 10.0.2.0/24 | `nsg-linux-dev-wus3-01` |
| `snet-web-dev-wus3-01` | 10.0.3.0/24 | `nsg-web-dev-wus3-01` |
| `snet-api-dev-wus3-01` | 10.0.4.0/24 | `nsg-api-dev-wus3-01` |
| `snet-data-dev-wus3-01` | 10.0.5.0/24 | `nsg-data-dev-wus3-01` |
| `snet-appgw-dev-wus3-01` | 10.0.6.0/24 | `nsg-appgw-dev-wus3-01` |
| `AzureBastionSubnet` | 10.0.7.0/26 | `nsg-bastion-dev-wus3-01` |
| `snet-capp-dev-wus3-01` | 10.0.8.0/23 | none (delegated) |

**SSH Key**  
Private key location: `C:\Users\gerar\az-104\az104_id_rsa` — NOT in git, gitignored.

---

### Phase 2 Resources (East US — torn down)

| RG | Notable Resources |
|---|---|
| `rg-phase2-network` | `vnet-hub` (10.0.0.0/16), `vnet-spoke` (10.1.0.0/16), `nsg-web`, `nsg-db`, `vm-hub-test` (10.0.1.4), `pe-storage-blob`, `lab.ostebovik.net` DNS zone |
| `rg-phase2-storage` | `stlabeastus001` (LRS · static website · private containers), `stlabgrs001` (GRS · deleted after screenshots) |
| `rg-phase2-lb` | `lb-web` (Standard), `vm-web-01` (10.1.1.4), `vm-web-02` (10.1.1.5), `avset-web`, `pip-lb-web` (20.171.241.228), `pip-lb-outbound` |

---

## 6. Resource Inventory — Portfolio Production

### Resource Group: `rg-geoste-prod-wus3-01` (westus3)

| Resource | Name | Key Properties |
|---|---|---|
| Log Analytics | `law-prod-wus3-01` | centralized logging |
| Application Insights | `appi-prod-wus3-01` | frontend telemetry |
| Storage Account | `stgeostewus301` | static assets (diagrams, screenshots) |
| Key Vault | `kv-geoste-prod-wus3-01` | RBAC model · soft-delete · purge protection |
| Static Web App | `swa-prod-wus3-01` | GitHub CI/CD · `polite-beach-008d6f51e.7.azurestaticapps.net` |
| WAF Policy | `wafafdprodwus301` | attached to Front Door |
| Front Door | `afd-prod-wus3-01` | CDN · custom domain · HTTPS |
| Front Door Endpoint | `ep-portfolio-bbgjdthdagbvawhc.z01.azurefd.net` | DNS CNAME target |

**DNS Configuration (registrar)**

| Type | Host | Value |
|---|---|---|
| CNAME | `@` | `ep-portfolio-bbgjdthdagbvawhc.z01.azurefd.net` |

Old records deleted: ALIAS `@` → `lively-water-03cc5611e.7.azurestaticapps.net` and CNAME `www` → same (FamilyTreeRG — old site).

**GitHub Actions Workflow**  
File: `.github/workflows/azure-static-web-apps.yml`  
Secret: `AZURE_STATIC_WEB_APPS_API_TOKEN` in repo settings  
Behavior: push to `main` → deployed in <60 seconds

---

## 7. Pending Bicep Updates

### `vm-linux.bicep`
- [ ] Add `MDE.Linux` extension (Microsoft Defender for Endpoint)
- [ ] Add `NetworkWatcherAgentLinux` extension (`Microsoft.Azure.NetworkWatcher`, type `NetworkWatcherAgentLinux`, version `1.4`)
- [ ] Add NSG rule: AllowBastionSSH inbound from `10.0.7.0/26` (AzureBastionSubnet) on port 22 — currently CLI-only, won't survive redeploy
- [ ] SSH key rotation procedure — Cloud Shell generates new key per session; update KV secret and redeploy if VMs need to be reprovisioned

### `vm-win.bicep`
- [ ] Add `MDE.Windows` extension
- [ ] Add `NetworkWatcherAgentWindows` extension (`Microsoft.Azure.NetworkWatcher`)
- [ ] Add NSG rule: AllowBastionRDP inbound from `10.0.7.0/26` on port 3389 — currently CLI-only
- [ ] Fix `computerName` — currently uses `take(vmName, 15)` or hardcoded `win-dev-01`. Pass `computerName` as explicit parameter from `main.bicep` for multi-VM uniqueness.
- [ ] Verify tags use `param tags object` with no hardcoded overrides

### `bastion.bicep`
- [ ] Keep `deployBastionHost` feature flag — intentional cost-control (~$140/mo Standard SKU). Document it clearly.

### `main.bicep`
- [ ] Replace system-assigned MI on Container App with user-assigned MI — eliminates role assignment timing/two-pass issue
- [ ] Add `networkwatcher.bicep` module (Project 13, deferred)
- [ ] Remove or wire unused `project` parameter (linter warning `no-unused-params`)
- [ ] Add NSG rules for Phase 4 tier subnets (needed for capstone / any future 3-tier app):
  - `nsg-appgw-dev-wus3-01`: allow `GatewayManager` inbound, `AzureLoadBalancer` inbound
  - `nsg-web-dev-wus3-01`: allow HTTPS inbound from App Gateway subnet
  - `nsg-api-dev-wus3-01`: allow inbound from web subnet only
  - `nsg-data-dev-wus3-01`: allow inbound from api subnet only, SQL port 1433

### `az104-bootstrap.sh`
- [ ] Strip to essentials — resource creation moving to Bicep
- [ ] Keep: subnet creation with delegation (`Microsoft.App/environments` on `snet-capp`)
- [ ] Keep: static IP assignment on VM NICs after creation
- [ ] Keep: Bastion NSG note (NSG created in `bastion.bicep`, not bootstrap)
- [ ] Remove: individual resource creation blocks that now have Bicep modules
- [ ] Implement smart name-availability check (Option A — check if resource already exists in subscription before running global availability check)

### `dev.bicepparam`
- [ ] Verify `adminPassword` and `sshPublicKey` use `getSecret()` — ARM requires `--enabled-for-template-deployment true` on vault
- [ ] All tag values must be literals, not parameter references

### Portfolio Infrastructure (`bootstrap.sh` + modules)
- [ ] Implement Option A preflight check — smart name availability that skips resources already owned in subscription (currently commented-out workaround is in place)
- [ ] Add `www` CNAME at registrar → `ep-portfolio-bbgjdthdagbvawhc.z01.azurefd.net`

### `storage.bicep` (both repos)
- [ ] Delete `stdevwus301` — legacy naming, no active use, costs money. Verify no dependencies first.
- [ ] Verify tag key is `project` not `wkld` throughout

---

## 8. Portfolio Site — Current State & Pending Work

### What Is Live
- `ostebovik.net` resolves via Front Door → Static Web App
- Landing page (`index.html`) deployed and serving — Giants color palette, skill domain cards, stats bar, scroll reveal animations
- GitHub Actions CI/CD working — push to `main` = live in <60 seconds
- All infrastructure resources deployed and healthy in `rg-geoste-prod-wus3-01`
- Delete `rg-az104-dev-wus3-01` — after all evidence captured and skill domain pages populated (target: next week)
- Reorganize repo to match target folder structure above — move infrastructure files, create skill domain folders
- Reformat Phase 2 guide to match Phase 3 & 4 format (requires Phase 4 guide as template reference)
- Add Certifications section to landing page: Credly badges for AZ-900, CC (ISC2), AZ-104 (in-progress), AI-900 (planned) — between Skills and footer
- [ ] Capture all evidence from `rg-az104-dev-wus3-01` before deletion: Container App screenshots, VNet topology, ACR, all Phase 4 project artifacts

### Repo Structure (Target)
```
geoste-portfolio/
├── index.html
├── .github/
│   └── workflows/
│       └── azure-static-web-apps.yml
├── infrastructure/
│   ├── bootstrap.sh
│   ├── main.bicep
│   ├── prod.bicepparam
│   └── modules/
│       ├── monitoring.bicep
│       ├── keyvault.bicep
│       ├── storage.bicep
│       ├── staticwebapp.bicep
│       └── frontdoor.bicep
└── az-104/
    ├── identity-governance/
    │   ├── index.html
    │   ├── diagrams/
    │   └── screenshots/
    ├── networking/
    ├── compute-storage/
    ├── infrastructure-as-code/
    └── monitoring-security/
```

### Immediately Actionable Pending Work

- [ ] Build remaining skill domain pages
- [ ] Wire "View projects" links on landing page to actual skill domain pages
- [ ] Upload assets to `stgeostewus301` via `az storage blob upload-batch` (CLI, not portal drag-and-drop)
- [ ] Add resume link — dedicated page or linked PDF
- [ ] Backfill Identity & Governance domain — no projects mapped yet (Phase 1 content)

### Future / Planned
- [ ] Operating hours WAF rule — upgrade JS check to proper Front Door Rule Set
- [ ] Dynamic log display page — surface Application Insights / LAW data on portfolio page
- [ ] `/resources/` page — RPO vs RTO write-up, PowerShell vs Bash syntax reference, AZ-104 whiteboard, other reference docs
- [ ] AZ-104 exam — schedule and sit
- [ ] Azure AI Fundamentals (Exam AI-901) - https://learn.microsoft.com/en-us/credentials/certifications/exams/ai-901/
- [ ] AZ-305: Designing Microsoft Azure Infrastructure Solutions - https://learn.microsoft.com/en-us/credentials/certifications/exams/az-305/

---

## 9. Content Organization — Skill Domains

Phases are not used in navigation. The site organizes all work by skill domain. Phase numbering is preserved as detail inside each domain page, not as top-level navigation.

| Skill Domain | URL Path | Projects |
|---|---|---|
| Identity & Governance | `/identity-governance/` | Phase 1 (backfill pending) |
| Networking | `/networking/` | P3 (VNets/NSGs), P5 (LB), P6 (DNS/Private Endpoints), P13 (AppGW/Bastion) |
| Compute & Storage | `/compute-storage/` | P4 (Storage), P7 (Compute/Extensions), P8 (App Service/Containers), P12 (Container Apps) |
| Infrastructure as Code | `/infrastructure-as-code/` | P11 (Bicep), P12 (Container Apps), P14 (Key Vault/MI), P15 (Capstone) |
| Monitoring & Security | `/monitoring-security/` | P9 (Monitor/Log Analytics), P10 (Backup/Site Recovery), P14 (Key Vault audit) |
| AI & Automation | — | Coming soon |

**Standalone reference documents** (RPO vs RTO, PS vs Bash, AZ-104 whiteboard) → `/resources/` page, not inside any skill domain.

**Uneven volume is expected.** Networking has four projects; Identity & Governance has none yet. Lean into depth over breadth in thinner sections — one well-documented project with design decisions, lessons learned, and real screenshots is stronger than three thin entries.

---

## 10. Key Files & Deliverables

### Phase 2 (East US — complete)
| File | Description |
|---|---|
| `project3-vnet-setup.sh` | Full VNet, subnet, NSG, peering, VM deployment |
| `project3-network-topology.svg` | Hub-spoke topology with NSG boundaries |
| `project4-storage.sh` | Storage accounts, containers, SAS, lifecycle, static website |
| `project4-storage-architecture.svg` | Storage architecture with tiers and access methods |
| `project5-lb-architecture.svg` | LB topology with SNAT, probes, availability set |
| `project5-portfolio.html` | Project 5 write-up for ostebovik.net |
| `project6-dns-private-endpoint.svg` | Private endpoint and DNS architecture |
| `project6-portfolio.html` | Project 6 write-up for ostebovik.net |
| `phase2-lessons-learned.html` | All 14+ gotchas + LB vs App Gateway comparison |
| `phase2-projects-index.html` | Phase 2 landing page linking all projects |
| `phase2-teardown.ps1` | Full teardown in correct dependency order |
| `az104-phase3-guide.html` | Offline interactive guide for Phase 3 |
| `azure-rbac-hierarchy.svg` | Phase 1 RBAC group→role→scope hierarchy |
| `project2-governance.html` | Phase 1 Project 2 governance write-up |
| `phase1-cleanup.ps1` | Phase 1 resource teardown |

### Phase 3–4 AZ-104 Lab
| File | Description |
|---|---|
| `main.bicep` | Orchestrates all Bicep modules (az104 lab) |
| `dev.bicepparam` | Dev environment values; `getSecret()` for passwords/SSH key |
| `modules/storage.bicep` | Storage account module |
| `modules/vm-linux.bicep` | Linux VM + NIC module |
| `modules/vm-win.bicep` | Windows VM + NIC module |
| `modules/acr.bicep` | Container Registry module |
| `modules/appgw.bicep` | Application Gateway module |
| `modules/bastion.bicep` | Bastion host module with condition flag |
| `modules/ca.bicep` | Container App module |
| `modules/cae.bicep` | Container Apps Environment module |
| `az104-bootstrap.sh` | Pre-flight: RG, KV secret seeding, subnet delegation |
| `project14-deployment.sh` | Full CLI script for Project 14 (KV + Managed Identity) |
| `project14-architecture.svg` | Architecture diagram: App Service → Key Vault → Log Analytics |
| `project14-writeup.md` | Project 14 design decisions and lessons learned write-up |

### Portfolio Infrastructure (ostebovik.net)
| File | Description |
|---|---|
| `infrastructure/bootstrap.sh` | Creates `rg-geoste-prod-wus3-01`, preflight checks, calls `main.bicep` |
| `infrastructure/main.bicep` | Orchestrates five portfolio modules in dependency order |
| `infrastructure/prod.bicepparam` | All production parameter values |
| `infrastructure/modules/monitoring.bicep` | Deploys `law-prod-wus3-01` and `appi-prod-wus3-01` |
| `infrastructure/modules/keyvault.bicep` | Deploys `kv-geoste-prod-wus3-01` (RBAC, soft-delete, purge protection) |
| `infrastructure/modules/storage.bicep` | Deploys `stgeostewus301` |
| `infrastructure/modules/staticwebapp.bicep` | Deploys `swa-prod-wus3-01` connected to GitHub |
| `infrastructure/modules/frontdoor.bicep` | Deploys Front Door, WAF, endpoint, origin, route, custom domain, TLS cert |
| `index.html` | Portfolio landing page (root of repo) |
| `.github/workflows/azure-static-web-apps.yml` | CI/CD: push to main → live in <60 seconds |

---

## 11. Exam Topic Coverage

| AZ-104 Domain | Projects | Confidence |
|---|---|---|
| Manage Azure identities and governance | P2 (Phase 1), policy assignments on RG | High |
| Implement and manage virtual networking | P3, P5, P6, P13 | High |
| Implement and manage storage | P4 | High |
| Deploy and manage Azure compute resources | P7, P8, P11, P12, P15 | High |
| Monitor and maintain Azure resources | P9, P10, P14 | High |
| Infrastructure as Code (Bicep) | P11, P12, P14, P15 | High |
| Identity & Governance (Phase 1 backfill) | P1–P2 | Medium — needs portfolio documentation |

---

## 12. Quick Reference — Commands to Remember

```bash
# Fix Windows CRLF line endings before running .sh in Cloud Shell
sed -i 's/\r//' script.sh

# Ensure Cloud Shell has clean copy of repo
cd ~ && rm -rf geoste-portfolio
git clone https://github.com/geostebovik/geoste-portfolio
cd geoste-portfolio && chmod +x bootstrap.sh

# Get your Entra Object ID (for KV admin role assignment)
az ad signed-in-user show --query id -o tsv

# Get managed identity principal ID from VM
az vm show -g $RG -n $VM --query "identity.principalId" -o tsv

# Get managed identity principal ID from Web App
az webapp identity show -g $RG -n $APP --query principalId -o tsv

# Get policy definition ID (never hardcode)
az policy definition list --query "[?displayName=='Allowed locations'].name" -o tsv

# Get exact backup container name (never construct manually)
az backup container list -g $RG --vault-name $RSV \
  --backup-management-type AzureIaasVM --query "[].name" -o tsv

# Tag all resources in RG at once
az resource list -g $RG --query "[].id" -o tsv | while read ID; do
  az resource tag --ids "$ID" --tags $TAGS --is-incremental 2>/dev/null || true
done

# Enable ARM to retrieve Key Vault secrets during Bicep deployment
az keyvault update -n $KV -g $RG --enabled-for-template-deployment true

# Assign Key Vault Secrets Officer to yourself
USER_OID=$(az ad signed-in-user show --query id -o tsv)
KV_ID=$(az keyvault show -n $KV -g $RG --query id -o tsv)
az role assignment create --assignee $USER_OID \
  --role "Key Vault Secrets Officer" --scope $KV_ID

# Assign Key Vault Secrets User to managed identity
az role assignment create --assignee $APP_PRINCIPAL \
  --role "Key Vault Secrets User" --scope $KV_ID

# DCR association (no -g flag — scope from resource ID)
az monitor data-collection rule association create \
  -n "dcra-name" --rule-id $DCR_ID --resource $VM_ID

# Bicep what-if (always before deploy)
az deployment group create -g $RG -f main.bicep -p dev.bicepparam --what-if

# Run command on VM without public IP
az vm run-command invoke -g $RG -n $VM \
  --command-id RunShellScript --scripts "your command here"

# Purge a soft-deleted Key Vault secret
az keyvault secret purge --vault-name $KV --name secret-name

# Upload asset folder to storage account (CLI, not portal)
az storage blob upload-batch \
  --account-name stgeostewus301 \
  --destination content/az-104/infrastructure-as-code \
  --source ./az-104/infrastructure-as-code \
  --auth-mode login

# Trigger immediate Azure Policy compliance scan
az policy state trigger-scan --resource-group rg-az104-dev-wus3-01

# Re-enable storage public access before teardown
az storage account update --name stlabeastus001 \
  --resource-group rg-phase2-storage --public-network-access Enabled

# Verify LB round-robin distribution (not strictly alternating)
for i in {1..20}; do curl -s http://<LB-IP> | grep "Served by"; done | sort | uniq -c

# KQL — Key Vault secret access audit (use in LAW → Logs)
# AzureDiagnostics
# | where ResourceType == "VAULTS"
# | where OperationName == "SecretGet"
# | project TimeGenerated, CallerIPAddress, OperationName, ResultType
# | order by TimeGenerated desc
```

---

*Merged from: PHASE02-NOTES.md · PHASE03-NOTES.md · PHASE04-NOTES.md · Phase 4 + Portfolio Build session summary*  
*Last updated: May 8, 2026*
