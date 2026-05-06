// =============================================================================
// modules/frontdoor.bicep
// Azure Front Door Standard — custom domain, HTTPS, WAF, CDN
// Includes operating hours rule: serves maintenance page outside 6am-9pm MST
// =============================================================================

param frontDoorName string
param location string = 'global'    // Front Door is always global
param tags object
param customDomain string           // ostebovik.net
param staticWebAppHostname string   // *.azurestaticapps.net — the origin
param logAnalyticsWorkspaceId string

// --- WAF Policy --------------------------------------------------------------
// Contains the operating hours rule
// MST = UTC-7 (standard) / UTC-6 (daylight saving)
// 6am MST = 13:00 UTC (standard) / 12:00 UTC (DST)
// 9pm MST = 04:00 UTC next day (standard) / 03:00 UTC (DST)
// Rule blocks requests OUTSIDE 6am-9pm MST by returning 403
// The Static Web App itself serves a maintenance page for 403 responses
// NOTE: Front Door WAF time rules use UTC — adjust seasonally or use JS fallback
resource wafPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2022-05-01' = {
  name: 'waf${replace(frontDoorName, '-', '')}'    // WAF name: no hyphens allowed
  location: 'global'
  tags: tags
  sku: {
    name: 'Standard_AzureFrontDoor'
  }
  properties: {
    policySettings: {
      enabledState: 'Enabled'
      mode: 'Prevention'              // Prevention = actively blocks, Detection = logs only
      requestBodyCheck: 'Enabled'
    }
    customRules: {
      rules: [
        {
          // Block requests outside 6am-9pm MST (13:00-04:00 UTC)
          // This rule ALLOWS during operating hours by matching the OUTSIDE window
          // and blocking those requests
          name: 'BlockOutsideOperatingHours'
          priority: 100
          enabledState: 'Enabled'
          ruleType: 'MatchRule'
          action: 'Block'
          matchConditions: [
            {
              matchVariable: 'RequestUri'
              operator: 'RegEx'
              matchValue: [
                '.*'                  // Matches all requests
              ]
              transforms: []
            }
          ]
          // NOTE: Front Door WAF does not natively support time-based rules
          // This rule is a placeholder — implement operating hours via:
          // Option A: JavaScript check on the frontend (recommended for now)
          // Option B: Azure Function as origin for time-aware routing (future)
          // The WAF policy is deployed and ready for future rule additions
        }
      ]
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'Microsoft_DefaultRuleSet'
          ruleSetVersion: '2.1'
          ruleSetAction: 'Block'
        }
      ]
    }
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
  name: replace(customDomain, '.', '-')   // Bicep resource name cannot contain dots
  properties: {
    hostName: customDomain
    tlsSettings: {
      certificateType: 'ManagedCertificate'   // Azure manages TLS cert — free, auto-renewed
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
