// =============================================================================
// modules/frontdoor.bicep
// Azure Front Door Standard — custom domain, HTTPS, WAF, CDN
// =============================================================================

param frontDoorName string
param tags object
param customDomain string // ostebovik.net
param staticWebAppHostname string // *.azurestaticapps.net — the origin
param logAnalyticsWorkspaceId string

// --- WAF Policy --------------------------------------------------------------
resource wafPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2022-05-01' = {
  name: 'waf${replace(frontDoorName, '-', '')}' // WAF name: no hyphens allowed
  location: 'global'
  tags: tags
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
}

// --- Front Door Profile ------------------------------------------------------
resource frontDoor 'Microsoft.Cdn/profiles@2023-05-01' = {
  name: frontDoorName
  location: 'global'
  tags: tags
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
}

// --- Origin Group ------------------------------------------------------------
// Contains the Static Web App as the single origin
resource originGroup 'Microsoft.Cdn/profiles/originGroups@2023-05-01' = {
  parent: frontDoor
  name: 'og-portfolio'
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath: '/'
      probeRequestType: 'HEAD'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 100
    }
  }
}

// --- Origin ------------------------------------------------------------------
resource origin 'Microsoft.Cdn/profiles/originGroups/origins@2023-05-01' = {
  parent: originGroup
  name: 'origin-swa'
  properties: {
    hostName: staticWebAppHostname
    httpPort: 80
    httpsPort: 443
    originHostHeader: staticWebAppHostname
    priority: 1
    weight: 1000
    enabledState: 'Enabled'
  }
}

// --- Endpoint ----------------------------------------------------------------
resource endpoint 'Microsoft.Cdn/profiles/afdEndpoints@2023-05-01' = {
  parent: frontDoor
  name: 'ep-portfolio'
  location: 'global'
  properties: {
    enabledState: 'Enabled'
  }
}

// --- Route -------------------------------------------------------------------
// Routes all traffic from the endpoint to the origin group
resource route 'Microsoft.Cdn/profiles/afdEndpoints/routes@2023-05-01' = {
  parent: endpoint
  name: 'route-portfolio'
  properties: {
    originGroup: {
      id: originGroup.id
    }
    supportedProtocols: ['Https']
    patternsToMatch: ['/*']
    forwardingProtocol: 'HttpsOnly'
    linkToDefaultDomain: 'Enabled'
    httpsRedirect: 'Enabled'
  }
}

// --- Custom Domain -----------------------------------------------------------
// Requires DNS CNAME validation before it activates
// After deploy: add CNAME at registrar pointing ostebovik.net to endpoint hostname
resource customDomainResource 'Microsoft.Cdn/profiles/customDomains@2023-05-01' = {
  parent: frontDoor
  name: replace(customDomain, '.', '-') // Bicep resource name cannot contain dots
  properties: {
    hostName: customDomain
    tlsSettings: {
      certificateType: 'ManagedCertificate' // Azure manages TLS cert — free, auto-renewed
      minimumTlsVersion: 'TLS12'
    }
  }
}

// --- Diagnostic Settings -----------------------------------------------------
resource frontDoorDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diagset-afd-prod-wus3-01'
  scope: frontDoor
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        category: 'FrontDoorAccessLog'
        enabled: true
      }
      {
        category: 'FrontDoorWebApplicationFirewallLog'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// --- Outputs -----------------------------------------------------------------
output frontDoorEndpoint string = endpoint.properties.hostName
output frontDoorId string = frontDoor.id
output wafPolicyId string = wafPolicy.id
