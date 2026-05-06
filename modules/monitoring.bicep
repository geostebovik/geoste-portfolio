// =============================================================================
// modules/monitoring.bicep
// Log Analytics workspace + Application Insights
// Deployed first — all other modules send diagnostics here
// =============================================================================

param logAnalyticsName string
param appInsightsName string
param location string
param tags object

// --- Log Analytics Workspace -------------------------------------------------
// Retention set to 30 days — free tier is 31 days, beyond that costs ~$2.30/GB
// Increase retention if you want longer query history
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'   // Pay-per-GB — correct for low-volume portfolio site
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// --- Application Insights ----------------------------------------------------
// Captures page views, browser performance, and custom events
// WorkspaceResourceId links it to LAW — workspace-based is the current model
// Classic (non-workspace) App Insights is deprecated — do not use
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    RetentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// --- Outputs -----------------------------------------------------------------
output logAnalyticsId string = logAnalytics.id
output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId
output appInsightsId string = appInsights.id
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
