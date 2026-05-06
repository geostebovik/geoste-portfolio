// =============================================================================
// modules/staticwebapp.bicep
// Azure Static Web Apps — serves the portfolio frontend
// CI/CD integrated with GitHub — pushes to main auto-deploy
// =============================================================================

param staticWebAppName string
param location string
param tags object
param githubRepoUrl string
param githubBranch string
param appInsightsConnectionString string
param appInsightsInstrumentationKey string

// --- Static Web App ----------------------------------------------------------
// Standard SKU — required for custom domains and staging environments
// Free SKU does not support custom domains — do not use for production
// repositoryUrl + branch: GitHub Actions workflow auto-created on deploy
// appLocation: root of your repo where index.html or framework config lives
// outputLocation: build output folder — '.' means output is at root (no build step)
resource staticWebApp 'Microsoft.Web/staticSites@2023-01-01' = {
  name: staticWebAppName
  location: location
  tags: tags
  sku: {
    name: 'Standard'    // Required for custom domain support
    tier: 'Standard'
  }
  properties: {
    repositoryUrl: githubRepoUrl
    branch: githubBranch
    buildProperties: {
      appLocation: '/'          // Root of repo
      outputLocation: '.'       // No build step — static HTML/MD served directly
      skipGithubActionWorkflowGeneration: false  // Auto-generate GitHub Actions workflow
    }
    stagingEnvironmentPolicy: 'Enabled'   // Allows PR preview environments
  }
}

// --- App Settings ------------------------------------------------------------
// Application Insights wired in as environment variables
// These are available to any JavaScript running on the site
resource swaAppSettings 'Microsoft.Web/staticSites/config@2023-01-01' = {
  parent: staticWebApp
  name: 'appsettings'
  properties: {
    APPINSIGHTS_CONNECTION_STRING: appInsightsConnectionString
    APPINSIGHTS_INSTRUMENTATIONKEY: appInsightsInstrumentationKey
  }
}

// --- Outputs -----------------------------------------------------------------
// defaultHostname: the *.azurestaticapps.net URL — used by Front Door as origin
output defaultHostname string = staticWebApp.properties.defaultHostname
output staticWebAppId string = staticWebApp.id
output staticWebAppName string = staticWebApp.name
