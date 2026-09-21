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

@description('Gerard\'s Entra object ID, from `az ad signed-in-user show --query id`.')
param adminPrincipalId string

// =============================================================================
// MODULE: Storage
// =============================================================================
module storage 'modules/storage.bicep' = {
  name: 'deploy-iip-storage'
  params: {
    storageAccountName: storageAccountName
    location: location
    tags: tags
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
  }
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
  }
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
