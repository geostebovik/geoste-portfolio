// =============================================================================
// IIP — alerts (M14 part 2). Written by Claude, 2026-10-12.
// Survey, prices and decisions: ../../m14-prep.md, "Part 2" (Gerard: 15-minute
// checks; the address comes from an environment variable, never the repo).
//
// ONE signal, chosen because it means "the app is broken" and nothing else:
// the Functions host's own log line when an upload has failed every try and is
// parked in the poison queue. A failed first try that a retry fixes is NOT an
// outage, so failed executions on their own would be the wrong trigger (on
// 2026-10-12, all 14 failed runs in 20 days were 7 deliberate tests, 2 tries
// each). A storage metric can't do this: QueueMessageCount has no per-queue
// dimension and is refreshed daily (Microsoft Learn).
// =============================================================================

param location string
param tags object

@description('CAF: ag-{workload}-{env}-{region}-{instance}.')
param actionGroupName string

@description('No CAF abbreviation exists for a log search alert rule, so the name is descriptive.')
param alertRuleName string

@description('Where alerts are emailed. Read from IIP_ALERT_EMAIL in dev.bicepparam, so it never enters the public repo.')
@minLength(6)
param alertEmail string

@description('The Log Analytics workspace the Function\'s telemetry lands in (workspace-based App Insights).')
param logAnalyticsId string

// "Who gets told, and how". Action groups are global resources.
resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: actionGroupName
  location: 'global'
  tags: union(tags, {
    purpose: 'alert-email'
  })
  properties: {
    groupShortName: 'IIP dev' // max 12 characters; shown in the email
    enabled: true
    emailReceivers: [
      {
        name: 'owner-email'
        emailAddress: alertEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

// Checks every 15 minutes ($0.50/month, retail price list, 2026-10-12) but
// looks back 30, so a log line that is ingested a few minutes late is still
// seen. Stateful (autoMitigate): one line fires one email, and the alert
// resolves itself once 30 minutes pass with no new line.
resource poisonAlert 'Microsoft.Insights/scheduledQueryRules@2023-12-01' = {
  name: alertRuleName
  location: location
  tags: union(tags, {
    purpose: 'alert-poison-queue'
  })
  kind: 'LogAlert'
  properties: {
    displayName: 'IIP: an upload was parked in the poison queue'
    description: 'An upload failed every try (maxDequeueCount 2) and was moved to upload-events-poison. Look in AppTraces around the alert time for the failing run.'
    severity: 2
    enabled: true
    scopes: [
      logAnalyticsId
    ]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT15M'
    overrideQueryTimeRange: 'PT30M'
    criteria: {
      allOf: [
        {
          // The exact line, seen 7 times in AppTraces (2026-09-25 and -29):
          // "Message has reached MaxDequeueCount of 2. Moving message to queue 'upload-events-poison'."
          query: 'AppTraces | where Message has "MaxDequeueCount" and Message contains "upload-events-poison"'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: {
            numberOfEvaluationPeriods: 1
            minFailingPeriodsToAlert: 1
          }
        }
      ]
    }
    autoMitigate: true
    actions: {
      actionGroups: [
        actionGroup.id
      ]
    }
  }
}

output actionGroupId string = actionGroup.id
output poisonAlertId string = poisonAlert.id
