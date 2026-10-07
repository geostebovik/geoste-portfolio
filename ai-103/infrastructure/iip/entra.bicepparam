// =============================================================================
// IIP dev -- parameters for entra.bicep (M11 pass 2, sign-in). Claude, 2026-09-30.
// Display names are the ones the RBAC model fixed on Sep 16. Entra objects are
// outside CAF, so there's no type prefix: 'app-' would have implied an App
// Service resource that doesn't exist (phase2-rbac-model-draft.md, naming).
// uniqueName is the template's key for idempotent redeploys. It's immutable
// once created, so it's lowercase, hyphenated and carries no display text.
// =============================================================================

using './entra.bicep'

// Same value as dev.bicepparam's adminPrincipalId (read 2026-09-21). Duplicated
// on purpose: the two files deploy separately.
param adminPrincipalId = 'fdc0b6bb-4bcd-4aee-b8d9-7f7c9156ed59'

param functionAppName = 'func-iip-dev-wus-01'
param signInIdentityName = 'id-iip-dev-wus-03'

param appUniqueName = 'iip-results-dev'
param appDisplayName = 'IIP Results (dev)'

param viewersGroupUniqueName = 'iip-results-viewers-dev'
param viewersGroupDisplayName = 'IIP Results Viewers (dev)'
param viewersGroupMailNickname = 'iip-results-viewers-dev'

// RBAC row 11, the Conditional Access test user: a non-admin, created by CLI on
// 2026-09-30. Since 2026-10-07 the only member of the viewers group (row 10);
// its interim direct assignment (2026-09-30 to 2026-10-07) was deleted by CLI.
param caTestUserUpn = 'iip-ca-test@letter7.onmicrosoft.com'
