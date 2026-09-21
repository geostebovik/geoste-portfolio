// =============================================================================
// IIP — Storage Account (stiipdevwus01)
// Baselined from the live resource on 2026-09-21. Values are literal, not
// derived, so `what-if` has nothing unresolvable to compare against.
// =============================================================================

param storageAccountName string
param location string
param tags object

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    encryption: {
      keySource: 'Microsoft.Storage'
      services: {
        blob: {
          enabled: true
          keyType: 'Account'
        }
        file: {
          enabled: true
          keyType: 'Account'
        }
      }
    }
    // networkAcls.resourceAccessRules is deliberately NOT declared here.
    // Defender for Storage injects its own storageDataScanner rule into that
    // array. Declaring the array would make this template fight the security
    // provider on every deployment. M12 revisits defaultAction.
    networkAcls: {
      bypass: 'None'
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

// NOT declared: allowCrossTenantDelegationSas. It is false on the live
// account, which is the default, and the 2023-05-01 schema does not carry
// it. Omitted rather than chasing a newer API version for a default value.
//
// NOT declared, deliberately: allowSharedKeyAccess. It is unset on the live
// account (so: keys enabled). M10 is the milestone that sets it false; naming
// it here would make M8 predict a change it is not making.

output storageAccountName string = storage.name
output storageAccountId string = storage.id
