# M12 prep: networking (cost estimate and scope)

Written by Claude, 2026-10-09. Gerard made the three decisions below. The
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

## Still to decide (M12 step 2, the design)

1. The storage firewall: `defaultAction`, `bypass`, the IP rule (the two
   "flagged at provisioning" items get decided here).
2. Names and address space: VNet, the two subnets, the endpoints and the DNS
   zones (CAF: `vnet-iip-dev-wus-01`, `snet-…`, `pe-…`).
3. The verification plan: what "the private paths verified" means (DNS
   resolving to private IPs from inside the VNet, a regression upload, the
   results page).
4. The teardown: what's deleted at the end of the window, and in what order.
