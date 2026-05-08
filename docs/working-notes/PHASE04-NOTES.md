# AZ-104 Project Notes
> Living document — update as work progresses. Bring this into each new session.

---

## Pending Bicep Updates
Items identified during Phase 4 work that should be added to Bicep modules after az-104 project completes. Do not add to bootstrap — these belong in Bicep.

### vm-linux.bicep
- [ ] Add `MDE.Linux` extension (Microsoft Defender for Endpoint)
- [ ] Add `NetworkWatcherAgentLinux` extension (enables `az network watcher test-connectivity`)
  - Publisher: `Microsoft.Azure.NetworkWatcher`
  - Type: `NetworkWatcherAgentLinux`
  - Version: `1.4`
- [ ] Add NSG rule: AllowBastionSSH inbound from `10.0.7.0/26` (AzureBastionSubnet) on port 22
  - Currently added via CLI, not in Bicep — will not survive redeploy

### vm-win.bicep
- [ ] Add `MDE.Windows` extension (Microsoft Defender for Endpoint)
- [ ] Add `NetworkWatcherAgentWindows` extension
  - Publisher: `Microsoft.Azure.NetworkWatcher`
  - Type: `NetworkWatcherAgentWindows`
- [ ] Add NSG rule: AllowBastionRDP inbound from `10.0.7.0/26` on port 3389
  - Currently added via CLI, not in Bicep — will not survive redeploy

### bastion.bicep
- [ ] Consider removing `deployBastionHost` two-pass flag once production pattern confirmed
  - OR keep as a cost-control feature flag (Bastion ~$140/mo Standard SKU)
  - Decision: keep flag, document it clearly as intentional

### main.bicep / general
- [ ] Replace system-assigned managed identity on Container App with user-assigned MI
  - Eliminates role assignment timing/two-pass issue
  - User-assigned MI created as infrastructure, role pre-assigned before app deploys
  - See: Project 12 AcrPull role assignment section
- [ ] Add `networkwatcher.bicep` module (Project 13, pending)

### bootstrap (az104-bootstrap.sh)
- [ ] Strip to essentials only — resource creation moving to Bicep
- [ ] Keep: subnet creation with delegation (`Microsoft.App/environments` on snet-capp)
- [ ] Keep: static IP assignment on VM NICs after creation
- [ ] Keep: Bastion NSG note (NSG created in bastion.bicep, not bootstrap)
- [ ] Remove: individual resource creation blocks that now have Bicep modules

---

## Naming Convention Reference (CAF Standard)
- Pattern: `{type}-{env}-{region}-{instance}`
- Examples: `vm-win-dev-wus3-01`, `nsg-web-dev-wus3-01`, `cae-dev-wus3-01`
- Storage/ACR: no hyphens — `stdevwus301`, `acrdevwus301`
- `wkld` (az104) appears ONLY in the resource group name, not individual resources
- Legacy resources with `az104` in name (VM subnets): accepted, cleanup deferred

---

## Lessons Learned / Gotchas

### PowerShell vs Bash
- **PowerShell + Azure CLI + special characters in values is a known friction point. When a command has complex string values, Cloud Shell Bash is almost always cleaner.
- **KV reference strings in PowerShell: The @ symbol and parentheses in Key Vault reference values cause parsing failures even inside quotes. Switch to Cloud Shell Bash for any az webapp config appsettings set commands containing KV references.
### Windows / Local Environment
- **Docker Desktop install fails**: Delete `C:\ProgramData\DockerDesktop` first, then run installer as admin. Known issue, easily found by searching the error string.
- **SSH key permissions**: Writing to `C:\Users\gerar\.ssh\` may fail due to deny-only Administrators group. Use alternate path (`C:\Users\gerar\az-104\`) and keep out of git via `.gitignore`.
- **File association**: Files without extensions (like `id_rsa`) may open with wrong app in Windows. Use path directly in dialog boxes rather than browsing.

### SSH Keys
- **Cloud Shell generates ephemeral keys**: `--generate-ssh-keys` in Cloud Shell saves to `~/.ssh/id_rsa` in the session — lost when private browsing session ends. Always store private key in Key Vault immediately after generation: `az keyvault secret set --name vm-ssh-private-key --file ~/.ssh/id_rsa`
- **Key Vault stored public key, not private**: The bootstrap stored the public key in KV as `vm-ssh-key`. Bastion requires the private key. Store private key separately under a distinct secret name.
- **VM key reset**: `az vm user update --ssh-key-value` to replace authorized key on a running VM without redeployment.

### Networking
- **NSG rule priorities are per-direction**: Priority 130 inbound and 130 outbound do not conflict — Azure evaluates them in separate queues.
- **`--nsg null`** detaches an NSG from a subnet. `--nsg ""` fails. `--remove networkSecurityGroup` also works.
- **Bastion target VM NSG**: Must have inbound rule allowing SSH (22) or RDP (3389) from `AzureBastionSubnet` range (`10.0.7.0/26`). Without this, Bastion connects but cannot reach the VM — no clear error message.
- **AppGW mandatory NSG rules**: Three non-negotiable inbound rules required or gateway fails to provision:
  1. GatewayManager → 65200-65535 (priority 100)
  2. AzureLoadBalancer → any (priority 200)
  3. Internet → 80,443 (priority 300)
- **Static private IPs on VMs**: Must be declared in Bicep (`privateIPAllocationMethod: 'Static'`) AND set via CLI on existing NICs. CLI alone is overwritten on next Bicep deploy. NIC IP config name is `ipconfig1` (not the VM name).

### Bastion
- **NSG compliance check fires at subnet attachment time**, not just at Bastion provisioning. Attaching a non-compliant NSG to `AzureBastionSubnet` fails even if Bastion isn't being deployed.
- **Inline NSG rules required**: Define rules inside `properties.securityRules: [...]` on the NSG resource, not as separate child resources. Separate child resources deploy in parallel and may not be complete when the compliance check runs.
- **Protocol must be `'*'` on VirtualNetwork rules**: `AllowBastionHostCommunication` (inbound) and `AllowBastionCommunication` (outbound) must use `protocol: '*'` not `'Tcp'`. Bastion internal comms use both TCP and UDP.
- **Source `'*'` on outbound rules**: `AllowSshRdpOutbound`, `AllowAzureCloudOutbound`, `AllowHttpOutbound` use `sourceAddressPrefix: '*'` not `'VirtualNetwork'`.
- **Two-pass deployment**: Even with correct rules, deploying Bastion in the same pass as the NSG/subnet attachment can fail. Pass 1: NSG + rules + subnet attachment. Pass 2: Bastion host. Use `deployBastionHost bool` condition flag.
- **Standard SKU costs ~$140/mo** — stop when not in use. No equivalent of AppGW stop command; delete and redeploy or use the condition flag.

### Container Apps
- **Subnet delegation required**: `snet-capp-dev-wus3-01` must be delegated to `Microsoft.App/environments` before CAE can deploy. Add `--delegations Microsoft.App/environments` to subnet create command.
- **Subnet size minimum /23**: Container Apps Environment requires at least 512 addresses.
- **AcrPull role assignment timing**: System-assigned MI only exists after Container App is created. Role assignment in same deployment pass fails. Prefer user-assigned MI created as infrastructure ahead of time.
- **`activeRevisionsMode: 'Multiple'`** required for traffic splitting between revisions.
- **Traffic weights in Bicep require hardcoded revision name**: Revision names are auto-generated at deploy time. Manage traffic weights via CLI post-deploy (`az containerapp ingress traffic set`) rather than in Bicep.
- **Scale to zero**: `minReplicas: 0` — pays nothing when idle. First request cold-starts in seconds.
- **Internal CAE cannot be changed to external** after creation — redeploy required.

### Bicep Patterns
- **`existing` keyword**: References a resource already in Azure without creating it. Returns a handle for dot-accessing properties (`law.properties.customerId`, `vnet.id`).
- **`listKeys()` function**: Retrieves sensitive values not exposed as plain properties. Used for Log Analytics shared key: `listKeys(law.id, '2023-09-01').primarySharedKey`.
- **`if (condition)` on resources**: Conditional resource deployment. The condition must evaluate using params known at deployment start, not module outputs.
- **`dependsOn` legitimate use**: When Bicep can't infer a dependency because the dependent resource doesn't reference the dependency in its properties — e.g., Bastion host depending on NSG rules that aren't referenced in its properties.
- **What-if verbosity**: NIC properties (`privateIPAddress`, `privateIPAddressVersion`, `allowPort25Out` etc.) and Azure-managed defaults show as modifies in what-if but don't actually change. Known behavior, not a concern.
- **Bicepparam: no string interpolation referencing other params** — values must be literals or expressions not involving other params.
- **Role assignment `name`**: Use `guid()` with stable inputs (param values, not module outputs) — module outputs aren't known at deployment start.

### Network Watcher
- **Auto-created by Azure** in `NetworkWatcherRG` when first network resource is deployed in a region. No manual creation needed.
- **`NetworkWatcherAgentLinux` extension required** on VM before `az network watcher test-connectivity` works.
- **`az network watcher test-connectivity` is preview** — flag appears in output, not an error.

---

## Key Resource Inventory

| Resource | Name | Notes |
|---|---|---|
| Resource Group | rg-az104-dev-wus3-01 | |
| VNet | vnet-az104-dev-wus3-01 | 10.0.0.0/16 |
| Linux VM | vm-linux-dev-wus3-01 | 10.0.2.4 static, snet-linux-az104-dev-wus3-01 |
| Windows VM | vm-win-dev-wus3-01 | 10.0.1.4 static, snet-win-az104-dev-wus3-01 |
| ACR | acrdevwus301 | acrdevwus301.azurecr.io |
| Key Vault | kv-az104-dev-wus3-01 | RBAC model |
| Log Analytics | law-az104-dev-wus03-01 | Note: wus03 not wus3 in name |
| CAE | cae-dev-wus3-01 | snet-capp-dev-wus3-01, 10.0.8.0/23, internal |
| Container App | ca-dev-wus3-01 | hello-project12:v2, 80/20 traffic split |
| App Gateway | appgw-dev-wus3-01 | 20.125.120.212, Standard_v2, stop when not in use |
| Bastion | bastion-dev-wus3-01 | Standard SKU, stop/delete when not in use |
| SSH Private Key | C:\Users\gerar\az-104\az104_id_rsa | NOT in git, .gitignored |

---

## Subnet Map

| Subnet | CIDR | NSG | Notes |
|---|---|---|---|
| snet-win-az104-dev-wus3-01 | 10.0.1.0/24 | nsg-win-dev-wus3-01 | Legacy name with az104 |
| snet-linux-az104-dev-wus3-01 | 10.0.2.0/24 | nsg-linux-dev-wus3-01 | Legacy name with az104 |
| snet-web-dev-wus3-01 | 10.0.3.0/24 | nsg-web-dev-wus3-01 | |
| snet-api-dev-wus3-01 | 10.0.4.0/24 | nsg-api-dev-wus3-01 | |
| snet-data-dev-wus3-01 | 10.0.5.0/24 | nsg-data-dev-wus3-01 | |
| snet-appgw-dev-wus3-01 | 10.0.6.0/24 | nsg-appgw-dev-wus3-01 | |
| AzureBastionSubnet | 10.0.7.0/26 | nsg-bastion-dev-wus3-01 | Exact name required by Azure |
| snet-capp-dev-wus3-01 | 10.0.8.0/23 | none | Delegated to Microsoft.App/environments |

---

*Last updated: Project 13 — Application Gateway, Bastion, Network Watcher (in progress)*
