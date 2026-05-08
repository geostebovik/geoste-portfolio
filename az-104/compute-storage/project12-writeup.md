# Project 12: Container Registry and Container Apps

**AZ-104 Phase 4 · West US 3 · May 2026**

---

## What I Built

I deployed a complete container workload on Azure using infrastructure-as-code throughout — no portal clicks for resource creation. The stack consists of Azure Container Registry (ACR) for storing container images, a Container Apps Environment (CAE) providing the VNet-injected runtime platform, and a Container App running an nginx web server with traffic splitting between two revisions.

Every resource was defined in modular Bicep files (`acr.bicep`, `cae.bicep`, `ca.bicep`) wired through `main.bicep` with parameters flowing from `dev.bicepparam`. No passwords exist anywhere in the deployment chain — managed identity handles all authentication.

---

## Architecture

```
vnet-az104-dev-wus3-01 (10.0.0.0/16)
│
├── acrdevwus301 (Azure Container Registry)
│     ├── hello-project12:v1  (docker build + push)
│     └── hello-project12:v2  (az acr build — cloud build)
│
└── snet-capp-dev-wus3-01 (10.0.8.0/23, delegated: Microsoft.App/environments)
      └── cae-dev-wus3-01 (Container Apps Environment — internal)
            └── ca-dev-wus3-01 (Container App)
                  ├── SystemAssigned managed identity
                  ├── AcrPull role scoped to registry
                  ├── Scale: min 0, max 3 replicas
                  └── Traffic split: 80% v1 / 20% v2
```

---

## Key Concepts

**Container images and registries.** A container image is an immutable snapshot of an application and everything it needs to run — the OS libraries, runtime, and code sealed together. ACR is a private registry: a warehouse for those snapshots. Nothing runs from ACR directly; a container host pulls an image and stamps out running instances from it. I learned to separate the *build* step (producing the image) from the *push* step (shipping it to the registry) from the *deploy* step (telling the Container App which image to run).

**Container Apps vs the alternatives.** Azure offers four ways to run containers at increasing levels of abstraction: AKS (full Kubernetes), Container Apps (managed Kubernetes-grade features), App Service (PaaS), and ACI (single container, job-style). Container Apps sits in the sweet spot — autoscaling, service discovery, traffic splitting, and scale-to-zero without requiring Kubernetes expertise. For a microservices API that needs to scale with demand and cost nothing when idle, Container Apps is the right choice.

**VNet injection and the networking model.** Container Apps integrates with my existing VNet by delegating a `/23` subnet (`snet-capp-dev-wus3-01`) to `Microsoft.App/environments`. Inbound traffic is internal-only — no public IP, no internet exposure. Outbound traffic routes through my VNet, respecting NSGs and reaching ACR and Key Vault through private paths. The Container Apps Environment is the campus that holds multiple apps; it was declared internal at creation time and cannot be changed afterward — a design decision I made deliberately, planning to rebuild as external for a public portfolio display later.

**Managed identity for ACR pulls.** The Container App has a system-assigned managed identity. I assigned the built-in `AcrPull` role to that identity, scoped specifically to the ACR resource — not the resource group. No credentials are stored anywhere. The Container App presents its identity token to ACR, which validates it against Azure AD and returns a short-lived pull token. This is the same pattern I established in earlier projects for VM-to-Key-Vault access.

**Scale to zero.** Setting `minReplicas: 0` means the Container App runs zero instances when no traffic arrives. Cost drops to zero. The first incoming request cold-starts a new instance in a few seconds. For workloads with uneven demand — internal tools, APIs called during business hours — this is a significant cost advantage over App Service, which idles at a fixed price regardless of traffic.

**Canary deployments with traffic splitting.** Container Apps supports multiple concurrent revisions. By setting `activeRevisionsMode: Multiple` and configuring traffic weights, I split 80% of requests to the stable `v1` revision and 20% to the new `v2` revision. If `v2` shows problems, I can immediately shift 100% back to `v1` without a redeployment. This is production-grade deployment practice: validate new code on real traffic at low blast radius before full promotion.

---

## Design Decisions

**ACR naming.** I initially deployed ACR as `acraz104devwus301` during the bootstrap phase before establishing the convention that the `az104` workload identifier belongs only in the resource group name, not individual resources. I deleted and redeployed as `acrdevwus301` rather than carry forward a naming inconsistency. Clean foundation now beats cleanup debt later.

**Two-pass deployment for role assignment.** The system-assigned managed identity only exists after the Container App is created, which means the role assignment can't be made in the same deployment pass. I solved this with a `deployRoleAssignment` boolean parameter: pass one creates the Container App and its identity, pass two assigns the role. The production-grade solution is a user-assigned managed identity created as infrastructure before the app — the identity exists independently, the role can be assigned before any app deploys, and the timing problem disappears entirely. I'll implement this pattern in a future project.

**Internal environment.** All resources in this environment follow a no-public-IP posture. The Container Apps Environment was declared internal, reachable only from within `vnet-az104-dev-wus3-01`. My Linux VM acts as a jumpbox for internal testing. When I rebuild this environment for public portfolio display, I'll redeploy the environment as external — the CAE cannot be changed in-place.

**Traffic split in Bicep vs CLI.** Defining traffic weights in Bicep requires hardcoding the current revision name, which is auto-generated by Azure and unknown until after deployment. This is fundamentally the wrong tool for an operational concern that changes frequently. The production pattern is: Bicep deploys the new revision, CLI adjusts weights afterward. I implemented the Bicep approach here to understand the mechanism; in practice I would use `az containerapp ingress traffic set` post-deploy.

---

## Two Build Methods

I deliberately built the same image twice using different methods to understand both workflows.

**Local Docker Desktop (`v1`):**
```bash
docker build -t acrdevwus301.azurecr.io/hello-project12:v1 .
docker push acrdevwus301.azurecr.io/hello-project12:v1
```
Build happens on my local machine. Docker Engine stamps the image from the Dockerfile, tags it with the full registry path, then pushes each layer to ACR. Layers from prior pushes are reused — only changed layers transfer.

**ACR Tasks (`v2`):**
```bash
az acr build \
  --registry acrdevwus301 \
  --image hello-project12:v2 \
  .
```
The Dockerfile and build context are uploaded to Azure. ACR spins up a build agent, pulls the base image, executes the Dockerfile steps, and pushes the result — all in the cloud. No local Docker daemon required. This is how CI/CD pipelines build images: GitHub Actions or Azure DevOps runs `az acr build` as a pipeline step, and the image lands in the registry without any developer machine involvement.

---

## Lessons Learned

**Subnet delegation is a prerequisite, not an afterthought.** Container Apps requires the target subnet to be delegated to `Microsoft.App/environments` before the environment can be created. I learned this from a failed deployment. The delegation belongs in the subnet creation command and in the bootstrap script — not discovered at deploy time.

**`Operation expired` means the container runtime timed out, not a network issue.** The error message is vague. The system logs (`az containerapp logs show --type system`) reveal the actual cause: in my case, a 401 from ACR's token exchange endpoint, meaning the managed identity lacked `AcrPull`. The fix was to assign the role and redeploy — but the diagnostic path through the logs was the real learning.

**What-if is a first-class tool, not a safety theater.** Running `az deployment group what-if` before every deploy caught a hardcoded revision name discrepancy, confirmed that the role assignment was correctly scoped to the ACR resource rather than the resource group, and showed the traffic weight changes exactly as designed. The investment of thirty seconds before each deploy has saved multiple failed deployments.

**Private browsing does not persist Cloud Shell storage.** Cloud Shell mounts storage from an Azure Storage account — but this mount requires an authenticated session. Private browsing sessions don't persist the authentication context, so the storage mount doesn't survive. Files created in a private-browsing Cloud Shell session are lost when the session ends.

---

## Resources

- `Modules/acr.bicep` — ACR module, admin disabled, tags
- `Modules/cae.bicep` — Container Apps Environment, VNet-injected, Log Analytics
- `Modules/ca.bicep` — Container App, managed identity, scale config, traffic split
- `main.bicep` — orchestration, existing resource references, outputs
- `dev.bicepparam` — environment-specific parameters, Key Vault secret references
- `Phase04/12_Container_Reg_Apps/Code/Dockerfile` — nginx:alpine, single page
- `Phase04/12_Container_Reg_Apps/Code/index.html` — served content

---

*ostebovik.net · AZ-104 Phase 4 · Project 12*
