// =============================================================================
// IIP dev environment parameters — rg-iip-dev-wus-01 (westus)
// Values read from the live resources on 2026-09-21, not from memory.
// =============================================================================

using './main.bicep'

param location = 'westus'

// The live tag set. NOTE: srch-iip-dev-wus-01 is currently missing
// 'managed-by' — the other four resources carry it. Applying this object
// uniformly is an intended M8 change, not drift to be suppressed.
param tags = {
  env: 'dev'
  'managed-by': 'bicep'
  owner: 'geoste'
  project: 'iip'
  region: 'wus'
}

param tenantId = 'e0249b00-7415-4be2-8e15-dec109294248'

param storageAccountName = 'stiipdevwus01'
param keyVaultName = 'kv-iip-dev-wus-01'
param searchServiceName = 'srch-iip-dev-wus-01'

// Documented CAF exception: the account name omits the 'iip' token.
// The custom subdomain does NOT — and the scripts depend on it.
param foundryAccountName = 'aif-dev-wus-01'
param foundryProjectName = 'proj-iip-dev-wus-01'
param foundryCustomSubDomainName = 'aif-iip-dev-wus-01'

// capacity is in units of 1,000 TPM: 300 = 300K TPM, 30 = 30K, 10 = 10K.
// gpt-5-4 and gpt-5-4-mini were raised to 300K in the portal; that raise is
// captured here, which is the point of M8.
param modelDeployments = [
  {
    name: 'gpt-5-4'
    skuName: 'GlobalStandard'
    capacity: 300
    modelName: 'gpt-5.4'
    modelVersion: '2026-03-05'
  }
  {
    name: 'gpt-5-4-mini'
    skuName: 'GlobalStandard'
    capacity: 300
    modelName: 'gpt-5.4-mini'
    modelVersion: '2026-03-17'
  }
  {
    name: 'gpt-5-2'
    skuName: 'GlobalStandard'
    capacity: 30
    modelName: 'gpt-5.2'
    modelVersion: '2025-12-11'
  }
  {
    name: 'text-embedding-3-small'
    skuName: 'GlobalStandard'
    capacity: 10
    modelName: 'text-embedding-3-small'
    modelVersion: '1'
  }
]
