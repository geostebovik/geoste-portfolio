# M12 prep: networking (cost estimate, scope and design)

Written by Claude, 2026-10-09. Gerard made every decision below. The
plan is `phase2-orientation.md`'s M12 row; this file holds the working detail,
the way `m11-prep.md` did for M11.

## Decisions (Gerard, 2026-10-09)

| # | Question | Decision |
|---|---|---|
| D-M12-1 | Which private endpoints? | **Scope A: data storage only.** `stiipdevwus01`, blob + queue: everything the Function reads and writes for the app. **No endpoint on Key Vault:** it's empty on purpose (RBAC model, D7) and nothing reads it, so an endpoint would cost $7.80/month to protect nothing. **Host storage `stiipdevwus02` stays as it is.** |
| D-M12-2 | Keep them running? | **No: an evidence window, then delete.** Build, verify, take the evidence, then delete the endpoints and DNS zones and keep the Bicep, so it can be redeployed (for an interview demo, say). |
| D-M12-3 | Pricing calculator? | **The retail price list is enough.** The calculator uses the same prices. The done-when is amended to name the source actually used. |

## The estimate (Azure retail prices API, 2026-10-09)

| Item | Unit price | Scope A | Per month |
|---|---|---|---|
| Private endpoint | $0.01 / hour ($7.30 / month) | 2 (blob, queue) | $14.60 |
| Private DNS zone | $0.50 / zone / month | 2 (`privatelink.blob…`, `privatelink.queue…`) | $1.00 |
| Data through the endpoints | $0.01 / GB | a few MB | < $0.01 |
| DNS queries | $0.40 / million | negligible | < $0.01 |
| VNet, subnets, Flex VNet integration | free | — | $0 |
| **Total, running all month** | | | **$15.60** |
| **Total, a one-week evidence window** | | | **about $3.60** |

For comparison, the scopes not chosen: A + Key Vault $23.40/month; A + Key
Vault + host storage (blob, queue, table) $45.80/month. The last full billing
cycle (Aug 18 - Sep 17) was $69.16 of the ~$150 credit.

**Sources:** `prices.azure.com` retail API: "Virtual Network Private Link"
(Standard Private Endpoint $0.01/hour; data processed $0.01/GB, first tier)
and "Azure DNS" (Private Zone $0.50, first 25 zones; Private Queries $0.40 per
million). Microsoft Learn: service endpoints and VNet integration carry no
charge of their own.

## Open question that could change the cost: outbound internet

**CLOSED 2026-10-09 by stage 2's upload test: no NAT gateway needed.** The
analysis below is kept as written before the test.

**On Flex Consumption, all of the Function's outbound traffic goes through the
VNet once it's integrated** (Microsoft Learn, "Azure Functions networking
options": "For Flex Consumption, all traffic is already routed through the
virtual network"). That includes the calls to Foundry, Entra ID and
Application Insights, which stay on public endpoints in scope A.

**New VNets now default to private subnets** (no default outbound access; API
versions after 2026-03-31, and the portal already does it). For VMs, a private
subnet needs an explicit way out, usually a NAT gateway.

**Unverified:** whether that applies to Flex Consumption's platform-managed
gateways, or whether they keep their own way out. Learn doesn't say.
- **If it applies:** add a NAT gateway (about $33/month plus a public IP at about
  $3.65/month; Claude's figures from memory, not yet checked against the price
  list), or deliberately set the integration subnet's `defaultOutboundAccess`
  to true. Inside a one-week window, a NAT gateway is about $8.
- **How the build answers it for free:** right after VNet integration, run one
  regression upload. If the agent's Foundry calls still work, no NAT is needed.

## Design facts found while costing

*(Kept as found during step 1; the design section that follows settles each
one.)*

- **Two subnets.** The integration subnet (/27 minimum for one app, delegated to
  `Microsoft.App/environments`, no underscore in its name) can't hold private
  endpoints, so the endpoints get a subnet of their own.
- **Register `Microsoft.App`** in the subscription before integrating.
- **Event Grid still has to reach the queue** once `stiipdevwus01` has a
  network rule: only with the system topic's system-assigned identity (already
  in place since M11) and the trusted-services exception on. `storage.bicep`
  has `bypass: 'None'` today; it has to become `AzureServices`.
- **Gerard's own uploads and scripts** reach `stiipdevwus01` from the tower over
  the internet. The firewall has to keep admitting them (an IP rule for the
  home connection, with `publicNetworkAccess` left on), or turning on
  `defaultAction: Deny` breaks the upload step of the demo. The home
  connection's address can change, and its sign-ins show IPv6 addresses:
  check which address family the tower uses to reach storage before writing
  the rule.

## The design (M12 step 2, done 2026-10-09)

Claude drafted it; Gerard decided D-M12-4 to -7.

### 1. The storage firewall on `stiipdevwus01`

| Setting | Today | M12 | Why |
|---|---|---|---|
| `defaultAction` | Allow | **Deny** | A guest list instead of an open door. |
| `ipRules` | none | **Gerard's home IPv4** | His uploads, scripts and the portal's blob browser keep working from home. |
| `bypass` | None | **AzureServices** | Event Grid delivers to the queue only as a trusted service; Learn offers nothing narrower. |
| `publicNetworkAccess` | unset (on) | **Enabled, written out** | An IP rule needs the public endpoint; Deny makes it a guest list. |
| `resourceAccessRules` | (Defender's) | **still not declared** | Defender for Storage injects its own rule there (`storage.bicep`'s comment). |

This settles the two "flagged at provisioning" items for this account
(`IIP-revised-project-plan.md`): `defaultAction` Deny, `publicNetworkAccess`
Enabled, both on purpose.

- **IPv4, checked 2026-10-09:** `stiipdevwus01.blob.core.windows.net` has only
  an `A` record (IPv4), so the tower always reaches it over IPv4, whatever
  Entra's logs show (Entra has IPv6 endpoints; the tower prefers IPv6 where it
  exists). A home rule admits the whole household, not just the tower; that's
  acceptable because every request still needs an Entra sign-in and a data
  role.
- **D-M12-4 (Gerard): the home IP stays out of the public repo.** It lives in
  an untracked local file on the tower and reaches the deployment at deploy
  time. Implementation (Claude's plan for the build): `dev.bicepparam` reads it
  with `readEnvironmentVariable('IIP_HOME_IP')`, and the parameter has a
  minimum length, so a deploy without it **fails** instead of deploying Deny
  with no IP rule (which would lock Gerard out).
- **Known effects while it's on:** Cloud Shell can't reach this account (a
  different IP); M3's `--blob` path probably fails (Content Understanding
  fetches the blob from Microsoft's network through a signed link, and it's not
  clear "trusted services" covers that); if Cox changes the home address,
  uploads get a 403 until the rule is updated.

### 2. Names and address space

No VNets exist in the subscription (Gerard, 2026-10-09: the AZ-104 hub-spoke
was torn down after the exam).

| Item | Name | Address / setting |
|---|---|---|
| VNet | `vnet-iip-dev-wus-01` | `10.20.0.0/24` |
| Function subnet | `snet-func-iip-dev-wus-01` | `10.20.0.0/27`, delegated to `Microsoft.App/environments` |
| Endpoint subnet | `snet-pep-iip-dev-wus-01` | `10.20.0.32/27` |
| NSGs (**D-M12-6**, Gerard: one per subnet) | `nsg-func-iip-dev-wus-01`, `nsg-pep-iip-dev-wus-01` | Azure's default rules |
| Endpoints (**D-M12-5**, Gerard: named after the target) | `pep-stiipdevwus01-blob`, `pep-stiipdevwus01-queue` | in `snet-pep-…` |
| DNS zones (names fixed by Azure) | `privatelink.blob.core.windows.net`, `privatelink.queue.core.windows.net` | each linked to the VNet |

Also needed: register the `Microsoft.App` resource provider before stage 2.

### 3. Build order and verification

Three stages, so each change is tested alone.

| Stage | What's added | Test | What it proves |
|---|---|---|---|
| 1 | VNet, subnets, NSGs, DNS zones and links, the two endpoints | `what-if`; then the endpoints show "Approved" and each zone has an `A` record in `10.20.0.32/27` | The private path exists. No traffic changes yet. |
| 2 | The Function joins the VNet | One regression upload; the results page loads | **The NAT question.** If Foundry calls fail here, this is the cause and nothing else changed. |
| 3 | The firewall: Deny + home IP + AzureServices | (a) a regression upload from the tower; (b) the results page; (c) **negative control:** a blob list from Cloud Shell gets 403; (d) one M3 `--blob` run, recorded either way | With the account closed to everyone but home, a working Function can only be using the private endpoints. (c) proves it's closed. |

The cost clock starts at stage 1 (2 endpoints: about $0.48 a day).

### 4. Teardown at the end of the window

In Azure's default deployment mode, a template only adds and changes; setting
a condition to false doesn't delete anything. So:

1. **Bicep with the isolation switch off:** the firewall goes back exactly to
   today's values, and the Function leaves the VNet.
2. **CLI deletes:** the two endpoints, then the DNS zone links, then the zones.
3. **D-M12-7 (Gerard): keep the free skeleton.** The VNet, both subnets and
   both NSGs stay ($0), so a redeploy for a demo is only the endpoints, zones,
   integration and firewall (about 10 minutes).

## M12 step 3, the build: progress

Claude writes the Bicep and walks Gerard through it; Gerard runs every
what-if, deploy and test. Details and the what-if register:
`infrastructure/iip/README.md`, "M12".

| Stage | Status | Result |
|---|---|---|
| 1 | **DONE 2026-10-09** (`m12-stage1-20261009`) | What-if exactly as predicted (11 to create). Both endpoints Approved; zones hold `stiipdevwus01 → 10.20.0.36` (blob) and `→ 10.20.0.37` (queue); the tower still resolves the public `57.150.229.161`. **The evidence window and its cost started here.** |
| 2 | **DONE 2026-10-09** (`m12-stage2-20261009`) | First what-if found 2 writable properties the template had dropped (now declared) and 2 noise lines (registered). Upload test: a full, correct result in 42 s. **The open NAT question is closed: no NAT gateway is needed.** |
| 3 | **Next** (planned 2026-10-10) | The firewall, then tests (a)-(d) from "Build order and verification". |

**Stage 3, what Claude writes first:** `storage.bicep` gets the firewall values
behind `networkStage >= 3` (stages 0-2 keep today's exact values, so the
register doesn't move); `main.bicep` gets a `homeIpAddress` parameter with a
minimum length; `dev.bicepparam` reads it with
`readEnvironmentVariable('IIP_HOME_IP')`; a small untracked script on the
tower sets that variable, and `.gitignore` gets an entry for it. Then the
what-if: expected, one Modify on `stiipdevwus01`'s `networkAcls` and
`publicNetworkAccess`.
