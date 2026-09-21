// =============================================================================
// IIP — role assignments (M9)
//
// This file deliberately mirrors the RBAC model's "Role assignments" table, in
// row order, so M9's done-when ("the assignments match the RBAC table") is an
// audit of one file rather than a hunt across modules. Row numbers below refer
// to ai-103/phase2-rbac-model-draft.md.
//
// ROLE IDS, NOT ROLE NAMES. Microsoft Learn is explicit about this for the
// Foundry roles: "Because the Foundry RBAC roles were recently renamed, use the
// role definition ID (GUID) instead of the role name in your code to avoid
// issues during the rename rollout." Foundry User was Azure AI User; the ID did
// not change. All three IDs below were read from Microsoft Learn on 2026-09-21,
// not from memory.
//
// WHY A ROLE ASSIGNMENT'S NAME LOOKS ARBITRARY: Azure enforces uniqueness on
// the (principal, role, scope) triple, not on the name. guid() over exactly
// those three values makes each assignment idempotent -- redeploying produces
// the same name and no change. It also means an assignment that ALREADY exists
// under a different name cannot be declared here: the deploy fails with
// RoleAssignmentExists. See row 3.
// =============================================================================

param foundryAccountName string
param storageAccountName string
param uploadsContainerName string
param resultsContainerName string

@description('Gerard: fdc0b6bb-... Read from `az ad signed-in-user show`, not assumed.')
param adminPrincipalId string

@description('Principal ID of id-iip-dev-wus-01, from the identity module.')
param functionIdentityPrincipalId string

@description('Principal ID of the Foundry PROJECT system-assigned identity.')
param foundryProjectPrincipalId string

var roleIds = {
  foundryUser: '53ca6127-db72-4b80-b1b0-d745d6d5456d'
  storageBlobDataContributor: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
  storageBlobDataReader: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
}

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: foundryAccountName
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' existing = {
  parent: storage
  name: 'default'
}

resource uploads 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' existing = {
  parent: blobService
  name: uploadsContainerName
}

resource results 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' existing = {
  parent: blobService
  name: resultsContainerName
}

// --- Row 2: Gerard -> Foundry account, Foundry User -------------------------
// Keyless local development runs (DefaultAzureCredential).
// The model guessed this might already exist, created automatically with the
// project. It does NOT exist at account scope: `az role assignment list` on the
// account returned nothing on 2026-09-21. Microsoft Learn explains why -- the
// automatic assignment happens only when the resource is deployed from the
// portal or Foundry UI, "not when deploying Foundry from SDK or CLI".
//
// HOWEVER: Gerard holds Foundry User at SUBSCRIPTION scope, which inherits
// here. That is how m7_orchestrator.py authenticates keylessly today, and it
// means this assignment grants nothing new right now. It is declared anyway,
// deliberately (Gerard, Sep 21): the narrow grant belongs in IaC so that
// tightening the subscription later does not silently break local development.
// Removing the subscription-scope grant is a separate deliberate act, tracked
// in phase2-orientation.md's Phase 2 Backlog. Until then this is a knowingly
// redundant assignment, not an accident.
resource adminFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, adminPrincipalId, roleIds.foundryUser)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.foundryUser)
    principalId: adminPrincipalId
    principalType: 'User'
  }
}

// --- Row 3: Gerard -> storage, Storage Blob Data Contributor ---------------
// NOT DECLARED. It already exists at account scope, confirmed 2026-09-21.
// Declaring it would resolve to the same (principal, role, scope) triple under
// a name Azure has not seen, and the deploy would fail with
// RoleAssignmentExists partway through. Row 3 is satisfied; it is simply not
// satisfied BY THIS FILE, and the verification step records that.
//
// Also observed at that scope and not in the model: Gerard holds Storage Blob
// Delegator, which grants user-delegation SAS keys. Harmless, and left alone.

// --- Row 4: Function identity -> Foundry account, Foundry User -------------
// Runs the agent. Foundry Agent Consumer would cover calling the agent but not
// the tools' direct model calls (judge, image audit, Vision Read), which is why
// this is Foundry User. D5: scoped to the account, matching Microsoft's
// documented minimum assignments.
// VERIFY at M10/M11: that Foundry User covers Vision Read and the Evaluation SDK.
resource functionFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, functionIdentityPrincipalId, roleIds.foundryUser)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.foundryUser)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 5: Function identity -> uploads container, Blob Data Reader -------
// Reads the blob that triggered the run. Container-scoped Reader FIRST, per the
// model: the identity-based blob-trigger docs list Blob Data Owner + Queue Data
// Contributor on the trigger's connection account, which is much broader. Widen
// only if the trigger actually fails at M11, and record what was required.
resource functionUploadsReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: uploads
  name: guid(uploads.id, functionIdentityPrincipalId, roleIds.storageBlobDataReader)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageBlobDataReader)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 6: Function identity -> results container, Blob Data Contributor --
resource functionResultsContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: results
  name: guid(results.id, functionIdentityPrincipalId, roleIds.storageBlobDataContributor)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageBlobDataContributor)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 9: Foundry PROJECT identity -> Foundry account, Foundry User ------
// The model marked this "(automatic)". IT IS NOT, on this account -- see row 2.
// Microsoft Learn calls it one of the two "minimum role assignments to get
// started", so the project identity has been running without its documented
// minimum since July. M7 did not notice because its tools authenticate with
// account keys and the orchestrator runs as Gerard.
resource projectFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, foundryProjectPrincipalId, roleIds.foundryUser)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.foundryUser)
    principalId: foundryProjectPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Rows 7, 8, 12: DEFERRED ----------------------------------------------
// Not omissions. A role assignment needs its scope resource to exist, and
// these three point at resources M11 creates:
//   row 7  -> stiipdevwus02 (Function host storage)
//   row 8  -> appi-iip-dev-wus-01 (Application Insights)
//   row 12 -> func-iip-dev-wus-01 (the Function app)
// id-iip-dev-wus-02 is created in M9 so row 12 is a one-line addition later.
//
// Rows 10 and 11 are Entra ID app assignment and a Conditional Access test
// user -- not Azure RBAC at all, and not expressible here. Row 1 is Gerard's
// existing subscription Owner, a documented single-admin exception (D1).

output declaredAssignmentCount int = 5
