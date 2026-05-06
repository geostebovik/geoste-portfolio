// =============================================================================
// ostebovik.net Portfolio Site — main.bicep
// Orchestrates all modules. No resources created directly here.
// All environment-specific values come from prod.bicepparam.
// =============================================================================

targetScope = 'resourceGroup'

// --- Parameters --------------------------------------------------------------
param environment string
param location string = resourceGroup().location
param appName string
param tags object

// Resource names — passed in from param file, enforces CAF naming
param staticWebAppName string
param storageAccountName string
param keyVaultName string
param logAnalyticsName string
param appInsightsName string
param frontDoorName string

// GitHub integration for Static Web Apps CI/CD
param githubRepoUrl string
param githubBranch string

// Custom domain
param customDomain string

// Key Vault admin — your Entra object ID, set in param file
// Used to grant yourself Secrets Officer role at deploy time
param kvAdminObjectId string

// =============================================================================
// MODULE: Log Analytics
// Deployed first — App Insights and diagnostics depend on it
// =============================================================================
module monitoring 'modules/monitoring.bicep' = {
  name: 'deploy-monitoring'
  params: {
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    location: location
    tags: tags
  }
}

// =============================================================================
// MODULE: Key Vault
// Deployed second — other modules may need to store secrets here
// =============================================================================
module keyvault 'modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    keyVaultName: keyVaultName
    location: location
    tags: tags
    kvAdminObjectId: kvAdminObjectId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsId
  }
}

// =============================================================================
// MODULE: Storage Account
// Hosts images, diagrams, and screenshots for the portfolio site
// =============================================================================
module storage 'modules/storage.bicep' = {
  name: 'deploy-storage'
  params: {
    storageAccountName: storageAccountName
    location: location
    tags: tags
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsId
  }
}

// =============================================================================
// MODULE: Static Web App
// Serves the portfolio frontend, integrated with GitHub for CI/CD
// =============================================================================
module staticwebapp 'modules/staticwebapp.bicep' = {
  name: 'deploy-staticwebapp'
  params: {
    staticWebAppName: staticWebAppName
    location: location
    tags: tags
    githubRepoUrl: githubRepoUrl
    githubBranch: githubBranch
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    appInsightsInstrumentationKey: monitoring.outputs.appInsightsInstrumentationKey
  }
}

// =============================================================================
// MODULE: Front Door
// Custom domain, HTTPS, WAF, CDN, and operating hours rule
// Deployed last — depends on Static Web App origin
// =============================================================================
module frontdoor 'modules/frontdoor.bicep' = {
  name: 'deploy-frontdoor'
  params: {
    frontDoorName: frontDoorName
    location: location
    tags: tags
    customDomain: customDomain
    staticWebAppHostname: staticwebapp.outputs.defaultHostname
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsId
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================
output staticWebAppUrl string = staticwebapp.outputs.defaultHostname
output frontDoorEndpoint string = frontdoor.outputs.frontDoorEndpoint
output storageAccountName string = storage.outputs.storageAccountName
output keyVaultName string = keyvault.outputs.keyVaultName
output appInsightsConnectionString string = monitoring.outputs.appInsightsConnectionString
