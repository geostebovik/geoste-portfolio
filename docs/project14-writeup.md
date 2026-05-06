# Project 14 — Key Vault & Managed Identity
## Zero-Credential Architecture on Azure App Service

**Phase:** 4 · **Region:** West US 3 · **Environment:** Dev  
**Stack:** Azure App Service · Key Vault · Microsoft Entra ID · Log Analytics

---

## What I Built

I deployed a zero-credential architecture connecting an Azure App Service to Key Vault using system-assigned managed identity — no passwords, no API keys, no service principal secrets anywhere in code, configuration files, deployment scripts, or git history.

The architecture has three moving parts: an App Service that needs secrets to function, a Key Vault that holds those secrets, and a managed identity that acts as the trust bridge between them. The App Service proves who it is to Microsoft Entra ID, receives a scoped token, and uses that token to retrieve secrets from Key Vault at runtime. Nothing sensitive is ever stored outside the vault.

---

## Key Concepts

**Managed Identity vs. credentials**  
The traditional approach to application secrets is to generate a password or API key, store it somewhere the application can read it, and rotate it periodically. Every step in that process is a potential failure: the credential gets committed to git, stored in plaintext in an environment variable, or forgotten in a config file after rotation. Managed identity eliminates the credential entirely. Azure manages the identity lifecycle — when the App Service is deleted, the identity is deleted with it. There is nothing to rotate, nothing to leak, and nothing to accidentally expose.

**RBAC over Access Policies**  
Key Vault supports two authorization models. The legacy Access Policies model grants access at the vault level — a principal either has access to all secrets or none. The RBAC model grants access at any scope using standard Azure role assignments, and integrates with the same IAM tooling used everywhere else in Azure. I used the RBAC model exclusively. Access Policies are deprecated for new vaults and should not be used in new deployments.

I assigned the `Key Vault Secrets User` role to the App Service identity — read-only access to secret values, nothing else. The identity cannot list secrets, create new ones, modify existing ones, or delete anything. This is least-privilege applied correctly: the application gets exactly what it needs to function and no more.

**Key Vault References**  
Rather than retrieving secrets programmatically in application code, I configured Key Vault references directly in App Service settings. The reference syntax `@Microsoft.KeyVault(SecretUri=https://...)` is resolved by the App Service runtime before the value is surfaced to the application. The actual secret value never appears in the Azure portal, never appears in deployment logs, and never touches the application configuration layer. From the application's perspective, `DB_CONNECTION` and `API_KEY` are ordinary environment variables — the fact that they come from Key Vault is transparent.

**Security auditing**  
I enabled diagnostic settings on Key Vault to send `AuditEvent` logs to Log Analytics. Every secret read, write, and delete operation is logged with a timestamp, caller IP address, and operation result. This is queryable via KQL:

```kql
AzureDiagnostics
| where ResourceType == "VAULTS"
| where OperationName == "SecretGet"
| project TimeGenerated, CallerIPAddress, OperationName, ResultType
| order by TimeGenerated desc
```

In a production environment this query becomes the foundation for security alerts — a spike in `SecretGet` operations or an unexpected caller IP can trigger an incident response workflow automatically.

---

## Design Decisions

**System-assigned over user-assigned managed identity**  
I used a system-assigned managed identity because the identity lifecycle is tied directly to the App Service. When the resource is deleted, the identity is deleted with it — no orphaned identities accumulating in Entra ID. At production scale, user-assigned identity becomes the better choice when multiple services share the same identity or when the identity needs to exist before the resource that will use it (the AKS node pool pattern, for example).

**Scope RBAC assignment to Key Vault, not resource group**  
The role assignment scope is the Key Vault resource ID, not the resource group. Scoping to the resource group would grant the same role against every resource in the group — a violation of least privilege with no operational benefit. Every RBAC assignment should be scoped as narrowly as possible.

**RBAC model over Access Policies**  
Beyond the deprecation concern, the RBAC model integrates with Azure Policy, supports conditional access, and produces audit logs that are consistent with every other RBAC operation in the subscription. Access Policies produce a separate audit trail in a different format, which complicates security monitoring. Consistency in the authorization model is operationally valuable.

**Key Vault references over SDK retrieval**  
Configuring secrets as App Service references rather than retrieving them via SDK in application code means the application itself has no Key Vault dependency. If the application is replaced, redeployed, or refactored, the secret management pattern stays intact at the infrastructure layer. This is the correct separation of concerns: infrastructure manages secrets, application consumes environment variables.

---

## Lessons Learned

**Local Bash on Windows corrupts Key Vault reference strings.** The `@` symbol and parentheses in the `@Microsoft.KeyVault(...)` reference syntax are mishandled by Git Bash and WSL when passed as CLI flag values, even inside quotes. Commands involving these strings must be run from Azure Portal Cloud Shell. This also affected the `az monitor diagnostic-settings create` command when passing workspace resource IDs — Cloud Shell resolved both issues cleanly.

**App Service masks Key Vault reference values by design.** After setting Key Vault references via CLI, the `az webapp config appsettings set` output shows `"value": null` for each setting. This is expected — App Service deliberately hides the reference string itself for security. Verification happens in the portal under Settings → Environment variables, where correctly resolved references show a green checkmark and "Key vault" in the Source column.

**Diagnostic log categories are resource-type specific.** The `AuditEvent` category is specific to Key Vault. Other resource types expose different categories — App Service exposes `AppServiceHTTPLogs`, `AppServiceConsoleLogs`, and others. The correct way to find available categories for any resource is `az monitor diagnostic-settings categories list --resource $RESOURCE_ID`, which returns exactly what is valid for that specific resource type.

**`az monitor` command structure requires drilling down.** The Azure CLI organizes monitor commands as `az monitor log-analytics workspace show` — not `az monitor workspace show` or `az loganalytics show`. The correct path is always discoverable by running `az monitor --help`, reading the subgroup list, then drilling into `az monitor log-analytics --help` and so on. This pattern works for every Azure service.

---

## Architecture

The App Service holds no credentials. Its managed identity authenticates to Microsoft Entra ID, which issues a scoped token valid only for Key Vault operations. The App Service uses that token to resolve Key Vault references at startup — replacing the `@Microsoft.KeyVault(...)` syntax with actual secret values before surfacing them to the application as environment variables. Every resolution event is logged to Log Analytics as an `AuditEvent`, creating a complete audit trail of which identity accessed which secret and when.

---

*ostebovik.net · AZ-104 Phase 4 · Project 14*
