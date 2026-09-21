// =============================================================================
// IIP — AI Search (srch-iip-dev-wus-01)
// Baselined from the live resource on 2026-09-21.
//
// SKU is 'free' and the tier cannot be changed after creation: moving to
// basic or standard means delete and recreate the service. That is recoverable
// -- scripts/m5_index.py rebuilds the index from a tracked source document --
// but the free tier CANNOT take a private endpoint at all, which is the
// constraint that would actually bite if M12 ever wants Search behind one.
//
// NOT declared: properties.endpoint. The 2025-05-01 schema does not flag it
// ReadOnly, but a search endpoint is not choosable — it is always
// https://{serviceName}.search.windows.net. Treating that as a schema
// inaccuracy rather than a real setting, because asserting a derived URL as a
// literal is how a template acquires a value that silently goes wrong after a
// rename. This is reasoning, not a verified read; the first real deployment
// settles it, and the endpoint is recorded here so a change would be obvious.
// =============================================================================

param searchServiceName string
param location string
param tags object

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchServiceName
  location: location
  tags: tags
  sku: {
    name: 'free'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'Default'
    // computeType is writable and a genuine choice (Default vs confidential
    // compute), not a status field. Declared so what-if stops predicting
    // its removal.
    computeType: 'Default'
    publicNetworkAccess: 'enabled'
    semanticSearch: 'free'
    // disableLocalAuth is false on the live service (admin keys work).
    // M10 revisits this; it is stated rather than omitted because the
    // aadOrApiKey block below is only valid while local auth is enabled.
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    // encryptionWithCmk.enforcement is writable. Its sibling
    // encryptionComplianceStatus is read-only and stays undeclared.
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    // bypass is absent from 2023-11-01 but present and writable in
    // 2025-05-01, which is why this module moved to that version rather
    // than dropping the property. M12 revisits the value.
    networkRuleSet: {
      bypass: 'None'
      ipRules: []
    }
  }
}

output searchServiceName string = search.name
output searchServiceId string = search.id
