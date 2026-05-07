// =============================================================================
// ostebovik.net Portfolio Site — prod.bicepparam
// Production environment values. 
// Do NOT store secrets here — secrets go in Key Vault.
// =============================================================================

using './main.bicep'

// --- Environment -------------------------------------------------------------
// param environment = 'prod'
param location = 'westus3'
param swaLocation = 'westus2'

// --- Tags --------------------------------------------------------------------
// Applied to all resources via modules
param tags = {
  owner: 'geoste'
  env: 'prod'
  region: 'wus3'
  project: 'portfolio'
  'managed-by': 'bicep'
}

// --- Resource Names (CAF standard) ------------------------------------------
param staticWebAppName = 'swa-prod-wus3-01'
param storageAccountName = 'stgeostewus301' // must be globally unique, 3-24 chars, lowercase letters and numbers only
param keyVaultName = 'kv-geoste-prod-wus3-01'
param logAnalyticsName = 'law-prod-wus3-01'
param appInsightsName = 'appi-prod-wus3-01'
param frontDoorName = 'afd-prod-wus3-01'

// --- GitHub Integration ------------------------------------------------------
param githubRepoUrl = 'https://github.com/geostebovik/geoste-portfolio'
param githubBranch = 'main'

// --- Custom Domain -----------------------------------------------------------
param customDomain = 'ostebovik.net'

// --- Key Vault Admin ---------------------------------------------------------
// Your Entra ID object ID — grants you Secrets Officer role at deploy time
// Find it: az ad signed-in-user show --query id -o tsv
param kvAdminObjectId = 'fdc0b6bb-4bcd-4aee-b8d9-7f7c9156ed59'
