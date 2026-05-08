# Project 11 — Infrastructure as Code with Bicep
## AZ-104 Phase 4 · ostebovik.net

---

## Overview

Project 11 marks a significant shift in how I approach Azure deployments. After spending Phases 1 through 3 building infrastructure imperatively — telling Azure what to do, step by step, through CLI commands — I transitioned to Bicep, Microsoft's declarative Infrastructure as Code language. The difference is not just syntactic. It represents a fundamentally different way of thinking about infrastructure management.

---

## From Imperative to Declarative

In Phase 3, deploying a VM looked like this: run a command to create a resource group, run another to create a VNet, another for the subnet, another for the NSG, another for the VM itself. Each command is an instruction. If something fails midway, you have partial state and no clean way to know what exists and what doesn't.

Bicep inverts this entirely. Instead of telling Azure what to do, I describe what I want to exist:

```bicep
resource vm 'Microsoft.Compute/virtualMachines@2025-04-01' = {
  name: vmName
  location: azureRegion
  identity: { type: 'SystemAssigned' }
  properties: {
    hardwareProfile: { vmSize: vmSize }
    ...
  }
}
```

Azure reads this definition, compares it against the current state of the resource group, and determines what actions are needed. If the VM already exists and matches the definition, nothing happens. If it doesn't exist, it gets created. If it exists but has drifted from the definition, it gets corrected. This property — called idempotency — means I can run the same template ten times and get the same result every time. That's not true of a Bash script.

---

## Module Pattern — Reusable Infrastructure Components

The most valuable structural concept I implemented in this project is the Bicep module pattern. Rather than defining all resources in a single monolithic file, I separated them into purpose-specific modules:

```
main.bicep              ← orchestrator: parameters and module calls only
modules/
  storage.bicep         ← storage account resource
  vm-linux.bicep        ← Linux VM + NIC
  vm-win.bicep          ← Windows VM + NIC
dev.bicepparam          ← environment-specific values
```

`main.bicep` contains no resource definitions — it receives parameters, resolves existing infrastructure references, and calls modules. Each module is self-contained and reusable. The same `vm-linux.bicep` module could be called multiple times with different parameters to deploy multiple Linux VMs without duplicating any code.

This is the lego pattern in practice. The modules are the bricks. `main.bicep` is the assembly instructions. `dev.bicepparam` is the specification for this particular build.

---

## What-If — Safe Deployments by Default

Every deployment in this project was preceded by a what-if check:

```bash
az deployment group create \
  -g rg-az104-dev-wus3-01 \
  -f main.bicep \
  -p dev.bicepparam \
  --what-if
```

What-if produces a detailed preview of every change the deployment will make before touching anything:

```
+ Create   Microsoft.Compute/virtualMachines/vm-win-dev-wus3-01
~ Modify   Microsoft.Storage/storageAccounts/staz104devwus301
* Ignore   Microsoft.Network/virtualNetworks/vnet-az104-dev-wus3-01
```

The `+`, `~`, and `*` symbols show exactly what will be created, modified, or left alone. This is categorically different from running a CLI script and hoping for the best. In a production environment, what-if output would be reviewed and approved before any deployment proceeds — it's the IaC equivalent of a code review for infrastructure changes.

I ran what-if multiple times throughout this project, catching issues before they became failed deployments. It identified a storage account name conflict, a Windows computer name length violation, and NIC property mismatches — all without touching any live resources.

---

## Zero-Credential Deployments with Key Vault getSecret()

One of the most significant improvements in this project over previous phases is the complete elimination of credentials from deployment pipelines. In Phase 3, VM admin passwords appeared in scripts, environment variables, or were typed interactively. None of those approaches are acceptable in production.

In Project 11, sensitive values never touch a file or a terminal. They live in Azure Key Vault and are retrieved at deploy time using Bicep's `getSecret()` function in the parameters file:

```bicep
param adminPassword = getSecret(
  '343a8a7e-...', 
  'rg-az104-dev-wus3-01', 
  'kv-az104-dev-wus3-01', 
  'vm-admin-password'
)
param sshPublicKey = getSecret(
  '343a8a7e-...', 
  'rg-az104-dev-wus3-01', 
  'kv-az104-dev-wus3-01', 
  'vm-ssh-key'
)
```

ARM retrieves these secrets during deployment using its own service identity. The actual values never appear in deployment logs, portal outputs, or git history. The deployment output confirms this — parameters marked `@secure()` show only their Key Vault reference, never their value:

```json
"adminPassword": {
  "reference": {
    "keyVault": { "id": "...kv-az104-dev-wus3-01" },
    "secretName": "vm-admin-password"
  },
  "type": "SecureString"
}
```

This is the production-correct pattern for credential management in IaC deployments.

---

## Brownfield IaC — The Decompile Workflow

A realistic enterprise scenario I practiced in this project is brownfield IaC — converting existing infrastructure into managed code. Azure allows you to export any resource as an ARM JSON template from the portal. Bicep can then decompile that JSON into a Bicep file:

```bash
az bicep decompile --file vm-linux.json
```

The decompiled output is a starting point, not a finished product. The exported template captures the current state of a specific resource — hardcoded resource IDs, subscription IDs, specific IP addresses, and literal credential values. Using it directly would create a brittle snapshot, not a reusable template.

The value of the decompile workflow is as a reference. I used the output to understand the correct ARM resource schema — what properties exist, what their valid values are, what the API version expects — then wrote clean modules informed by that knowledge. The decompiled files taught me the `windowsConfiguration.patchSettings` structure for Windows Server 2025 Azure Edition that I wouldn't have known to include otherwise.

---

## Lessons Learned

**Windows computer name — 15 character limit.** The Azure resource name for a VM can be longer, but the Windows OS-level computer name has a hard 15-character maximum. `vm-win-dev-wus3-01` is 18 characters and fails at provisioning time. The solution is to pass `computerName` as an explicit parameter separate from `vmName`, allowing the caller to control both independently:

```bicep
// In main.bicep
params: {
  vmName: 'vm-win-dev-wus3-01'     // Azure resource name (18 chars, fine)
  computerName: 'win-dev-01'        // Windows hostname (10 chars, fine)
}
```

**Bicepparam string interpolation limitations.** Native Bicep parameter files (`.bicepparam`) do not support referencing other parameters within the same file. This means you cannot build a tag value like `env: env` by referencing the `env` parameter — you must use literal values. This creates some duplication between the `param env = 'dev'` declaration and `env: 'dev'` in the tags object, but it's an intentional constraint of the format.

**Windows Server 2025 Azure Edition — hotpatch requirements.** The Azure Edition image is a Hotpatch-compatible image that requires specific patch settings. Using `patchMode: 'AutomaticByOS'` fails. The correct configuration is:

```bicep
patchSettings: {
  patchMode: 'AutomaticByPlatform'
  assessmentMode: 'AutomaticByPlatform'
  enableHotpatching: true
  automaticByPlatformSettings: {
    rebootSetting: 'IfRequired'
  }
}
```

Hotpatching allows security patches to be applied without rebooting by patching in-memory — a meaningful operational improvement for production workloads.

**Key Vault RBAC for ARM deployments.** When using `getSecret()` in a parameters file, it is ARM — not the deploying user — that retrieves the secret. ARM requires its own access to the vault, configured by enabling template deployment access on the vault:

```bash
az keyvault update \
  --name kv-az104-dev-wus3-01 \
  --enabled-for-template-deployment true
```

This is separate from the role assignment needed for the deploying user to write secrets.

---

## Repository Structure

```
Phase04/11_Bicep_Fundamentals/
  main.bicep              Orchestrator — parameters and module calls
  dev.bicepparam          Dev environment values + Key Vault references
  Modules/
    storage.bicep         Storage account — written from scratch
    vm-linux.bicep        Linux VM + NIC — decompiled and rebuilt
    vm-win.bicep          Windows VM + NIC — decompiled and rebuilt
  Screenshots/
    bicep-visualizer.png  VS Code module dependency graph
```

---

## Result

A complete, modular Bicep deployment producing two VMs (Windows Server 2025 Azure Edition and Ubuntu 24.04 LTS) and a storage account, with secrets sourced exclusively from Key Vault and no credentials present anywhere in the codebase. The deployment is idempotent, what-if verified, and version-controlled.

---

*AZ-104 Phase 4 · Project 11 · ostebovik.net*
