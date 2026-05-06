// =============================================================================
// modules/storage.bicep
// Storage Account — hosts portfolio images, diagrams, and screenshots
// =============================================================================

param storageAccountName string
param location string
param tags object
param logAnalyticsWorkspaceId string

// --- Storage Account ---------------------------------------------------------
// LRS — locally redundant, sufficient for static assets that live in GitHub too
// Standard_LRS is the lowest cost option — ~$0.018/GB/month
// allowBlobPublicAccess: true — required for Static Web App to read assets
// HTTPS only, TLS 1.2 minimum — non-negotiable even in portfolio environments
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: true       // Required for public asset serving
    allowSharedKeyAccess: true        // Needed for SAS token generation
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// --- Blob Service ------------------------------------------------------------
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7                         // Soft delete — recoverable for 7 days
    }
  }
}

// --- Containers --------------------------------------------------------------
// content/ — portfolio write-ups, diagrams, screenshots
// Structured to mirror your local az-104 folder layout:
// content/phase02/, content/phase03/, content/phase04/
// Public access level: blob — individual blobs readable, container listing blocked
resource contentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'content'
  properties: {
    publicAccess: 'Blob'              // Blob-level public read, no container listing
  }
}

// --- Diagnostic Settings -----------------------------------------------------
resource storageDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diagset-st-prod-wus3-01'
  scope: storageAccount
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    metrics: [
      {
        category: 'Transaction'
        enabled: true
      }
    ]
  }
}

// --- Outputs -----------------------------------------------------------------
output storageAccountName string = storageAccount.name
output storageAccountId string = storageAccount.id
output contentContainerUrl string = '${storageAccount.properties.primaryEndpoints.blob}content'
