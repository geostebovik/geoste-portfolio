// =============================================================================
// IIP — Azure AI Foundry account, project, and model deployments
// Baselined from the live resources on 2026-09-21.
//
// TWO THINGS IN HERE ARE LOAD-BEARING. Read them before editing.
//
// 1. customSubDomainName is PINNED to 'aif-iip-dev-wus-01'.
//    The account resource is named aif-dev-wus-01 (the known CAF exception),
//    but its custom subdomain DOES carry the iip token. Every endpoint the
//    M3-M7 scripts call is built from the subdomain, not the resource name:
//      https://aif-iip-dev-wus-01.services.ai.azure.com/
//    If this value is ever left to default, ARM derives it from the account
//    name, the endpoint host changes, and every script in scripts/ breaks at
//    once with an auth or DNS error that looks nothing like its cause.
//
// 2. Model deployments are serialised with @batchSize(1).
//    Cognitive Services rejects concurrent writes to deployments on the same
//    account. Deployed in parallel they fail intermittently, which reads as a
//    flaky template rather than a documented constraint.
// =============================================================================

param foundryAccountName string
param foundryProjectName string
param location string
param tags object

@description('Custom subdomain for the account. Pinned — see note 1 above.')
param customSubDomainName string

@description('Model deployments, in the order they should be applied.')
param modelDeployments array

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: foundryAccountName
  location: location
  tags: tags
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: customSubDomainName
    allowProjectManagement: true
    publicNetworkAccess: 'Enabled'
    // defaultProject and associatedProjects are WRITABLE in the 2025-06-01
    // schema, not read-only. Omitting them let what-if predict their deletion,
    // and a deploy could have cleared them — detaching the project and
    // breaking any data-plane call made without an explicit project name.
    // They are plain strings, so no reference() and nothing for what-if to
    // choke on.
    //
    // CAVEAT: this names a project that this same template creates below. That
    // is correct for a BASELINE against resources that already exist, which is
    // what M8 is. On a genuinely empty resource group it would be a
    // chicken-and-egg, and the account would need deploying twice.
    defaultProject: foundryProjectName
    associatedProjects: [
      foundryProjectName
    ]
  }
}

// The project carries almost nothing writable: the 2025-06-01 schema marks
// endpoints, isDefault and provisioningState ReadOnly, and agentIdentity is
// provider-injected and absent from the schema entirely. Name, identity and
// tags are the whole managed surface.
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: foundryProjectName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

@batchSize(1)
resource deployments 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = [
  for d in modelDeployments: {
    parent: foundry
    name: d.name
    sku: {
      name: d.skuName
      capacity: d.capacity
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: d.modelName
        version: d.modelVersion
      }
      raiPolicyName: 'Microsoft.DefaultV2'
      // Chosen per deployment in dev.bicepparam, not hardcoded (Gerard,
      // 2026-09-24). Was a bare 'OnceNewDefaultVersionAvailable' inherited
      // from the portal default, which let the judge's build move within two
      // weeks of a new default with no commit, no what-if diff and no decision.
      versionUpgradeOption: d.versionUpgradeOption
      // currentCapacity is writable, not read-only, despite reading like a
      // status field. Held equal to sku.capacity so the two cannot drift.
      currentCapacity: d.capacity
    }
  }
]

// NOT declared, deliberately: disableLocalAuth. Unset on the live account,
// so keys still work. M10 owns that switch.
//
// NOT declarable at all: properties.armFeatures on the account (the RAI legal
// terms record) and kind / agentIdentity / internalId / isDefault / endpoints
// on the project. None appear as writable in the 2025-06-01 schema, so what-if
// reporting them as deleted is a false positive of the kind its own header
// warns about. Confirmed against the schema on 2026-09-21, not assumed.

output foundryAccountName string = foundry.name
output foundryAccountId string = foundry.id
output foundryEndpoint string = foundry.properties.endpoint
output foundryPrincipalId string = foundry.identity.principalId
output projectPrincipalId string = project.identity.principalId
