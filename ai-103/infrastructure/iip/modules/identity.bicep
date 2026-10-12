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

@description('M14 (D-M14-2): the GitHub Actions token subject that id-iip-dev-wus-02 trusts, e.g. repo:owner/name:ref:refs/heads/main.')
param githubOidcSubject string

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

// M14 part 1 (2026-10-12, Claude; D-M14-2, Gerard). GitHub Actions signs in as
// this identity over OIDC: GitHub issues the workflow run a short-lived token,
// and Entra swaps it for an Azure token ONLY if issuer, subject and audience
// all match this credential exactly. No secret exists anywhere. The identity's
// only role is Website Contributor on the Function (M9, RBAC model), so a
// matching run can deploy the Function and do nothing else.
resource githubDeployCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: cicdIdentity
  name: 'fic-gh-geoste-portfolio-main'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: githubOidcSubject
    audiences: [
      'api://AzureADTokenExchange'
    ]
  }
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
