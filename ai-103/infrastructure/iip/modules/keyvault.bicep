// =============================================================================
// IIP — Key Vault (kv-iip-dev-wus-01)
// Baselined from the live resource on 2026-09-21.
// =============================================================================

param keyVaultName string
param location string
param tags object
param tenantId string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    // RBAC, not access policies. accessPolicies is [] on the live vault and
    // must stay empty while enableRbacAuthorization is true.
    enableRbacAuthorization: true
    accessPolicies: []
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    publicNetworkAccess: 'Enabled'
  }
}

// NOT declared, deliberately: enablePurgeProtection. It is off on the live
// vault. Per this project's standing lesson, purge protection cannot be
// switched back off once enabled — so it stays an explicit decision, never a
// side effect of a baseline template.

output keyVaultName string = keyVault.name
output keyVaultId string = keyVault.id
