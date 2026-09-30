// =============================================================================
// IIP — user-assigned managed identities (M9)
//
// D2 (Gerard, Sep 16): user-assigned, not system-assigned. Bicep can create
// these and assign their roles BEFORE the Function app exists, and they
// survive the app being recreated. That ordering is the whole reason M9 comes
// before M11.
// =============================================================================

param location string
param tags object
param functionIdentityName string
param cicdIdentityName string
param signInIdentityName string

// The RBAC model requires a `purpose` tag on every new resource, because two
// resources of the same type are told apart by instance number alone.
resource functionIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: functionIdentityName
  location: location
  tags: union(tags, {
    purpose: 'function-runtime'
  })
}

resource cicdIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: cicdIdentityName
  location: location
  tags: union(tags, {
    purpose: 'github-deploy'
  })
}

// M11 pass 2 (2026-09-30), D-M11-2 (b), RBAC row 17. Built-in authentication
// presents this identity's token as a client assertion, through a federated
// credential on the IIP Results (dev) app registration (entra.bicep), so the
// sign-in has no client secret. It holds NO Azure role. Microsoft: assign it
// only to the one app that uses the registration. Any other resource holding it
// could sign in as the app.
resource signInIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: signInIdentityName
  location: location
  tags: union(tags, {
    purpose: 'easyauth-fic'
  })
}

output functionIdentityId string = functionIdentity.id
output functionIdentityPrincipalId string = functionIdentity.properties.principalId
output functionIdentityClientId string = functionIdentity.properties.clientId

output cicdIdentityId string = cicdIdentity.id
output cicdIdentityPrincipalId string = cicdIdentity.properties.principalId
output cicdIdentityClientId string = cicdIdentity.properties.clientId

output signInIdentityId string = signInIdentity.id
output signInIdentityPrincipalId string = signInIdentity.properties.principalId
output signInIdentityClientId string = signInIdentity.properties.clientId
