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

// --- M9: the two app containers -------------------------------------------
// Added so rows 5 and 6 of the RBAC model have a scope to be assigned at.
// `docs` already exists on this account (from M2-M5) and is deliberately NOT
// declared here -- it is not part of the Phase 2 app and this template does not
// own it.
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    // Declared to match live, NOT as a preference. The first M9 what-if showed
    // this being removed because the resource was declared with no properties
    // at all -- deleteRetentionPolicy is writable, so that is the same class of
    // real diff as defaultProject and currentCapacity were in M8, and the same
    // rule applies: a writable property left undeclared is one a deploy can
    // clear.
    //
    // enabled:false means BLOB SOFT DELETE IS OFF on the app data account.
    // That is the state as found, and M9 is not the milestone that changes it.
    // See the Phase 2 Backlog item on soft delete.
    deleteRetentionPolicy: {
      enabled: false
    }
  }
}

resource uploadsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'uploads'
  properties: {
    publicAccess: 'None'
  }
}

resource resultsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'results'
  properties: {
    publicAccess: 'None'
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
output uploadsContainerName string = uploadsContainer.name
output resultsContainerName string = resultsContainer.name
