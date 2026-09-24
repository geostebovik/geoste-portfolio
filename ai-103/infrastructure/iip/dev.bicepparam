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

// --- M9 ----------------------------------------------------------------------
// CAF: {abbreviation}-{workload}-{env}-{region}-{instance}. Both carry a
// `purpose` tag, because they differ only by instance number.
param functionIdentityName = 'id-iip-dev-wus-01'
param cicdIdentityName = 'id-iip-dev-wus-02'

// Gerard's Entra object ID, read from `az ad signed-in-user show` on 2026-09-21.
param adminPrincipalId = 'fdc0b6bb-4bcd-4aee-b8d9-7f7c9156ed59'

// --- M11, pass 1 (2026-09-24) --------------------------------------------------
// Names from phase2-rbac-model-draft.md's naming table (CAF, Sep 16).
param hostStorageAccountName = 'stiipdevwus02'
param logAnalyticsName = 'log-iip-dev-wus-01'
param appInsightsName = 'appi-iip-dev-wus-01'
param planName = 'asp-iip-dev-wus-01'
param functionAppName = 'func-iip-dev-wus-01'
param systemTopicName = 'egst-iip-dev-wus-01'

// Each instance runs one upload at a time (host.json batchSize 1), so this is
// also the cap on uploads processed at once: 2 x ~16K tokens is far inside
// gpt-5-4's 300K TPM, and it bounds a runaway to two concurrent agent runs.
param maximumInstanceCount = 2

// Cost guard on Log Analytics ingestion. At $2.99/GB (westus, Sep 24 retail),
// 1 GB/day caps a worst-case month at about $75 (30 GB less the 5 GB free).
// Still inside the $90 budget alert, which would fire first on anything worse.
// Expected use is well under the free 5 GB/month.
param logDailyCapGb = 1

// Copied from scripts/.env, where M10 measured them.
param chatApiVersion = '2024-06-01'
param pfWorkerCount = '2'

// capacity is in units of 1,000 TPM: 300 = 300K TPM, 30 = 30K, 10 = 10K.
// gpt-5-4 and gpt-5-4-mini were raised to 300K in the portal; that raise is
// captured here, which is the point of M8.
//
// versionUpgradeOption (Gerard, 2026-09-24): OnceCurrentVersionExpired on all
// four. The build moves only when Microsoft retires the pinned version, never
// because a new default ships, and the deployment never stops working (which
// NoAutoUpgrade would do at retirement). gpt-5-4 is both drafter and judge, so
// a silent build change would split every longitudinal comparison in two. A
// forced move at retirement is still detectable: model_builds provenance
// records the build on every measured run since 2026-09-23. See README.md.
param modelDeployments = [
  {
    name: 'gpt-5-4'
    skuName: 'GlobalStandard'
    capacity: 300
    modelName: 'gpt-5.4'
    modelVersion: '2026-03-05'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
  {
    name: 'gpt-5-4-mini'
    skuName: 'GlobalStandard'
    capacity: 300
    modelName: 'gpt-5.4-mini'
    modelVersion: '2026-03-17'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
  {
    name: 'gpt-5-2'
    skuName: 'GlobalStandard'
    capacity: 30
    modelName: 'gpt-5.2'
    modelVersion: '2025-12-11'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
  {
    name: 'text-embedding-3-small'
    skuName: 'GlobalStandard'
    capacity: 10
    modelName: 'text-embedding-3-small'
    modelVersion: '1'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
]
