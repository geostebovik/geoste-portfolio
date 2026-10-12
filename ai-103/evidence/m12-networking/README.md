# M12 evidence: the network state at stage 3 (captured 2026-10-12)

Written by Claude, 2026-10-12. Claude wrote the capture script; Gerard ran it.

**What this is:** a read-only record of M12's private network as it stood
at stage 3 (deployment `m12-stage3-20261010`), taken on the morning of the
teardown. The teardown deletes the private endpoints and DNS zones and opens
the storage firewall again, so after it, this folder and the Bicep are the
only record of the built state. The test results that prove the private
paths work are in `../../infrastructure/iip/README.md`, "M12", and
`../../m12-prep.md`.

## Files

| File | What it shows |
|---|---|
| `01-storage-firewall.json` | `stiipdevwus01`: `defaultAction` **Deny**, `bypass` **AzureServices**, **1** IP rule |
| `02-private-endpoints.json` | `pep-stiipdevwus01-blob` and `-queue`: both **Approved**, on `snet-pep-iip-dev-wus-01` |
| `03-dns-records-blob.json` | `stiipdevwus01.privatelink.blob.core.windows.net` → **10.20.0.36** |
| `03-dns-records-queue.json` | `stiipdevwus01.privatelink.queue.core.windows.net` → **10.20.0.37** |
| `04-dns-link-blob.json`, `04-dns-link-queue.json` | each zone linked to `vnet-iip-dev-wus-01` (no auto-registration), state **Completed** |
| `05-function-vnet.json` | `func-iip-dev-wus-01` integrated with `snet-func-iip-dev-wus-01` |
| `06-vnet.json` | `10.20.0.0/24`: the Function subnet `10.20.0.0/27` (delegated to `Microsoft.App/environments`) and the endpoint subnet `10.20.0.32/27`, each with its own NSG and `defaultOutboundAccess: false` |

## What was left out, on purpose

- **The home IP address.** The firewall's IP rules are *counted*, not listed
  (D-M12-4: the home IPv4 never goes into this public repo). The capture
  script's queries never read the address, so it never reached a file.
- **The subscription ID**, replaced with `<subscription-id>` in the resource
  IDs (9 places). It isn't a secret, but this keeps the repo's exposure where
  it was.

Otherwise the content is unchanged from what `az` returned, apart from line
endings (LF, per `.gitattributes`).

## One field that reads wrong but isn't

`05-function-vnet.json` shows `outboundVnetRouting` with **every flag
`false`**, `allTraffic` included. On an App Service or Premium plan that would
mean only private (RFC 1918) traffic enters the VNet. **Flex Consumption is
different:** Microsoft Learn's *Azure Functions networking options* says "For
Flex Consumption, all traffic is already routed through the virtual network,
and Route All isn't needed." The tests agree. With the firewall at Deny, the
Function still reached `stiipdevwus01` (through the private endpoints) while
Cloud Shell was refused.

That also makes an earlier result more interesting, though it doesn't
overturn it. If all of the Function's traffic enters a subnet with
`defaultOutboundAccess: false`, it still reached Foundry and Entra, which are
public endpoints, with no NAT gateway (2026-10-09, stage 2 upload test). The
result is measured. **The mechanism isn't known, and isn't claimed here.**

## How it was captured

`capture-m12-evidence.ps1` (kept outside the repo, in Gerard's working
folder): eight read-only `az ... show` / `list` calls (one per file) with `--query`
projections, run in PowerShell on the tower on 2026-10-12 at 09:07
Phoenix. For example:

```powershell
az storage account show -g rg-iip-dev-wus-01 -n stiipdevwus01 `
  --query "{publicNetworkAccess:publicNetworkAccess, defaultAction:networkRuleSet.defaultAction, bypass:networkRuleSet.bypass, ipRuleCount:length(networkRuleSet.ipRules)}" `
  -o json
```
