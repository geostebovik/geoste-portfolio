# PHASE02-NOTES
## AZ-104 Phase 2 — Networking & Storage
### Master Reference Document
**Projects:** 3 (VNet/NSG/Peering) · 4 (Storage) · 5 (Load Balancer) · 6 (DNS/Private Endpoints)
**Status:** Complete — environment torn down
**Compiled from:** Full conversation history including all troubleshooting sessions

---

## 1. Pending Bicep Updates

> These are configurations that were applied manually during troubleshooting
> and must be reflected in any Bicep/IaC templates for Phase 4 capstone
> or future redeployments. Each item notes which Bicep module it belongs in.

### 1.1 NSG — `nsg-web` (module: `networking/nsg-web.bicep`)

The following rules were added **after** initial deployment during troubleshooting
and are not in the original project guide scripts. Any Bicep template for nsg-web
must include all five rules below:

```bicep
// Rule added during LB troubleshooting — CRITICAL for Standard SKU LB health probes
{
  name: 'allow-azure-lb'
  properties: {
    priority: 120
    access: 'Allow'
    protocol: 'Tcp'
    direction: 'Inbound'
    sourceAddressPrefix: 'AzureLoadBalancer'   // service tag — not an IP range
    sourcePortRange: '*'
    destinationAddressPrefix: '*'
    destinationPortRange: '80'
  }
}

// Rule CORRECTED during troubleshooting — source was wrongly set to '*'
// '*' blocks Bastion connections; 'Internet' blocks only public RDP
{
  name: 'deny-rdp-internet'
  properties: {
    priority: 400
    access: 'Deny'
    protocol: 'Tcp'
    direction: 'Inbound'
    sourceAddressPrefix: 'Internet'            // NOT '*' — see Lesson 04
    sourcePortRange: '*'
    destinationAddressPrefix: '*'
    destinationPortRange: '3389'
  }
}

// Rule added during VNet peering troubleshooting — allows peered VNet traffic
{
  name: 'allow-vnet-inbound'
  properties: {
    priority: 150
    access: 'Allow'
    protocol: '*'
    direction: 'Inbound'
    sourceAddressPrefix: 'VirtualNetwork'
    sourcePortRange: '*'
    destinationAddressPrefix: 'VirtualNetwork'
    destinationPortRange: '*'
  }
}
```

**Full corrected rule set for nsg-web (in priority order):**

| Priority | Name | Access | Source | Port |
|---|---|---|---|---|
| 100 | allow-http | Allow | Any | 80 |
| 110 | allow-https | Allow | Any | 443 |
| 120 | allow-azure-lb | Allow | AzureLoadBalancer | 80 |
| 150 | allow-vnet-inbound | Allow | VirtualNetwork | * |
| 400 | deny-rdp-internet | Deny | Internet | 3389 |

---

### 1.2 NSG — `nsg-db` (module: `networking/nsg-db.bicep`)

The `allow-vnet-inbound` rule is also required on nsg-db to allow Bastion
management access to future DB-tier VMs:

```bicep
{
  name: 'allow-vnet-inbound'
  properties: {
    priority: 150
    access: 'Allow'
    protocol: '*'
    direction: 'Inbound'
    sourceAddressPrefix: 'VirtualNetwork'
    sourcePortRange: '*'
    destinationAddressPrefix: 'VirtualNetwork'
    destinationPortRange: '*'
  }
}
```

---

### 1.3 Load Balancer — Outbound SNAT rule (module: `compute/lb-web.bicep`)

Standard SKU LB provides **no implicit outbound SNAT**. Any Bicep template
deploying a Standard LB must include a second public IP and an outbound rule.
This was discovered only when nginx installation failed silently on backend VMs.

```bicep
// Second public IP required for outbound (keep separate from inbound)
resource pipLbOutbound 'Microsoft.Network/publicIPAddresses@2023-05-01' = {
  name: 'pip-lb-outbound'
  location: location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

// Frontend IP config for outbound (separate from inbound fe-web)
// Must be created BEFORE the outbound rule that references it
resource lbFrontendOutbound 'Microsoft.Network/loadBalancers/frontendIPConfigurations@2023-05-01' = {
  name: 'fe-outbound'
  parent: lbWeb
  properties: {
    publicIPAddress: { id: pipLbOutbound.id }
  }
}

// Outbound rule — must reference frontend IP config, NOT the public IP directly
resource lbOutboundRule 'Microsoft.Network/loadBalancers/outboundRules@2023-05-01' = {
  name: 'outbound-snat'
  parent: lbWeb
  properties: {
    frontendIPConfigurations: [{ id: lbFrontendOutbound.id }]
    backendAddressPool: { id: lbBackendPool.id }
    protocol: 'All'
    allocatedOutboundPorts: 10000
  }
}
```

> **Dependency note:** In Bicep, `lbFrontendOutbound` must have a `dependsOn`
> relationship with `lbWeb` and must be fully provisioned before `lbOutboundRule`
> is created. The CLI equivalent is two separate `az network lb frontend-ip create`
> and `az network lb outbound-rule create` commands run sequentially.

---

### 1.4 VNet Peering — both directions required (module: `networking/peering.bicep`)

VNet peering requires two separate peering resource objects — one in each VNet.
If only one is created, `peeringState` shows `Initiated` not `Connected` and
traffic does not flow. Both must include `allowForwardedTraffic: true`.

```bicep
// Hub → Spoke
resource hubToSpoke 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-05-01' = {
  name: 'hub-to-spoke'
  parent: vnetHub
  properties: {
    remoteVirtualNetwork: { id: vnetSpoke.id }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true       // required for hub-spoke routing patterns
    allowGatewayTransit: false        // set true when VPN gateway exists in hub
  }
}

// Spoke → Hub (separate object, same subscription is fine)
resource spokeToHub 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2023-05-01' = {
  name: 'spoke-to-hub'
  parent: vnetSpoke
  properties: {
    remoteVirtualNetwork: { id: vnetHub.id }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    useRemoteGateways: false          // set true when hub has VPN gateway
  }
}
```

---

### 1.5 Private DNS Zone — link to both VNets (module: `networking/private-dns.bicep`)

The private DNS zone must be linked to **both** vnet-hub (with auto-registration)
and vnet-spoke (resolution only). Linking to hub only means spoke VMs cannot
resolve the private endpoint hostname to a private IP.

```bicep
resource dnsLinkHub 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  name: 'dns-link-hub'
  parent: privateDnsZone
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetHub.id }
    registrationEnabled: true    // auto-registers VM hostnames
  }
}

resource dnsLinkSpoke 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  name: 'dns-link-spoke'
  parent: privateDnsZone
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetSpoke.id }
    registrationEnabled: false   // resolution only — no auto-registration
  }
}
```

---

### 1.6 Storage Account — explicit public access setting (module: `storage/storage-main.bicep`)

Always set public network access explicitly. Default behaviour varies by
subscription policy. For private endpoint deployments, disable after endpoint
is confirmed working. Re-enable before running teardown scripts.

```bicep
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  properties: {
    publicNetworkAccess: 'Disabled'       // set after private endpoint confirmed
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}
```

> **Teardown note:** Re-enable public access before running delete scripts
> or the CLI cannot reach the storage account to delete blobs.

---

## 2. Lessons Learned / Gotchas

### Lesson 01 — VNet peering states Connected but ip route show has no hub route

**Category:** VNet Peering / Linux networking
**Encountered in:** Project 3

**Symptom:** Both peerings showed `peeringState: Connected` and
`peeringSyncLevel: FullyInSync`. Running `ip route show` on the spoke VM
showed only `10.1.1.x` routes — no route to `10.0.0.0/16` (hub VNet).
Ping to hub addresses timed out.

**Root cause (two parts):**
1. Azure SDN handles peered VNet routes at the hypervisor layer. Guest OS
   routing tables do **not** show peering routes. `ip route show` is not a
   valid tool for diagnosing VNet peering — it will always appear to be missing
   the remote VNet even when peering is fully functional.
2. Separately, `nsg-web` was missing the `allow-vnet-inbound` rule, so peered
   traffic arriving at the subnet was silently dropped at the NSG even though
   the route existed.

**Fix:**
- Add `allow-vnet-inbound` rule (priority 150, source: VirtualNetwork) to nsg-web
- Test peering by pinging a real VM in the hub — not a subnet gateway address
- Do not use `ip route show` to validate peering; use actual connectivity tests

**Do this differently next time:** Deploy a test VM in snet-shared at the same
time as the spoke VMs so peering has a real target to ping from day one.

---

### Lesson 02 — Pinging hub subnet gateway always times out

**Category:** Azure networking behaviour
**Encountered in:** Project 3

**Symptom:** `ping -c 4 10.0.1.1` (hub subnet gateway) returned 100% packet
loss. This was initially interpreted as a peering failure.

**Root cause:** Azure subnet gateways (the `.1` address in each subnet) do not
respond to ICMP ping. They are infrastructure addresses managed by Azure, not
reachable hosts. This behaviour is consistent and expected — it is not a
configuration problem.

**Fix:** Always test peering connectivity by pinging a **VM's private IP**, never
a subnet gateway address. Without a VM deployed in the hub subnet, there is
nothing to ping across the peering.

---

### Lesson 03 — Standard LB health probes blocked by NSG by default

**Category:** NSG / Standard Load Balancer SKU change
**Encountered in:** Project 5

**Symptom:** Both backend VMs showed as Down/Unhealthy in the LB backend pool.
Browser requests timed out. Portal message: "HTTP endpoint unreachable; meaning
either an NSG rule blocking port or unhealthy app listening on port."

**Root cause:** Standard SKU Load Balancer health probe traffic arrives tagged
with the `AzureLoadBalancer` service tag. Without an explicit NSG allow rule for
this tag, the NSG silently drops all probe traffic. Both VMs register as
Unhealthy and the LB drops all inbound requests. Basic SKU allowed this traffic
implicitly — Standard SKU does not. This is a documented but easy-to-miss
breaking change between SKUs.

**Fix:**
```bash
az network nsg rule create \
  --resource-group rg-phase2-network \
  --nsg-name nsg-web \
  --name allow-azure-lb \
  --priority 120 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound \
  --source-address-prefixes AzureLoadBalancer \
  --destination-port-ranges 80
```

**Do this differently next time:** Include this rule in nsg-web from initial
deployment — it is always required when a Standard LB backend pool uses this NSG.

---

### Lesson 04 — NSG deny rule with source `*` blocks Azure Bastion

**Category:** NSG / service tags
**Encountered in:** Project 5

**Symptom:** Portal showed an alert on the VM networking blade: "This rule
denies traffic from AzureLoadBalancer and may affect virtual machine connectivity."
The DenyRDP3389Internet rule had source `*` (any) instead of `Internet`.

**Root cause:** `*` matches all traffic sources including VirtualNetwork, which
encompasses Azure Bastion connections routed through the VNet. Using `*` on a
Deny rule could block Bastion SSH/RDP access entirely. `Internet` matches only
public internet traffic — Bastion connections from the VNet are excluded.

**Fix:**
```bash
az network nsg rule update \
  --resource-group rg-phase2-network \
  --nsg-name nsg-web \
  --name DenyRDP3389Internet \
  --source-address-prefixes Internet
```

**Key distinction:**
- `*` = everything (internet + VNet + peered VNets + Bastion)
- `Internet` = public internet only (Bastion connections unaffected)

---

### Lesson 05 — Standard LB provides no implicit outbound SNAT

**Category:** Standard Load Balancer SKU change
**Encountered in:** Project 5

**Symptom:** `sudo apt install nginx -y` appeared to complete but
`systemctl status nginx` returned "Unit nginx.service could not be found."
apt printed connection warnings to `azure.archive.ubuntu.com` but reported
success. VMs in the backend pool had no outbound internet access.

**Root cause:** Standard SKU LB does not provide implicit outbound SNAT for
backend pool VMs the way Basic SKU did. VMs with no public IP and no outbound
rule have zero outbound internet connectivity. Package manager appeared to
succeed because apt does not always exit non-zero when individual package
downloads fail.

**Fix:** Create a second public IP (`pip-lb-outbound`), add it as a frontend
IP config (`fe-outbound`) on the LB, then create an outbound rule:

```bash
az network lb frontend-ip create \
  --resource-group rg-phase2-lb \
  --lb-name lb-web \
  --name fe-outbound \
  --public-ip-address pip-lb-outbound

az network lb outbound-rule create \
  --resource-group rg-phase2-lb \
  --lb-name lb-web \
  --name outbound-snat \
  --frontend-ip-configs fe-outbound \
  --protocol All \
  --outbound-ports 10000 \
  --address-pool be-web
```

**Do this differently next time:** Include outbound SNAT rule in initial LB
deployment. Always verify package installation with `systemctl status` —
never rely on package manager exit message alone.

---

### Lesson 06 — Outbound rule CLI requires frontend IP config first

**Category:** Azure CLI / LB object model
**Encountered in:** Project 5

**Symptom:** `az network lb outbound-rule create` failed with
`.../loadBalancers/lb-web/outboundrules/outbound-snat was not found.`
Portal outbound rule dropdown did not show `pip-lb-outbound` as an option.

**Root cause:** The Azure Load Balancer object model has a required intermediate
layer: `Public IP → Frontend IP Config → Rule`. Outbound rules (and inbound
rules) must reference a **frontend IP configuration** object, not a public IP
directly. The public IP must first be attached to a frontend IP config.

**Fix:** Always create the frontend IP config before the rule that references it:
```bash
# Step 1 — must run first
az network lb frontend-ip create --name fe-outbound ...

# Step 2 — can only run after step 1 succeeds
az network lb outbound-rule create --frontend-ip-configs fe-outbound ...
```

**Portal equivalent:** The outbound rule dropdown only populates after the
frontend IP config exists. If the dropdown is empty, the frontend IP config
is missing.

---

### Lesson 07 — Round-robin LB does not mean strictly alternating

**Category:** Load Balancer behaviour / testing methodology
**Encountered in:** Project 5

**Symptom:** Browser always showed the same VM hostname when refreshing.
Even curl in a loop sometimes returned the same VM multiple times in a row.

**Root cause:** Azure Standard LB uses a 5-tuple hash (source IP, source port,
destination IP, destination port, protocol). Browser HTTP keep-alive reuses
TCP connections so the same VM serves multiple requests. Curl source ports
tend to cluster, producing runs on the same VM. Neither is a configuration
error — both are expected behaviour.

**Correct verification method:**
```bash
for i in {1..20}; do curl -s http://<LB-IP> | grep "Served by"; done | sort | uniq -c
```

This shows the distribution across 20 requests. Both VMs appearing in the
count confirms round-robin is working. Expect an uneven split (e.g., 13/7)
rather than exactly 10/10.

---

### Lesson 08 — Browsers silently upgrade bare IPs to HTTPS

**Category:** Browser behaviour / HTTP vs HTTPS
**Encountered in:** Project 5

**Symptom:** Opening `20.171.241.228` in Chrome/Edge produced
"secure connections not supported." The LB only had port 80 configured.

**Root cause:** Modern browsers (Chrome, Edge) automatically prepend `https://`
to bare IP addresses and domains without a scheme. Port 443 received no
response from the LB, producing a timeout/error that looks like an LB failure.

**Fix:** Always type `http://` explicitly when testing HTTP-only backends:
```
http://20.171.241.228
```

---

### Lesson 09 — apt install can silently fail when outbound access is blocked

**Category:** Linux package management / networking dependency
**Encountered in:** Project 5

**Symptom:** `sudo apt install nginx -y` printed connection warnings to
`azure.archive.ubuntu.com:80` but completed without a clear fatal error.
nginx was not installed despite no obvious failure message.

**Root cause:** When outbound port 80 is blocked, apt attempts package
downloads, receives connection timeouts, but does not always exit non-zero.
The install appears to succeed while silently doing nothing.

**Verification rule:** Always run both checks after installing a service:
```bash
sudo systemctl status nginx     # confirms service registered
curl http://localhost            # confirms service is listening
```

Never rely on package manager exit status alone as confirmation of success.

---

### Lesson 10 — Private DNS zone must be linked to ALL VNets that need resolution

**Category:** Private DNS / VNet linking
**Encountered in:** Project 6

**Symptom:** nslookup from vm-web-01 (vnet-spoke) returned a public IP for
the storage account instead of the private endpoint IP, even though the private
endpoint was correctly configured in vnet-hub.

**Root cause:** The private DNS zone was initially linked only to vnet-hub.
VMs in vnet-spoke queried Azure DNS (168.63.129.16) but that DNS server had
no override for the storage hostname because the zone link for vnet-spoke was
missing. Azure DNS only applies private zone overrides to VNets that have an
explicit link to that zone.

**Fix:** Add a second VNet link for vnet-spoke with `registrationEnabled: false`
(resolve only — no auto-registration):
```bash
az network private-dns link vnet create \
  --resource-group rg-phase2-network \
  --name dns-link-spoke \
  --zone-name "privatelink.blob.core.windows.net" \
  --virtual-network vnet-spoke \
  --registration-enabled false
```

**Key principle:** DNS resolution and network routing are independent. Peering
establishes the route. VNet DNS zone links determine DNS resolution. Both must
be configured for private endpoints to work from all VNets.

---

### Lesson 11 — Private DNS zone name is fixed, not configurable

**Category:** Azure Private DNS naming convention
**Encountered in:** Project 6

**Symptom:** N/A — noted during setup to prevent error.

**Root cause/context:** Azure uses a fixed, service-specific zone name for each
Private Link service. The zone name is not configurable. Using any other name
prevents automatic A record creation when private endpoints are deployed.

**Required zone names for common services:**

| Service | Private DNS Zone Name |
|---|---|
| Blob Storage | `privatelink.blob.core.windows.net` |
| File Storage | `privatelink.file.core.windows.net` |
| SQL Database | `privatelink.database.windows.net` |
| Key Vault | `privatelink.vaultcore.azure.net` |
| ACR | `privatelink.azurecr.io` |
| App Service | `privatelink.azurewebsites.net` |

---

### Lesson 12 — Disabling storage public access returns 404, not 403

**Category:** Azure Storage security behaviour
**Encountered in:** Project 6

**Symptom:** After disabling public network access on the storage account,
browser returned `404 WebContentNotFound` rather than the expected `403`.

**Root cause:** This is intentional Azure behaviour. When public network access
is disabled, Azure Storage does not acknowledge the endpoint exists from the
public internet — the service appears not to be present at all. A `403` would
reveal the resource exists but you lack permission. A `404` reveals nothing.
This is the stronger security posture ("security through obscurity at the
network layer").

**Portfolio note:** This distinction is worth explaining explicitly — it
demonstrates understanding of Azure security design, not just configuration.

---

### Lesson 13 — Subnets are not directly selectable during VM deployment

**Category:** Azure portal UX
**Encountered in:** Project 3

**Symptom:** Guide instructed deploying a VM "into snet-web" but no subnet
dropdown appeared initially in the VM creation flow.

**Root cause:** Azure portal VM creation requires selecting the Virtual Network
first, after which a Subnet dropdown populates with subnets belonging to that
VNet. The subnet is not independently selectable.

**Correct portal flow:**
`Networking tab → Virtual network: vnet-spoke → Subnet: snet-web`

---

### Lesson 14 — Teardown must re-enable storage public access first

**Category:** Operational / teardown dependency
**Encountered in:** Phase 2 teardown planning

**Root cause:** If storage public network access is left Disabled, CLI delete
commands run from outside the VNet (e.g., Cloud Shell without VNet integration)
cannot reach the storage account to delete blobs or the account itself.

**Teardown rule:** Always re-enable public access before running any delete
commands against storage accounts with public access disabled:
```bash
az storage account update \
  --name stlabeastus001 \
  --resource-group rg-phase2-storage \
  --public-network-access Enabled
```

---

### Lesson 15 — Policy evaluation delay after assignment (Phase 1 carryover)

**Category:** Azure Policy behaviour
**Encountered in:** Project 2 (Phase 1) — noted here for completeness

**Symptom:** After assigning a policy, resources showed as non-compliant for
5–15 minutes before the compliance dashboard updated.

**Root cause:** Azure Policy evaluation engine runs asynchronously. Assignment
does not immediately trigger evaluation of existing resources.

**Production fix:** Trigger immediate evaluation:
```bash
az policy state trigger-scan --resource-group rg-phase1-lab
```

---

## 3. Key Design Decisions

### Decision 01 — Hub-spoke topology instead of flat VNet

**Choice:** Deployed two VNets (vnet-hub and vnet-spoke) connected via peering
rather than a single flat VNet with multiple subnets.

**Reasoning:**
- Hub-spoke is the standard enterprise pattern for Azure landing zones
- Shared services (Bastion, DNS, future VPN gateway) live in the hub and are
  accessible to all spokes without duplicating them
- Each spoke is an independent blast radius — a misconfiguration in one spoke
  cannot directly affect another
- Demonstrates AZ-104 exam content (peering, hub-spoke) more thoroughly than
  a flat network would
- Maps directly to how real Azure environments are structured at scale

**Trade-off:** More complex to set up and debug than a flat VNet. Peering adds
an additional dependency layer that must be correctly configured on both sides.

---

### Decision 02 — Standard SKU for all networking resources

**Choice:** Used Standard SKU for Load Balancer and Public IPs throughout,
despite Basic SKU being simpler to configure.

**Reasoning:**
- Microsoft is retiring Basic SKU Load Balancer — all new deployments should
  use Standard
- Standard SKU is zone-redundant by default
- Standard LB supports availability zones, outbound rules, and multiple frontend
  IP configurations that Basic does not
- The additional configuration required (explicit SNAT, probe NSG rules) teaches
  the correct enterprise patterns, not deprecated shortcuts
- AZ-104 exam increasingly focuses on Standard SKU behaviour

---

### Decision 03 — No public IPs on backend VMs

**Choice:** All backend VMs (vm-web-01, vm-web-02, vm-hub-test) were deployed
with no public IP address. Access is exclusively through Azure Bastion.

**Reasoning:**
- No public IP = no attack surface on the VM directly
- Azure Bastion proxies RDP/SSH over HTTPS port 443 through the browser — no
  inbound RDP/SSH port needs to be open
- Demonstrates zero-trust access pattern that aligns with enterprise security
  requirements and regulatory compliance frameworks
- Consistent with the NSG rule that denies RDP from Internet

---

### Decision 04 — Service tags over IP ranges in all NSG rules

**Choice:** All NSG rules use Azure service tags (`AzureLoadBalancer`,
`VirtualNetwork`, `Internet`) rather than explicit IP address ranges.

**Reasoning:**
- Service tags are maintained by Microsoft and automatically updated when
  Azure infrastructure IP ranges change
- Hard-coded IP ranges break when Azure updates infrastructure — which happens
  regularly without notice
- Service tags are more readable and self-documenting than IP ranges
- This is the AZ-104 exam best practice and the real-world operational standard

---

### Decision 05 — Separate frontend IP configs for inbound and outbound LB traffic

**Choice:** Created two frontend IP configurations on lb-web: `fe-web` for
inbound traffic (pip-lb-web) and `fe-outbound` for outbound SNAT (pip-lb-outbound).

**Reasoning:**
- Separating inbound and outbound public IPs allows independent management —
  the inbound IP can be changed without affecting outbound SNAT and vice versa
- Clearer operational visibility in monitoring and logging
- Best practice for production Standard LB deployments
- Required by Azure — outbound rules cannot share the same frontend IP config
  as inbound rules in most configurations

---

### Decision 06 — LRS for primary storage, GRS demonstration only

**Choice:** Primary storage account `stlabeastus001` uses LRS. A separate
`stlabgrs001` account was created with GRS solely to demonstrate geo-replication,
then deleted after screenshots.

**Reasoning:**
- LRS is sufficient for lab data with no durability requirements
- GRS costs approximately double LRS with no lab benefit beyond the screenshot
- Creating a separate account to demonstrate GRS (and deleting it promptly)
  shows cost awareness — a skill employers value
- In production, the choice between LRS, ZRS, GRS depends on RTO/RPO
  requirements and cost budgets

---

### Decision 07 — Policy-linked SAS over ad-hoc SAS for production pattern

**Choice:** Both SAS token types were configured but the portfolio write-up
emphasises stored access policy SAS as the production-appropriate pattern.

**Reasoning:**
- Ad-hoc SAS tokens cannot be revoked before expiry — if a token is
  compromised, the only remediation is rotating the storage account key,
  which invalidates all tokens and disrupts all applications
- Policy-linked SAS tokens can be revoked instantly by deleting the policy
- The "ad-hoc SAS = cash (irrecoverable), policy SAS = credit card (can be
  cancelled)" analogy captures the operational difference clearly

---

### Decision 08 — Disable public storage access after private endpoint confirmed

**Choice:** Storage public access was left enabled during private endpoint
setup, then disabled only after nslookup confirmed private IP resolution was
working, then re-enabled before teardown.

**Reasoning:**
- Disabling public access before confirming the private path works risks
  locking yourself out with no recovery path except re-enabling from the portal
- The confirm-then-lockdown sequence is the correct production procedure:
  1. Deploy private endpoint
  2. Verify private connectivity from inside the VNet
  3. Disable public access
  4. Verify public access is blocked (404/403)
- Re-enabling before teardown is a hard dependency — CLI delete commands
  from Cloud Shell cannot reach the storage account otherwise

---

### Decision 09 — Bash as primary CLI with PowerShell equivalents documented

**Choice:** Bash (Linux line continuation with `\`) used as the primary shell
for all scripts. PowerShell equivalents (backtick `` ` `` continuation) documented
alongside for all commands.

**Reasoning:**
- Azure Cloud Shell defaults to Bash; most Azure documentation uses Bash syntax
- AZ-104 exam tests both Bash and PowerShell `az` CLI syntax
- Variable capture syntax differs significantly (`$()` vs `$var = ...`) and
  is worth learning side by side
- `az` CLI commands are identical in both shells — only the shell syntax
  (line continuation, variable assignment, loops) differs

---

## 4. Resource Inventory

> All resources below were deployed in East US region unless noted.
> All resources were torn down after Phase 2 completion.

### Resource Group: `rg-phase2-network`

| Resource Name | Type | Key Properties |
|---|---|---|
| `vnet-hub` | Virtual Network | 10.0.0.0/16 · East US |
| `snet-shared` | Subnet (in vnet-hub) | 10.0.1.0/24 |
| `AzureBastionSubnet` | Subnet (in vnet-hub) | 10.0.2.0/26 · exact name required |
| `vnet-spoke` | Virtual Network | 10.1.0.0/16 · East US |
| `snet-web` | Subnet (in vnet-spoke) | 10.1.1.0/24 · nsg-web associated |
| `snet-db` | Subnet (in vnet-spoke) | 10.1.2.0/24 · nsg-db associated |
| `hub-to-spoke` | VNet Peering | vnet-hub → vnet-spoke · allowForwardedTraffic: true |
| `spoke-to-hub` | VNet Peering | vnet-spoke → vnet-hub · allowForwardedTraffic: true |
| `nsg-web` | NSG | 5 rules: allow 80, 443, AzureLoadBalancer, VirtualNetwork, deny RDP Internet |
| `nsg-db` | NSG | allow SQL from web subnet only, allow VirtualNetwork, deny Internet |
| `vm-hub-test` | Virtual Machine | Ubuntu 22.04 · B1s · 10.0.1.4 · snet-shared · no public IP |
| `privatelink.blob.core.windows.net` | Private DNS Zone | linked to vnet-hub (auto-reg) + vnet-spoke (resolve) |
| `dns-link-hub` | Private DNS VNet Link | zone → vnet-hub · registrationEnabled: true |
| `dns-link-spoke` | Private DNS VNet Link | zone → vnet-spoke · registrationEnabled: false |
| `pe-storage-blob` | Private Endpoint | → stlabeastus001 · blob sub-resource · NIC: 10.0.1.6 · snet-shared |
| `lab.ostebovik.net` | Public DNS Zone | A record: www→20.171.241.228 · CNAME: storage→stlabeastus001.blob... |
| Azure Bastion | Bastion Host | Basic SKU · AzureBastionSubnet · deleted same session |

---

### Resource Group: `rg-phase2-storage`

| Resource Name | Type | Key Properties |
|---|---|---|
| `stlabeastus001` | Storage Account | Standard_LRS · Hot · TLS1.2 · allowBlobPublicAccess: false |
| `uploads` | Blob Container | Private · 5 test blobs · soft delete 7 days |
| `archive` | Blob Container | Private · lifecycle policy demo |
| `$web` | Blob Container | Static website · index.html + 404.html |
| `stlabgrs001` | Storage Account | Standard_GRS · Cool · deleted after screenshots |
| `read-policy-30d` | Stored Access Policy | Read+List · 30 day expiry · on uploads container |
| Lifecycle policy | Management Policy | uploads/: Hot→Cool 30d→Archive 90d→Delete 365d · archive/: 7d→30d→180d |
| Static website endpoint | Feature | https://stlabeastus001.z13.web.core.windows.net |

---

### Resource Group: `rg-phase2-lb`

| Resource Name | Type | Key Properties |
|---|---|---|
| `vm-web-01` | Virtual Machine | Ubuntu 22.04 · B1s · 10.1.1.4 · snet-web · Fault domain 0 |
| `vm-web-02` | Virtual Machine | Ubuntu 22.04 · B1s · 10.1.1.5 · snet-web · Fault domain 1 |
| `avset-web` | Availability Set | 2 fault domains · 2 update domains · Aligned managed disks |
| `lb-web` | Load Balancer | Standard SKU · Public |
| `pip-lb-web` | Public IP | Static · Standard SKU · 20.171.241.228 · inbound frontend |
| `pip-lb-outbound` | Public IP | Static · Standard SKU · outbound SNAT only |
| `LoadBalancerFrontEnd` | LB Frontend IP Config | → pip-lb-web · inbound |
| `fe-outbound` | LB Frontend IP Config | → pip-lb-outbound · outbound SNAT |
| `be-web` | LB Backend Pool | vm-web-01 (10.1.1.4) + vm-web-02 (10.1.1.5) |
| `probe-http` | LB Health Probe | HTTP · port 80 · path / · 15s interval · threshold 2 |
| `rule-http` | LB Load Balancing Rule | TCP 80→80 · Default (round-robin) · probe-http |
| `outbound-snat` | LB Outbound Rule | fe-outbound → be-web · All protocol · 10000 ports |

---

## 5. File Inventory — Phase 2 Deliverables

| Filename | Type | Description |
|---|---|---|
| `project3-vnet-setup.sh` | Bash script | Full VNet, subnet, NSG, peering, VM deployment |
| `project3-network-topology.svg` | SVG diagram | Hub-spoke topology with NSG boundaries |
| `project4-storage.sh` | Bash script | Storage accounts, containers, SAS, lifecycle, static website |
| `project4-storage-architecture.svg` | SVG diagram | Storage architecture with tiers and access methods |
| `project5-lb-architecture.svg` | SVG diagram | LB topology with SNAT, probes, availability set |
| `project5-portfolio.html` | Portfolio page | Project 5 write-up for ostebovik.net |
| `project6-dns-private-endpoint.svg` | SVG diagram | Private endpoint and DNS architecture |
| `project6-portfolio.html` | Portfolio page | Project 6 write-up for ostebovik.net |
| `phase2-lessons-learned.html` | Portfolio page | All 14 gotchas + LB vs App Gateway comparison |
| `phase2-projects-index.html` | Portfolio index | Phase 2 landing page linking all projects |
| `phase2-teardown.ps1` | PowerShell script | Full teardown in correct dependency order |
| `az104-phase3-guide.html` | Standalone guide | Offline interactive guide for Phase 3 |
| `azure-rbac-hierarchy.svg` | SVG diagram | Phase 1 RBAC group→role→scope hierarchy |
| `project2-governance.html` | Portfolio page | Phase 1 Project 2 governance write-up |
| `phase1-cleanup.ps1` | PowerShell script | Phase 1 resource teardown |

---

## 6. Exam Topic Coverage — Phase 2

| AZ-104 Domain | Topics Covered | Confidence |
|---|---|---|
| Implement and manage virtual networking | VNets, subnets, NSGs, service tags, peering, Bastion, DNS, private endpoints | High |
| Implement and manage storage | Storage accounts, redundancy tiers, blob containers, SAS, lifecycle, soft delete | High |
| Deploy and manage Azure compute resources | VM deployment, availability sets, no-public-IP pattern | Medium |
| Monitor and maintain Azure resources | NSG effective rules, LB health monitoring | Medium |
| Manage Azure identities and governance | Covered in Phase 1 | Complete |

---

*Document compiled from full conversation history — ostebovik.net AZ-104 portfolio project*
*Phase 2 complete · Environment torn down · Ready for Phase 3*
