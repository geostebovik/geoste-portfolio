// =============================================================================
// modules/keyvault.bicep
// Key Vault — RBAC model, audit logging to LAW
// =============================================================================

param keyVaultName string
param location string
param tags object
param kvAdminObjectId string          // Your Entra object ID — Secrets Officer
param logAnalyticsWorkspaceId string  // For diagnostic settings

// --- Key Vault ---------------------------------------------------------------
// RBAC authorization model — Access Policies are deprecated, never use them
// soft-delete and purge protection: required for production
// enabledForTemplateDeployment: allows Bicep to retrieve secrets during deploy
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true       // RBAC model — not Access Policies
    enableSoftDelete: true
    softDeleteRetentionInDays: 7        // Minimum — increase for production data
    enablePurgeProtection: true         // Cannot be disabled once enabled
    enabledForTemplateDeployment: true  // Required for Bicep getSecret()
    publicNetworkAccess: 'Enabled'      // Tighten with private endpoint later
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// --- RBAC: Key Vault Secrets Officer for admin (you) ------------------------
// Secrets Officer = full CRUD on secrets
// This is your admin access — separate from any managed identity assignments
// Role definition ID for Key Vault Secrets Officer is fixed across all tenants
resource kvAdminRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, kvAdminObjectId, 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'  // Key Vault Secrets Officer
    )
    principalId: kvAdminObjectId
    principalType: 'User'
  }
}

// --- Diagnostic Settings — send AuditEvent to LAW ---------------------------
resource kvDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diagset-kv-prod-wus3-01'
  scope: keyVault
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'AuditEvent'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// --- Outputs -----------------------------------------------------------------
output keyVaultName string = keyVault.name
output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri
