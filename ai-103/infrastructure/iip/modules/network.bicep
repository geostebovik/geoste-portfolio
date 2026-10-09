// =============================================================================
// IIP — the network skeleton (M12, stage 1)
// Written by Claude, 2026-10-09, to the design in m12-prep.md (Gerard's
// decisions D-M12-4 to -7).
//
// The VNet, its two subnets and their two NSGs. All of it is free, and per
// D-M12-7 it STAYS after the evidence window, so it is deployed
// unconditionally. The billed parts (private endpoints, DNS zones) are in
// privatelink.bicep, behind the networkStage switch.
//
// Subnets are declared INLINE in the VNet, not as child resources. A VNet
// redeployed with child-resource subnets tries to delete subnets it doesn't
// list, and fails while one is in use (the Function's, from stage 2 on).
// =============================================================================

param location string
param tags object

param vnetName string
param vnetAddressPrefix string

param funcSubnetName string
param funcSubnetPrefix string
param funcNsgName string

param pepSubnetName string
param pepSubnetPrefix string
param pepNsgName string

// --- NSGs (D-M12-6: one per subnet, Azure's default rules) --------------------
// securityRules is written out as empty so what-if compares it against the
// live value instead of treating it as unset.
resource funcNsg 'Microsoft.Network/networkSecurityGroups@2024-05-01' = {
  name: funcNsgName
  location: location
  tags: union(tags, {
    purpose: 'func-integration-subnet'
  })
  properties: {
    securityRules: []
  }
}

resource pepNsg 'Microsoft.Network/networkSecurityGroups@2024-05-01' = {
  name: pepNsgName
  location: location
  tags: union(tags, {
    purpose: 'private-endpoint-subnet'
  })
  properties: {
    securityRules: []
  }
}

// --- The VNet ------------------------------------------------------------------
resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  tags: union(tags, {
    purpose: 'private-networking'
  })
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    // Declared as found (stage 2 what-if, 2026-10-09: "- privateEndpointVNetPolicies").
    // Writable, so leaving it out would be a real diff, not noise.
    privateEndpointVNetPolicies: 'Disabled'
    subnets: [
      {
        // Flex Consumption integration subnet (Microsoft Learn): /27 minimum
        // for one app, delegated to Microsoft.App/environments, no other
        // endpoints in it, no underscore in its name.
        name: funcSubnetName
        properties: {
          addressPrefix: funcSubnetPrefix
          networkSecurityGroup: {
            id: funcNsg.id
          }
          delegations: [
            {
              name: 'flex-consumption'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
          // Private subnet: no implicit way out to the internet. This is the
          // default for new VNets on API versions after 2026-03-31; written
          // out here because this API version (2024-05-01) would otherwise
          // leave it null, which still allows it. Stage 2's regression upload
          // then tests the modern case: whether the Function can reach Foundry
          // without a NAT gateway (m12-prep.md, "Open question").
          defaultOutboundAccess: false
        }
      }
      {
        name: pepSubnetName
        properties: {
          addressPrefix: pepSubnetPrefix
          networkSecurityGroup: {
            id: pepNsg.id
          }
          // The default for new subnets, written out so what-if has a value
          // to compare. 'Disabled' means NSG rules don't filter traffic to the
          // endpoints themselves; with default rules only, that changes nothing.
          privateEndpointNetworkPolicies: 'Disabled'
          defaultOutboundAccess: false
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output funcSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, funcSubnetName)
output pepSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnet.name, pepSubnetName)
