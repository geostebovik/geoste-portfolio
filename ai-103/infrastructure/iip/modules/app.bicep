// =============================================================================
// IIP -- the M11 app, pass 1: upload -> result
//
// Written by Claude, 2026-09-24. Nothing here is deployed until Gerard runs it.
// Pass 1 builds only what the upload -> agent -> result path needs. The sign-in
// half (app registration, built-in authentication, id-iip-dev-wus-03 and its
// federated credential, and the viewers group) is pass 2. Both halves are in
// M11's done-when.
//
// Shape and decisions: m11-prep.md; RBAC rows: phase2-rbac-model-draft.md
// (the role assignments themselves live in rbac.bicep, in row order).
//
//   stiipdevwus02         host storage (D3): AzureWebJobsStorage + the
//                         deployment package container. Shared keys OFF from
//                         birth -- a new account has no legacy key callers.
//   log-/appi-            telemetry, Entra-only ingestion (DisableLocalAuth)
//   asp- / func-          Flex Consumption, Python 3.14 (Gerard, Sep 24)
//   egst-                 system topic on stiipdevwus01, SYSTEM-assigned
//                         identity (row 14: M12's storage firewall only admits
//                         Event Grid delivery from a system-assigned identity)
//
// The event SUBSCRIPTION is not here. It lives in eventsub.bicep, deployed
// after rbac.bicep, because delivery needs row 14's role to exist first.
// =============================================================================

param location string
param tags object

param hostStorageAccountName string
param logAnalyticsName string
param appInsightsName string
param planName string
param functionAppName string
param systemTopicName string

param dataStorageAccountName string
param functionIdentityName string

@description('Non-secret settings the M7 code reads, same names as scripts/.env.')
param m7Settings object

@description('Flex ceiling on on-demand instances. Each instance runs ONE upload at a time (host.json batchSize 1).')
param maximumInstanceCount int

@description('Log Analytics daily ingestion cap in GB -- a cost guard, not a retention setting.')
param logDailyCapGb int

// host.json-independent names the code expects
var deploymentContainerName = 'app-package-${functionAppName}'
var uploadEventsQueueName = 'upload-events'

resource functionIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: functionIdentityName
}

resource dataStorage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: dataStorageAccountName
}

// --- Host storage (D3) --------------------------------------------------------
resource hostStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: hostStorageAccountName
  location: location
  tags: union(tags, { purpose: 'function-host' })
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
  resource blobService 'blobServices' = {
    name: 'default'
    resource deploymentContainer 'containers' = {
      name: deploymentContainerName
      properties: { publicAccess: 'None' }
    }
  }
}

// --- Telemetry ------------------------------------------------------------------
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    // Cost guard: a runaway loop stops ingesting at the cap rather than billing.
    workspaceCapping: { dailyQuotaGb: logDailyCapGb }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    // Entra-only ingestion (row 8, Monitoring Metrics Publisher). The Function
    // authenticates with APPLICATIONINSIGHTS_AUTHENTICATION_STRING below.
    DisableLocalAuth: true
  }
}

// --- Flex Consumption plan and the Function app --------------------------------
resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  tags: tags
  kind: 'functionapp'
  sku: {
    tier: 'FlexConsumption'
    name: 'FC1'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${functionIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
    }
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${hostStorage.properties.primaryEndpoints.blob}${deploymentContainerName}'
          authentication: {
            type: 'UserAssignedIdentity'
            userAssignedIdentityResourceId: functionIdentity.id
          }
        }
      }
      scaleAndConcurrency: {
        maximumInstanceCount: maximumInstanceCount
        instanceMemoryMB: 2048
      }
      runtime: {
        name: 'python'
        version: '3.14'
      }
    }
  }

  resource appSettings 'config' = {
    name: 'appsettings'
    properties: union({
      // Host storage, identity-based (row 7). No connection string exists.
      AzureWebJobsStorage__accountName: hostStorage.name
      AzureWebJobsStorage__credential: 'managedidentity'
      AzureWebJobsStorage__clientId: functionIdentity.properties.clientId

      // The queue trigger's connection, identity-based (rows 15, 16).
      UploadEvents__queueServiceUri: dataStorage.properties.primaryEndpoints.queue
      UploadEvents__credential: 'managedidentity'
      UploadEvents__clientId: functionIdentity.properties.clientId

      // DefaultAzureCredential in the M7 code: name the identity explicitly.
      // Pass 2 adds id-iip-dev-wus-03 to this app, and from then on an unnamed
      // user-assigned identity is ambiguous.
      AZURE_CLIENT_ID: functionIdentity.properties.clientId

      // Telemetry, Entra-authenticated (row 8).
      APPLICATIONINSIGHTS_CONNECTION_STRING: appInsights.properties.ConnectionString
      APPLICATIONINSIGHTS_AUTHENTICATION_STRING: 'ClientId=${functionIdentity.properties.clientId};Authorization=AAD'
    }, m7Settings)
  }
}

// --- Event Grid system topic on the APP DATA account ---------------------------
// Only one system topic may exist per source resource. If stiipdevwus01 already
// has one (for example, created by Defender for Storage), this create FAILS,
// and the template must reference that topic instead. Check before the first
// deploy -- see the M11 notes in README.md.
resource systemTopic 'Microsoft.EventGrid/systemTopics@2025-02-15' = {
  name: systemTopicName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    source: dataStorage.id
    topicType: 'Microsoft.Storage.StorageAccounts'
  }
}

output functionAppName string = functionApp.name
output functionAppId string = functionApp.id
output hostStorageAccountName string = hostStorage.name
output appInsightsName string = appInsights.name
output systemTopicName string = systemTopic.name
output systemTopicPrincipalId string = systemTopic.identity.principalId
output uploadEventsQueueName string = uploadEventsQueueName
