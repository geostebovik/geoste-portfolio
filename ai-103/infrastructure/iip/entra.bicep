// =============================================================================
// IIP dev -- the Entra objects for M11 pass 2, sign-in (Microsoft Graph Bicep)
//
// Written by Claude, 2026-09-30. Nothing here is deployed until Gerard runs it.
// Gerard's decision (2026-09-30): Entra objects in Graph Bicep, in THIS file,
// kept apart from main.bicep. The reason for the separate file: Graph resources
// get no what-if at all (Microsoft Graph Bicep limitations), so mixing them
// into main.bicep would put unanalysed resources inside the one deployment
// whose what-if is registered line by line (README.md). This file is verified
// by reading the objects back, not by what-if. See README.md, section
// "M11 pass 2 -- sign-in".
//
//   IIP Results (dev)          app registration; single tenant; one Web
//                              redirect URI on the Function's default host;
//                              implicit grant OFF; no client secret, ever
//     fic-id-iip-dev-wus-03    federated credential: trusts id-iip-dev-wus-03
//                              (D-M11-2 (b), RBAC row 17)
//   its service principal      the enterprise app; "Assignment required" = Yes
//                              (RBAC row 10's gate)
//   admin consent              openid, profile, email on Microsoft Graph, for
//                              all users. Needed because an app that requires
//                              assignment needs admin consent, even where
//                              user consent would otherwise be allowed
//   IIP Results Viewers (dev)  security group, no members yet (RBAC row 10)
//
// NOT here yet, on purpose:
//   - The app-role assignment (row 10). letter7 is assumed to be on Entra ID
//     Free, and assigning a GROUP to an app needs P1/P2. Gerard's decision
//     (2026-09-30): prove the gate with the CA test user assigned directly
//     (works on Free), then start the P2 trial and swap to the group as the
//     first step on trial day 1. Both land in this file when they happen.
//   - Built-in authentication on the Function, and attaching id-iip-dev-wus-03
//     to it. Those are ARM (Microsoft.Web/sites, authsettingsV2) and go in
//     main.bicep, where what-if covers them.
//
// Idempotency: Graph creates with POST, so each object carries a client-
// provided key (uniqueName for the app and group, appId for the service
// principal, name for the federated credential). Redeploying updates in place.
// =============================================================================

extension microsoftGraphV1

targetScope = 'resourceGroup'

@description('Gerard\'s Entra object ID. Declared owner of the app and the group, so ownership does not depend on who happens to run the deployment.')
param adminPrincipalId string

param functionAppName string
param signInIdentityName string

param appUniqueName string
param appDisplayName string
param viewersGroupUniqueName string
param viewersGroupDisplayName string
param viewersGroupMailNickname string

// --- Existing ARM resources this file reads from ------------------------------
resource functionApp 'Microsoft.Web/sites@2024-04-01' existing = {
  name: functionAppName
}

resource signInIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: signInIdentityName
}

// Microsoft Graph's own service principal in this tenant: the resource the
// consent grant below points at. Well-known appId, the same in every tenant.
resource msGraphSp 'Microsoft.Graph/servicePrincipals@v1.0' existing = {
  appId: '00000003-0000-0000-c000-000000000000'
}

// The issuer is this tenant's v2.0 endpoint, built from the environment, not
// typed. It's used twice: the federated credential's issuer below, and the
// openIdIssuer that built-in authentication will need in main.bicep.
var tenantIssuer = '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0'

// --- The app registration -----------------------------------------------------
resource resultsApp 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: appUniqueName
  displayName: appDisplayName
  signInAudience: 'AzureADMyOrg'
  owners: {
    relationships: [
      adminPrincipalId
    ]
  }
  web: {
    // Built-in authentication's callback on the Function's REAL default host,
    // read from the resource. Flex apps can get a host name with a random
    // suffix, so it isn't assumed to be <name>.azurewebsites.net.
    redirectUris: [
      'https://${functionApp.properties.defaultHostName}/.auth/login/aad/callback'
    ]
    // OFF on purpose. With a client assertion (the federated credential),
    // built-in authentication uses the authorization code flow. Implicit grant
    // is only its fallback when there is NO credential, so if the federated
    // credential is misconfigured, sign-in fails loudly instead of quietly
    // downgrading to the flow Microsoft doesn't recommend.
    implicitGrantSettings: {
      enableIdTokenIssuance: false
      enableAccessTokenIssuance: false
    }
  }
  // Declared so the portal's "API permissions" shows exactly what's consented.
  // Scope IDs are Microsoft Graph's published delegated-permission IDs.
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000'
      resourceAccess: [
        { id: '37f7f235-527c-4136-accd-4a02d197296e', type: 'Scope' } // openid
        { id: '14dad69e-099b-42c9-810b-d002981feec1', type: 'Scope' } // profile
        { id: '64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0', type: 'Scope' } // email
      ]
    }
  ]

  // RBAC row 17 / D-M11-2 (b): trust tokens that id-iip-dev-wus-03 gets from
  // this tenant. Subject = the identity's object (principal) ID; a mismatch
  // fails sign-in with AADSTS70021.
  resource signInFic 'federatedIdentityCredentials@v1.0' = {
    // Graph requires '{parent uniqueName}/{child name}' here, even though the
    // resource is nested (deploy error 2026-09-30 with a one-segment name).
    // The credential's own name is 'fic-id-iip-dev-wus-03': immutable once
    // created, URL-friendly, 120 characters at most.
    name: '${appUniqueName}/fic-${signInIdentityName}'
    description: 'Built-in authentication on ${functionAppName} signs in as this app using ${signInIdentityName}. No client secret.'
    issuer: tenantIssuer
    subject: signInIdentity.properties.principalId
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
}

// --- The enterprise app (service principal) -----------------------------------
resource resultsSp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: resultsApp.appId
  // RBAC row 10's gate: only assigned principals can sign in. Until the first
  // assignment exists, NOBODY can, Gerard included. That's the intended state.
  appRoleAssignmentRequired: true
  owners: {
    relationships: [
      adminPrincipalId
    ]
  }
}

// Tenant-wide admin consent for the three sign-in scopes, and nothing else.
// If the first sign-in fails with AADSTS65001 naming another scope (for
// example offline_access), add exactly that scope here and to
// requiredResourceAccess, and record why.
resource signInConsent 'Microsoft.Graph/oauth2PermissionGrants@v1.0' = {
  clientId: resultsSp.id
  consentType: 'AllPrincipals'
  resourceId: msGraphSp.id
  scope: 'openid profile email'
}

// --- The viewers group (RBAC row 10) -------------------------------------------
resource viewersGroup 'Microsoft.Graph/groups@v1.0' = {
  uniqueName: viewersGroupUniqueName
  displayName: viewersGroupDisplayName
  description: 'People who may sign in to the IIP results page (dev). Holds no Azure roles (RBAC model, principle 3).'
  securityEnabled: true
  mailEnabled: false
  mailNickname: viewersGroupMailNickname
  owners: {
    relationships: [
      adminPrincipalId
    ]
  }
}

// --- Outputs: main.bicep's built-in authentication step needs the first two ----
output resultsAppClientId string = resultsApp.appId
output tenantIssuer string = tenantIssuer
output resultsAppObjectId string = resultsApp.id
output resultsSpObjectId string = resultsSp.id
output viewersGroupObjectId string = viewersGroup.id
output redirectUri string = resultsApp.web.redirectUris[0]
