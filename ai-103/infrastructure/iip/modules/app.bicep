// =============================================================================
// IIP -- the M11 app, pass 1: upload -> result
//
// Written by Claude, 2026-09-24. Nothing here is deployed until Gerard runs it.
// Pass 1 builds only what the upload -> agent -> result path needs. The sign-in
// half (app registration, built-in authentication, id-iip-dev-wus-03 and its
// federated credential, and the viewers group) is pass 2. Both halves are in
// M11's done-when.
//
// Pass 2, step C (Claude, 2026-09-30): this file now also attaches
// id-iip-dev-wus-03 to the Function and turns on built-in authentication
// (authsettingsV2). The Entra objects it points at live in entra.bicep.
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

// --- Pass 2, step C: sign-in ------------------------------------------------------
@description('id-iip-dev-wus-03 (RBAC row 17). Attached to the Function ONLY so built-in authentication can present it as a client assertion.')
param signInIdentityName string

@description('Application (client) ID of the IIP Results (dev) app registration. An entra.bicep output, passed as a parameter so this ARM deployment never references a Graph resource (what-if cannot analyse those).')
param resultsAppClientId string

@description('Non-secret settings the M7 code reads, same names as scripts/.env.')
param m7Settings object

@description('Flex ceiling on on-demand instances. Each instance runs ONE upload at a time (host.json batchSize 1).')
param maximumInstanceCount int

@description('Log Analytics daily ingestion cap in GB -- a cost guard, not a retention setting.')
param logDailyCapGb int

// --- M12, stage 2 (Claude, 2026-10-09) -------------------------------------------
@description('''The subnet the Function joins (M12 stage 2+), or empty to leave it
out of any VNet. Once joined, ALL of the Function's outbound traffic goes through
the VNet (Flex Consumption has no "route all" switch: it always does). Setting
this back to empty may not detach an app that's already joined; the M12
teardown uses `az functionapp vnet-integration remove` (m12-prep.md).''')
param virtualNetworkSubnetId string = ''

// host.json-independent names the code expects
var deploymentContainerName = 'app-package-${functionAppName}'
var uploadEventsQueueName = 'upload-events'

resource functionIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: functionIdentityName
}

resource dataStorage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: dataStorageAccountName
}

resource signInIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: signInIdentityName
}

// The same issuer the federated credential trusts (entra.bicep builds it the
// same way): this tenant's v2.0 endpoint, from the environment, not typed.
// Microsoft recommends the v2.0 issuer over the legacy sts.windows.net one that
// the portal's express setup still writes.
var tenantIssuer = '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0'

// Built-in authentication reads the client credential from the app setting
// NAMED here. This reserved name tells it the setting holds a managed
// identity's client ID, to be used as a federated client assertion, not a
// secret (Microsoft Learn, "Use a managed identity instead of a secret").
var ficSettingName = 'OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID'

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
    // Declared as found (2026-09-25): the first what-if after the M11 deploy
    // showed '- deleteRetentionPolicy' here. It's writable, the same class as
    // stiipdevwus01's fix (storage.bicep), so it's declared rather than accepted.
    // Soft delete is OFF on host storage, as found.
    properties: {
      deleteRetentionPolicy: {
        enabled: false
        allowPermanentDelete: false
      }
    }
    resource deploymentContainer 'containers' = {
      name: deploymentContainerName
      // Encryption-scope pair declared as found (2026-09-25), same reason and
      // same values as the uploads/results containers in storage.bicep.
      properties: {
        publicAccess: 'None'
        defaultEncryptionScope: '$account-encryption-key'
        denyEncryptionScopeOverride: false
      }
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
      // Pass 2, step C. From here on the app holds two user-assigned
      // identities, which is why every setting below names -01 explicitly
      // (AZURE_CLIENT_ID and the __clientId settings).
      '${signInIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: plan.id
    // M12 stage 2. null leaves the property out of the request entirely, so
    // stages 0-1 send exactly what M11 sent.
    virtualNetworkSubnetId: empty(virtualNetworkSubnetId) ? null : virtualNetworkSubnetId
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

      // Pass 2, step C: -03's CLIENT ID (not the app registration's). Built-in
      // authentication uses it to get a token for the federated credential.
      // Not a secret: a client ID proves nothing without the identity itself.
      '${ficSettingName}': signInIdentity.properties.clientId

      // Pass 2, the results page (results_page.py): where it reads result files,
      // with -01's identity (RBAC row 6). Read from the resource, not typed.
      RESULTS_BLOB_ENDPOINT: dataStorage.properties.primaryEndpoints.blob
    }, m7Settings)
  }

  // --- Pass 2, step C: built-in authentication (Easy Auth), V2 settings ----------
  resource authSettings 'config' = {
    name: 'authsettingsV2'
    // The setting it names must exist before sign-in is switched on.
    dependsOn: [
      appSettings
    ]
    properties: {
      platform: {
        enabled: true
      }
      globalValidation: {
        // Every HTTP request must be signed in. Non-HTTP triggers (the queue
        // trigger, process_upload) never pass through this layer.
        requireAuthentication: true
        unauthenticatedClientAction: 'RedirectToLoginPage'
        redirectToProvider: 'azureactivedirectory'
      }
      identityProviders: {
        azureActiveDirectory: {
          enabled: true
          registration: {
            clientId: resultsAppClientId
            clientSecretSettingName: ficSettingName
            openIdIssuer: tenantIssuer
          }
        }
      }
      login: {
        // Off: the results page reads blobs with the Function's OWN identity
        // (RBAC principle 3), so it never needs the viewer's tokens. Storing
        // them would keep credentials the app doesn't use.
        tokenStore: {
          enabled: false
        }
      }
      httpSettings: {
        requireHttps: true
      }
    }
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
