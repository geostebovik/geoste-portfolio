// =============================================================================
// IIP — private endpoints and their DNS (M12, stage 1)
// Written by Claude, 2026-10-09, to the design in m12-prep.md.
//
// D-M12-1: endpoints on stiipdevwus01's blob and queue only.
// D-M12-5: each endpoint is named after its target.
// D-M12-2: these are the BILLED parts (about $0.48 a day for both), built for
// an evidence window and then deleted by CLI. main.bicep deploys this module
// only while networkStage >= 1, so after the teardown a redeploy doesn't
// quietly recreate them.
//
// What each piece does:
// - the private DNS zone answers "stiipdevwus01.blob.core.windows.net" with
//   the endpoint's private IP, but only for clients inside a linked VNet;
// - the VNet link is what makes the zone visible to the VNet;
// - the endpoint's zone group writes the A record into the zone, and removes
//   it again if the endpoint is deleted.
// =============================================================================

param tags object
param location string

param vnetId string
param pepSubnetId string
param storageAccountId string
param storageAccountName string

@description('The storage services to give endpoints, e.g. [\'blob\', \'queue\'].')
param storageServices array

// --- Private DNS zones (location is always 'global') -----------------------------
// environment().suffixes.storage is 'core.windows.net' in Azure's public cloud.
resource zones 'Microsoft.Network/privateDnsZones@2024-06-01' = [for svc in storageServices: {
  name: 'privatelink.${svc}.${environment().suffixes.storage}'
  location: 'global'
  tags: union(tags, {
    purpose: 'private-dns-${svc}'
  })
}]

resource links 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = [for (svc, i) in storageServices: {
  parent: zones[i]
  name: 'link-${last(split(vnetId, '/'))}'
  location: 'global'
  tags: tags
  properties: {
    // Only the endpoint's zone group writes records here. VMs in the VNet
    // don't auto-register their names.
    registrationEnabled: false
    // Declared as found (stage 2 what-if, 2026-10-09: "- resolutionPolicy").
    // Writable; 'Default' means a name missing from the zone fails rather
    // than falling back to public DNS.
    resolutionPolicy: 'Default'
    virtualNetwork: {
      id: vnetId
    }
  }
}]

// --- Private endpoints ---------------------------------------------------------
resource endpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = [for svc in storageServices: {
  name: 'pep-${storageAccountName}-${svc}'
  location: location
  tags: union(tags, {
    purpose: 'storage-${svc}-private'
  })
  properties: {
    subnet: {
      id: pepSubnetId
    }
    // Named here because Azure's default is '<endpoint>.nic.<guid>', and the
    // name can't be changed after creation.
    customNetworkInterfaceName: 'nic-pep-${storageAccountName}-${svc}'
    privateLinkServiceConnections: [
      {
        name: 'pep-${storageAccountName}-${svc}'
        properties: {
          privateLinkServiceId: storageAccountId
          groupIds: [
            svc
          ]
        }
      }
    ]
  }
}]

resource zoneGroups 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = [for (svc, i) in storageServices: {
  parent: endpoints[i]
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: replace(zones[i].name, '.', '-')
        properties: {
          privateDnsZoneId: zones[i].id
        }
      }
    ]
  }
  dependsOn: [
    links[i]
  ]
}]

output endpointNames array = [for (svc, i) in storageServices: endpoints[i].name]
output zoneNames array = [for (svc, i) in storageServices: zones[i].name]
