// =============================================================================
// IIP (AI-103) dev environment — main.bicep
// M8, the IaC baseline. Orchestrates modules; creates nothing directly.
// All values come from dev.bicepparam.
//
// This template describes rg-iip-dev-wus-01 AS IT ALREADY EXISTS, as of
// 2026-09-21. It is not a greenfield deployment. Its job is to make
// `az deployment group what-if` boring — see README.md for the diffs that are
// expected and why.
// =============================================================================

targetScope = 'resourceGroup'

// --- Parameters --------------------------------------------------------------
param location string = resourceGroup().location
param tags object
param tenantId string

// Resource names — CAF, except the Foundry account (documented exception)
param storageAccountName string
param keyVaultName string
param searchServiceName string
param foundryAccountName string
param foundryProjectName string
param foundryCustomSubDomainName string

param modelDeployments array

// --- M9 ----------------------------------------------------------------------
param functionIdentityName string
param cicdIdentityName string

@description('M11 pass 2: the sign-in identity (row 17). Created here; trusted by entra.bicep.')
param signInIdentityName string

@description('Gerard\'s Entra object ID, from `az ad signed-in-user show --query id`.')
param adminPrincipalId string

// --- M11, pass 1: upload -> result (2026-09-24) -------------------------------
param hostStorageAccountName string
param logAnalyticsName string
param appInsightsName string
param planName string
param functionAppName string
param systemTopicName string
param maximumInstanceCount int
param logDailyCapGb int

// --- M11, pass 2, step C: sign-in (2026-09-30) -----------------------------------
@description('Application (client) ID of IIP Results (dev), from entra.bicep\'s output resultsAppClientId.')
param resultsAppClientId string

@description('Same value as scripts/.env CHAT_API_VERSION -- the version M10 measured.')
param chatApiVersion string

@description('Same value as scripts/.env PF_WORKER_COUNT (caps evaluate() concurrency).')
param pfWorkerCount string

// --- M12: networking (2026-10-09; design and decisions in m12-prep.md) ---------
@description('''Which M12 stage is deployed. 0 = the free skeleton only (VNet,
subnets, NSGs): the state after the evidence window's teardown. 1 = plus the
private endpoints and DNS zones (billed). 2 = plus the Function joined to the
VNet. 3 = plus the storage firewall (written 2026-10-10).''')
@allowed([
  0
  1
  2
  3
])
param networkStage int

param vnetName string
param vnetAddressPrefix string
param funcSubnetName string
param funcSubnetPrefix string
param funcNsgName string
param pepSubnetName string
param pepSubnetPrefix string
param pepNsgName string

@description('The storage services on stiipdevwus01 that get private endpoints (D-M12-1).')
param privateStorageServices array

// M12 stage 3 (2026-10-10). Required at EVERY stage, by Gerard's choice: one
// rule, no placeholder value. dev.bicepparam reads it from IIP_HOME_IP with no
// default, so a what-if or deploy in a terminal where set-home-ip.ps1 hasn't
// run fails at compile time (BCP427) and nothing reaches Azure. The lengths
// reject an empty value (BCP333) and anything longer than an IPv4 address
// (an IPv6 address, say). The script checks the format itself.
@description('Gerard\'s home IPv4, from set-home-ip.ps1. Kept out of the public repo (D-M12-4). Used only at networkStage 3.')
@minLength(7)
@maxLength(15)
param homeIpAddress string

// The settings the M7 code reads, under the names scripts/.env uses. Endpoints
// are DERIVED from the pinned custom subdomain, never typed: that subdomain is
// the load-bearing name (README "Load-bearing lines").
var m7Settings = {
  AIF_ENDPOINT: 'https://${foundryCustomSubDomainName}.cognitiveservices.azure.com'
  AIF_PROJECT_ENDPOINT: 'https://${foundryCustomSubDomainName}.services.ai.azure.com/api/projects/${foundryProjectName}'
  AIF_ACCOUNT: foundryAccountName
  AIF_RESOURCE_GROUP: resourceGroup().name
  CHAT_DEPLOYMENT_GPT_5_4: 'gpt-5-4'
  CHAT_DEPLOYMENT_GPT_5_4_MINI: 'gpt-5-4-mini'
  CHAT_API_VERSION: chatApiVersion
  PF_WORKER_COUNT: pfWorkerCount
}

// =============================================================================
// MODULE: Storage
// =============================================================================
module storage 'modules/storage.bicep' = {
  name: 'deploy-iip-storage'
  params: {
    storageAccountName: storageAccountName
    location: location
    tags: tags
    // M12 stage 3: the firewall. Below stage 3 the module ignores the IP.
    firewallEnabled: networkStage >= 3
    homeIpAddress: homeIpAddress
  }
}

// =============================================================================
// MODULE: Key Vault
// =============================================================================
module keyvault 'modules/keyvault.bicep' = {
  name: 'deploy-iip-keyvault'
  params: {
    keyVaultName: keyVaultName
    location: location
    tags: tags
    tenantId: tenantId
  }
}

// =============================================================================
// MODULE: AI Search
// =============================================================================
module search 'modules/search.bicep' = {
  name: 'deploy-iip-search'
  params: {
    searchServiceName: searchServiceName
    location: location
    tags: tags
  }
}

// =============================================================================
// MODULE: Foundry account, project, and model deployments
// =============================================================================
module foundry 'modules/foundry.bicep' = {
  name: 'deploy-iip-foundry'
  params: {
    foundryAccountName: foundryAccountName
    foundryProjectName: foundryProjectName
    location: location
    tags: tags
    customSubDomainName: foundryCustomSubDomainName
    modelDeployments: modelDeployments
  }
}

// =============================================================================
// MODULE: Managed identities (M9)
// Created before the Function app exists, deliberately -- see D2.
// =============================================================================
module identity 'modules/identity.bicep' = {
  name: 'deploy-iip-identity'
  params: {
    location: location
    tags: tags
    functionIdentityName: functionIdentityName
    cicdIdentityName: cicdIdentityName
    signInIdentityName: signInIdentityName
  }
}

// =============================================================================
// MODULE: The app, pass 1 (M11) -- host storage, telemetry, plan, Function,
// Event Grid system topic. The event subscription waits for rbac (below).
// =============================================================================
module app 'modules/app.bicep' = {
  name: 'deploy-iip-app'
  params: {
    location: location
    tags: tags
    hostStorageAccountName: hostStorageAccountName
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    planName: planName
    functionAppName: functionAppName
    systemTopicName: systemTopicName
    dataStorageAccountName: storage.outputs.storageAccountName
    functionIdentityName: functionIdentityName
    signInIdentityName: signInIdentityName
    resultsAppClientId: resultsAppClientId
    m7Settings: m7Settings
    maximumInstanceCount: maximumInstanceCount
    logDailyCapGb: logDailyCapGb
    // M12 stage 2: join the Function to the VNet. resourceId(), not a module
    // output, for the same what-if reason as the private-link module.
    virtualNetworkSubnetId: networkStage >= 2 ? resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, funcSubnetName) : ''
  }
  dependsOn: [
    identity
    network
  ]
}

// =============================================================================
// MODULE: Role assignments (M9)
// Mirrors the RBAC model's table in row order. Depends on every scope it
// assigns at, so it runs last.
// =============================================================================
module rbac 'modules/rbac.bicep' = {
  name: 'deploy-iip-rbac'
  params: {
    foundryAccountName: foundryAccountName
    storageAccountName: storageAccountName
    uploadsContainerName: storage.outputs.uploadsContainerName
    resultsContainerName: storage.outputs.resultsContainerName
    adminPrincipalId: adminPrincipalId
    functionIdentityPrincipalId: identity.outputs.functionIdentityPrincipalId
    foundryProjectPrincipalId: foundry.outputs.projectPrincipalId
    // M11
    hostStorageAccountName: app.outputs.hostStorageAccountName
    appInsightsName: app.outputs.appInsightsName
    functionAppName: app.outputs.functionAppName
    uploadEventsQueueName: storage.outputs.uploadEventsQueueName
    uploadEventsPoisonQueueName: storage.outputs.uploadEventsPoisonQueueName
    cicdIdentityPrincipalId: identity.outputs.cicdIdentityPrincipalId
    systemTopicPrincipalId: app.outputs.systemTopicPrincipalId
  }
}

// =============================================================================
// MODULE: Event subscription (M11) -- AFTER rbac, because delivery needs row 14.
// =============================================================================
module eventsub 'modules/eventsub.bicep' = {
  name: 'deploy-iip-eventsub'
  params: {
    systemTopicName: app.outputs.systemTopicName
    dataStorageAccountName: storage.outputs.storageAccountName
    uploadEventsQueueName: storage.outputs.uploadEventsQueueName
    uploadsContainerName: storage.outputs.uploadsContainerName
  }
  dependsOn: [
    rbac
  ]
}

// =============================================================================
// MODULE: Network skeleton (M12) -- free, and stays after the window (D-M12-7)
// =============================================================================
module network 'modules/network.bicep' = {
  name: 'deploy-iip-network'
  params: {
    location: location
    tags: tags
    vnetName: vnetName
    vnetAddressPrefix: vnetAddressPrefix
    funcSubnetName: funcSubnetName
    funcSubnetPrefix: funcSubnetPrefix
    funcNsgName: funcNsgName
    pepSubnetName: pepSubnetName
    pepSubnetPrefix: pepSubnetPrefix
    pepNsgName: pepNsgName
  }
}

// =============================================================================
// MODULE: Private endpoints + DNS (M12) -- billed, so only from stage 1 on.
// At stage 0 this module is skipped. Skipping does NOT delete anything already
// deployed: the teardown deletes the endpoints and zones by CLI (m12-prep.md).
// =============================================================================
// The IDs are computed with resourceId() here rather than read from the
// network module's outputs. A module output is a runtime reference() to that
// module's deployment, and the network deployment doesn't exist yet on the
// first run, so what-if would mark everything downstream "Unsupported"
// (the same limitation as the role assignments in README's register).
module privatelink 'modules/privatelink.bicep' = if (networkStage >= 1) {
  name: 'deploy-iip-privatelink'
  params: {
    location: location
    tags: tags
    vnetId: resourceId('Microsoft.Network/virtualNetworks', vnetName)
    pepSubnetId: resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, pepSubnetName)
    storageAccountId: resourceId('Microsoft.Storage/storageAccounts', storageAccountName)
    storageAccountName: storageAccountName
    storageServices: privateStorageServices
  }
  dependsOn: [
    network
    storage
  ]
}

// =============================================================================
// OUTPUTS
// M9 consumes the two principal IDs when it writes the role assignments.
// =============================================================================
output storageAccountId string = storage.outputs.storageAccountId
output keyVaultId string = keyvault.outputs.keyVaultId
output searchServiceId string = search.outputs.searchServiceId
output foundryAccountId string = foundry.outputs.foundryAccountId
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output foundryPrincipalId string = foundry.outputs.foundryPrincipalId
output projectPrincipalId string = foundry.outputs.projectPrincipalId

// M9 — M11 consumes these when it builds the Function app and the OIDC federation
output functionIdentityId string = identity.outputs.functionIdentityId
output functionIdentityClientId string = identity.outputs.functionIdentityClientId
output cicdIdentityId string = identity.outputs.cicdIdentityId
output cicdIdentityClientId string = identity.outputs.cicdIdentityClientId
output signInIdentityPrincipalId string = identity.outputs.signInIdentityPrincipalId
output signInIdentityClientId string = identity.outputs.signInIdentityClientId

// M11
output functionAppName string = app.outputs.functionAppName
output systemTopicPrincipalId string = app.outputs.systemTopicPrincipalId

// M12 -- stage 2 attaches the Function to this subnet
output funcSubnetId string = resourceId('Microsoft.Network/virtualNetworks/subnets', vnetName, funcSubnetName)
