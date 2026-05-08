# App Service vs Container Instances vs Virtual Machines
## When to Choose Each — AZ-104 Phase 3 Reference

**ostebovik.net · AZ-104 Phase 3**

---

## The Core Question

Every Azure compute decision starts with the same question: how much of the stack do you want to manage? The three options represent a trade-off between control and operational overhead. The more Azure manages, the less flexibility you have — and the less you have to think about at 2am when something breaks.

```
Virtual Machines          You manage everything above the hypervisor
App Service               Azure manages OS, runtime, patching, scaling
Container Instances       Azure manages the host — you manage the container
```

Think of it as the difference between owning a house, renting an apartment, and booking a hotel room. You have the most control in the house and the least hassle in the hotel — but you can't repaint the hotel walls.

---

## Virtual Machines

### What it is
A full virtualized server running on Azure hardware. You get an OS, a disk, a network interface, and complete control over everything inside. Azure manages the physical host — you manage everything else.

### When to choose it
- **Lift and shift** — migrating an on-premises application that has specific OS requirements, registry settings, or software dependencies that can't be containerized
- **Legacy applications** — software that requires a specific Windows version, .NET Framework version, or Linux kernel module
- **Domain join** — applications that must be members of Active Directory, which requires a full OS
- **Custom OS configuration** — applications needing specific drivers, kernel parameters, or software that can't run in a managed environment
- **Stateful workloads with complex storage** — databases, file servers, or applications with specific disk I/O requirements

### What you own
OS patching, security hardening, agent installation, disk management, scaling logic, high availability configuration, runtime updates. If the OS has a vulnerability, you patch it. If the disk fills up, you expand it. The VM does exactly what you tell it — nothing more.

### Cost model
Billed per hour whether the VM is doing work or sitting idle. A stopped (deallocated) VM stops compute billing but still charges for managed disk storage. This makes VMs expensive for intermittent workloads.

### AZ-104 exam signals
"Domain join", "custom OS", "lift and shift", "specific software version", "IaaS" — reach for VM.

---

## App Service

### What it is
A managed platform for running web applications, APIs, and background jobs. You deploy code or a container image — Azure handles the OS, runtime, patching, load balancing, TLS certificates, and scaling. The unit of billing is the App Service Plan, which is the underlying compute that one or more apps share.

### When to choose it
- **Web applications and REST APIs** — the primary use case, regardless of language (Python, Node, .NET, Java, PHP, Ruby)
- **Continuous deployment** — built-in integration with GitHub, Azure DevOps, and Bitbucket via Deployment Center
- **Blue-green deployments** — deployment slots allow staging environments with zero-downtime swaps
- **Managed TLS** — automatic certificate provisioning and renewal for custom domains
- **Authentication** — built-in OAuth integration with Azure AD, Google, Facebook, GitHub without writing auth code
- **Autoscaling** — scale out based on CPU, memory, or custom metrics without managing VMs

### What you own
Your application code, dependencies, and configuration. The runtime version (Python 3.11, Node 18) is your choice but Azure maintains it. You don't patch the OS, configure the load balancer, or manage TLS certificates unless you want custom behavior.

### Cost model
Billed per App Service Plan hour regardless of how many apps run on it. Multiple apps can share one plan at no extra cost — an efficient model for running several small services. The plan tier determines features: Free and Basic tiers have no slots, no autoscaling, no VNet integration. Standard and Premium tiers unlock production capabilities.

### The container deployment mode
App Service can run container images instead of code — this is not the same as Container Instances. The platform remains App Service (slots, scaling, auth, TLS all still work) but the delivery mechanism is a container image rather than a zip deploy. Use this when your team already has a container build pipeline and wants App Service's operational features without rewriting deployment tooling.

### AZ-104 exam signals
"Web app", "API", "PaaS", "deployment slots", "autoscale", "managed TLS", "GitHub integration" — reach for App Service.

---

## Azure Container Instances

### What it is
The simplest way to run a container in Azure without managing any infrastructure. No cluster, no orchestrator, no App Service Plan. You specify an image, CPU, and memory — Azure runs it. Billing starts when the container starts and stops when it stops, billed per second.

### When to choose it
- **Batch jobs** — data processing, report generation, or any task that runs to completion and exits
- **CI/CD runners** — ephemeral build agents that spin up for a job and disappear
- **Event-driven tasks** — containers triggered by a queue message, timer, or webhook that run briefly then stop
- **Testing and validation** — quickly run a container image to verify behavior without setting up infrastructure
- **Sidecar patterns** — auxiliary containers that support a primary workload (log shippers, proxies)
- **Simple APIs with intermittent traffic** — if traffic is unpredictable and often zero, per-second billing beats an always-on App Service Plan

### What you own
The container image and its configuration. You don't manage hosts, OS, or runtime — those come from the image. Azure manages the host infrastructure entirely.

### What it lacks
No deployment slots, no autoscaling, no built-in TLS termination, no persistent storage beyond mounted Azure Files shares, no built-in auth. If you need any of those, App Service is the right answer.

### Cost model
Billed per second of CPU and memory consumption. A container that runs for 5 minutes costs 5 minutes. When stopped, billing stops completely — no idle charges. This makes ACI extremely cost-effective for intermittent workloads and genuinely expensive for always-on services compared to App Service.

### AZ-104 exam signals
"Serverless containers", "batch job", "short-lived", "event-driven", "no cluster", "per-second billing" — reach for Container Instances.

---

## Decision Framework

```
Does the workload need full OS control, domain join,
or specific kernel/driver requirements?
    YES → Virtual Machine
    NO  ↓

Is it a web app, API, or background service
that runs continuously?
    YES → App Service
    NO  ↓

Does it need slots, autoscale, managed TLS,
or built-in auth?
    YES → App Service
    NO  ↓

Is it a short-lived task, batch job, or
intermittent workload?
    YES → Container Instances
    NO  ↓

Are there multiple containers that need to
communicate, scale independently, or be
orchestrated?
    YES → AKS (Kubernetes) — beyond this comparison
```

---

## Side-by-Side Reference

| Dimension | Virtual Machine | App Service | Container Instances |
|---|---|---|---|
| Abstraction | IaaS | PaaS | CaaS |
| OS management | You | Azure | N/A (image) |
| Startup time | 1-5 min | Seconds | Seconds |
| Scaling | Manual / VMSS | Built-in autoscale | Manual only |
| Cost model | Per hour (always on) | Per plan (always on) | Per second (usage) |
| Deployment slots | No | Yes (Standard+) | No |
| Managed TLS | No | Yes | No |
| Persistent storage | Managed disks | Limited | Azure Files mount |
| Domain join | Yes | No | No |
| Custom OS | Yes | No | Via image |
| Best for | Legacy, IaaS, lift-and-shift | Web apps, APIs, PaaS | Batch, event-driven, testing |

---

## The Exam Trap

The most common AZ-104 trick question pairs App Service with Container Instances. The question describes a containerized web application and asks which service to use. The answer depends on one thing: **does it need to run continuously?**

- Containerized web app serving users continuously → **App Service** (container deployment mode)
- Containerized job that processes a queue and exits → **Container Instances**

The word "container" in the question is a distraction. The decision driver is the workload pattern, not the packaging format.

---

*AZ-104 Phase 3 · ostebovik.net*
