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

// --- M11 (2026-09-24) ----------------------------------------------------------
param hostStorageAccountName string
param appInsightsName string
param functionAppName string
param uploadEventsQueueName string
param uploadEventsPoisonQueueName string

@description('Principal ID of id-iip-dev-wus-02 (CI/CD), from the identity module.')
param cicdIdentityPrincipalId string

@description('Principal ID of the SYSTEM-ASSIGNED identity on egst-iip-dev-wus-01.')
param systemTopicPrincipalId string

var roleIds = {
  foundryUser: '53ca6127-db72-4b80-b1b0-d745d6d5456d'
  storageBlobDataContributor: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
  storageBlobDataReader: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
  // Added 2026-09-24 for M11. Read from Microsoft Learn's built-in roles pages
  // and the Flex Consumption Bicep quickstart the same day, not from memory.
  storageBlobDataOwner: 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
  storageTableDataContributor: '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'
  monitoringMetricsPublisher: '3913510d-42f4-4e42-8a64-420c390055eb'
  websiteContributor: 'de139f84-1756-47ae-9be6-808fbbe84772'
  storageQueueDataReader: '19e7f393-937e-4f77-808e-94535e297925'
  storageQueueDataMessageProcessor: '8a0f0c08-91a1-4084-bc3d-661d67233fed'
  storageQueueDataMessageSender: 'c6a89b2d-59bc-44d0-9896-0f6e12d7b80a'
}

// --- Custom role: IIP Queue Trigger (dev) -- added 2026-09-25 ---------------
// Written by Claude. Decisions Gerard's, 2026-09-25: a custom role (option a),
// ending as ONE role that replaces row 15's two built-ins, reached in two
// stages so each test changes one thing.
//   STAGE 1 (this deploy): messages/write only, ALONGSIDE the built-ins.
//     Test proves messages/write fixes the retry.
//     [DEPLOYED m11-row15-stage1-20260925; PROVEN 2026-09-25 21:00Z: no 403,
//     retry about 100 s after the failure. It still 403'd 65 min after the
//     assignment was created. For stage 2: expand the role FIRST, confirm it's
//     effective, and only THEN delete the built-ins, or the trigger could lose
//     read/process for as long as propagation takes.]
//   STAGE 2 (next): expand THIS role in place (same GUID, so the assignment
//     doesn't move) to the union -- Reader's queues/read (Get Queue Metadata)
//     + messages/read + messages/process/action + messages/write. Remove the
//     built-ins from this file AND delete their assignments by hand
//     (Incremental mode never deletes). Test proves the role works alone.
//
// WHY IT EXISTS: row 15's documented minimum (Reader + Message Processor) can't
// call Update Message. Found by forcing failures for row 16: after try 1 failed,
// the host's Update Message (which applies host.json visibilityTimeout, 1 min)
// got 403 AuthorizationPermissionMismatch, and try 2 came 10 min later -- the
// visibility the message was retrieved with. The queue listener also renews
// visibility every 5 min during a run with the same call, so without this a run
// longer than ~10 min would reappear and could be processed twice.
//
// WHY ONLY THIS ACTION: Microsoft's permissions table maps Update Message to
// messages/write and nothing else. Honest cost: messages/write ALSO satisfies
// Put Message, so the Function can add messages to upload-events. No narrower
// action exists. Storage Queue Data Contributor (option b) would have added
// messages/delete plus ARM queues/delete and queues/write on top.
//
// assignableScopes = this resource group only.
resource queueTriggerRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(resourceGroup().id, 'iip-queue-trigger')
  properties: {
    roleName: 'IIP Queue Trigger (dev)'
    description: 'What the IIP Function queue trigger needs on upload-events. Stage 1 of 2 (2026-09-25): Update Message only, so the host can apply visibilityTimeout and renew visibility. rg-iip-dev-wus-01 only.'
    type: 'CustomRole'
    permissions: [
      {
        actions: []
        notActions: []
        dataActions: [
          'Microsoft.Storage/storageAccounts/queueServices/queues/messages/write'
        ]
        notDataActions: []
      }
    ]
    assignableScopes: [
      resourceGroup().id
    ]
  }
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

// =============================================================================
// M11 rows (2026-09-24, Claude). Rows 7, 8 and 12 were deferred from M9 because
// their scopes did not exist yet; rows 14-16 come from D-M11-1 (b).
// =============================================================================

resource hostStorage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: hostStorageAccountName
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: appInsightsName
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' existing = {
  name: functionAppName
}

resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-05-01' existing = {
  parent: storage
  name: 'default'
}

resource uploadEventsQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' existing = {
  parent: queueService
  name: uploadEventsQueueName
}

resource uploadEventsPoisonQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' existing = {
  parent: queueService
  name: uploadEventsPoisonQueueName
}

// --- Row 7: Function identity -> host storage --------------------------------
// Amended 2026-09-24: Microsoft's AzureWebJobsStorage minimum is Blob Data Owner,
// plus Table Data Contributor so the host can write diagnostic events. Storage
// Queue Data Contributor and Storage Account Contributor are NOT assigned: both
// were blob-trigger requirements, and D-M11-1 (b) has no blob trigger.
// VERIFY at first light: add Queue Data Contributor only if the host asks.
resource functionHostBlobOwner 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: hostStorage
  name: guid(hostStorage.id, functionIdentityPrincipalId, roleIds.storageBlobDataOwner)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageBlobDataOwner)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource functionHostTableContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: hostStorage
  name: guid(hostStorage.id, functionIdentityPrincipalId, roleIds.storageTableDataContributor)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageTableDataContributor)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 8: Function identity -> App Insights, Monitoring Metrics Publisher ---
resource functionAppInsightsPublisher 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: appInsights
  name: guid(appInsights.id, functionIdentityPrincipalId, roleIds.monitoringMetricsPublisher)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.monitoringMetricsPublisher)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 12: CI/CD identity -> Function app, Website Contributor -------------
// Used by M14's GitHub Actions deploy over OIDC. Assigned now because its scope
// exists now. It grants nothing until a federated credential trusts GitHub.
resource cicdWebsiteContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: functionApp
  name: guid(functionApp.id, cicdIdentityPrincipalId, roleIds.websiteContributor)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.websiteContributor)
    principalId: cicdIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 14: system topic (SYSTEM-assigned) -> stiipdevwus01, Message Sender --
// ACCOUNT scope, not queue scope. Changed 2026-09-24 (Gerard's decision) after
// the first deploy failed three times over ~20 minutes with "Managed Identity
// Authorization Error ... does not have authorization to deliver to the
// endpoint", while a queue-scoped Message Sender assignment for this exact
// principal existed (confirmed with `az role assignment list`). Leading
// explanation: Event Grid validates the identity at subscription CREATION
// against the destination's `resourceId`, which is the STORAGE ACCOUNT (the
// queue is only named in `queueName`). Microsoft Learn's steps for this setup
// say the role goes "on the storage account". CONFIRMED the same day: the
// redeploy with this account-scoped grant succeeded on its first attempt,
// and the orphaned queue-scoped grant was then deleted by hand. Cost:
// the topic can ADD messages to any queue on this account (today: our two);
// it cannot read or delete them.
resource topicQueueSender 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storage
  name: guid(storage.id, systemTopicPrincipalId, roleIds.storageQueueDataMessageSender)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageQueueDataMessageSender)
    principalId: systemTopicPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 15: Function identity -> upload-events, Reader + Message Processor --
// The queue trigger's documented minimum (Microsoft Learn, "Configure
// connections... Grant permissions to an identity"). Scoped to ONE queue.
// [2026-09-25: NOT enough. The minimum can't call Update Message. The custom
// role IIP Queue Trigger is assigned below; stage 2 retires these two.]
resource functionQueueReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: uploadEventsQueue
  name: guid(uploadEventsQueue.id, functionIdentityPrincipalId, roleIds.storageQueueDataReader)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageQueueDataReader)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

resource functionQueueProcessor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: uploadEventsQueue
  name: guid(uploadEventsQueue.id, functionIdentityPrincipalId, roleIds.storageQueueDataMessageProcessor)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageQueueDataMessageProcessor)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Row 15, custom role (2026-09-25): IIP Queue Trigger, stage 1. See its comment.
resource functionQueueTrigger 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: uploadEventsQueue
  name: guid(uploadEventsQueue.id, functionIdentityPrincipalId, queueTriggerRole.name)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', queueTriggerRole.name)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 16: Function identity -> upload-events-poison, Message Sender -------
// The runtime ADDS a message to <queue>-poison after maxDequeueCount failures,
// and row 15's roles cannot add. Microsoft's role table has no footnote for this.
// VERIFY by forcing failures once deployed.
resource functionPoisonSender 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: uploadEventsPoisonQueue
  name: guid(uploadEventsPoisonQueue.id, functionIdentityPrincipalId, roleIds.storageQueueDataMessageSender)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleIds.storageQueueDataMessageSender)
    principalId: functionIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// --- Row 13 (Gerard, Storage Blob Delegator): pre-existing, NOT declared, like
// row 3. Row 17 (id-iip-dev-wus-03) holds no Azure RBAC by design.
//
// Rows 10 and 11 are Entra ID app assignment and a Conditional Access test
// user -- not Azure RBAC at all, and not expressible here. Row 1 is Gerard's
// existing subscription Owner, a documented single-admin exception (D1).

output declaredAssignmentCount int = 13
