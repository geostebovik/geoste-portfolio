# RPO vs RTO
## What They Mean and How Backup Policy Controls Them
### AZ-104 Phase 3 · Interview Reference

**ostebovik.net · AZ-104 Phase 3**

---

## Why This Matters

RPO and RTO appear in every infrastructure interview and on the AZ-104 exam because they force a concrete conversation about risk tolerance and cost. Anyone can say "we need good backups." RPO and RTO make that statement measurable — and measurable means you can design for it, price it, and hold someone accountable to it.

---

## The Definitions

### RPO — Recovery Point Objective
**How much data can you afford to lose?**

RPO is expressed as a time window and represents the maximum age of the data you'd restore from. If your RPO is 24 hours, you've accepted that in a disaster you might lose up to 24 hours of transactions, records, or changes.

RPO answers the question: *"If everything failed right now, what is the oldest acceptable state to restore to?"*

```
Last backup          Disaster occurs
     │                     │
     ├─────────────────────┤
              ↑
          This gap is your RPO
          All changes in this window are lost
```

A lower RPO means more frequent backups, more storage, more cost. An RPO of zero means synchronous replication — every write is confirmed in two places before returning success. That's expensive and architecturally complex.

### RTO — Recovery Time Objective
**How long can the system be down during recovery?**

RTO is expressed as a time duration and represents the maximum acceptable outage from the moment of failure to the moment the system is operational again. An RTO of 4 hours means the business can survive a 4-hour outage — anything longer causes unacceptable impact.

RTO answers the question: *"How fast do we need to be back online after a failure?"*

```
Disaster occurs      System restored
      │                    │
      ├────────────────────┤
               ↑
           This duration is your RTO
           The business is down for this window
```

A lower RTO requires faster recovery mechanisms — pre-provisioned infrastructure, automated failover, warm standby systems. These cost money to maintain even when never used.

---

## The Relationship Between RPO and RTO

They are independent dimensions but often traded off against each other in budget conversations:

```
                High RPO (accept data loss)
                        │
    Low RTO ────────────┼──────────── High RTO
    (recover fast)      │             (slow recovery ok)
                        │
                Low RPO (minimal data loss)
```

A financial trading system might need RPO of seconds and RTO of minutes — every transaction matters and downtime costs millions per minute. A development environment might accept RPO of 24 hours and RTO of 4 hours — losing a day of dev work is annoying but not catastrophic.

The business defines acceptable RPO and RTO. The infrastructure team designs and prices the solution that meets those targets.

---

## How Azure Backup Policy Controls RPO

The backup policy directly sets your RPO by defining how often backups are taken:

### Backup frequency → RPO ceiling
```
Daily backup at 11pm UTC
    → RPO = up to 23 hours 59 minutes
    → A failure at 10:59pm means you restore from yesterday

Hourly backup (Azure Backup supports this for some workloads)
    → RPO = up to 59 minutes
    → More storage, more cost, tighter protection

Azure Site Recovery continuous replication
    → RPO = as low as 30 seconds
    → Replicates at block level, near-synchronous
    → Significantly higher cost (~$25+/month per VM)
```

### Your Project 10 policy — pol-daily-7day
```
Schedule:   Daily at 11:00 PM UTC
RPO:        Up to ~24 hours
            A failure at 10:59 PM means up to 23h59m of data loss

Retention:
  Daily:    7 days    → can restore to any day in the last week
  Weekly:   4 weeks   → can restore to any week in the last month
  Monthly:  3 months  → can restore to any month in the last quarter
```

The retention tiers don't affect RPO — they affect how far back you can go when choosing a restore point. RPO is set by the backup frequency. Retention is set by business requirements (compliance, audit, "restore the database to last Tuesday").

---

## How Recovery Infrastructure Controls RTO

RTO is controlled by how fast you can restore, not how often you back up. Three Azure mechanisms target different RTO ranges:

### Azure Backup — VM restore
```
RTO range:   30 minutes to several hours
Mechanism:   Restore managed disks from vault,
             deploy new VM or replace existing
Use case:    Accidental deletion, corruption,
             ransomware recovery
Cost:        Backup storage only (low)
```

### Azure Site Recovery (ASR)
```
RTO range:   Minutes (with runbooks) to ~1 hour
Mechanism:   Continuous block-level replication
             to secondary region
             Failover flips DNS to replica VMs
Use case:    Regional outage, DR drill,
             compliance requirement
Cost:        ~$25+/month per replicated VM
             plus egress + storage in target region
```

### Availability Zones + Load Balancer
```
RTO range:   Seconds to minutes (automatic)
Mechanism:   Multiple VM instances across zones
             Load balancer detects failures,
             routes away from unhealthy instances
Use case:    Hardware failure, zone outage
             (not data corruption or ransomware)
Cost:        Double or triple the VM count
```

---

## The Policy → RPO/RTO Mapping for Project 10

```
What you configured          What it gives you
─────────────────────────────────────────────────────────
Daily backup 11pm UTC    →   RPO: ~24 hours
7-day daily retention    →   Can restore to any of last 7 days
4-week weekly retention  →   Can restore to start of any week
                             in last 4 weeks
3-month monthly          →   Can restore to start of any month
                             in last quarter
LRS vault redundancy     →   Vault survives rack/building failure
                             within single region
                             Vault does NOT survive regional outage
GRS vault redundancy     →   Vault survives regional outage
(production standard)        Backup data replicated to paired region
```

---

## The Interview Answer

When an interviewer asks "what's the difference between RPO and RTO?" the complete answer has three parts:

**1. The definitions:**
RPO is how much data you can lose — it's set by backup frequency. RTO is how long recovery takes — it's set by recovery infrastructure.

**2. The trade-off:**
Lower RPO and RTO both cost more. The business defines acceptable values based on the cost of downtime vs the cost of protection. A $10,000/hour revenue system justifies very different investment than an internal reporting tool.

**3. The Azure mapping:**
For VMs: Azure Backup daily schedule sets RPO, vault restore time sets RTO baseline. Azure Site Recovery pushes RPO to seconds and RTO to minutes but at significantly higher cost. The right answer depends on the workload's criticality.

---

## Quick Reference Card

```
RPO   = data loss window      = set by backup FREQUENCY
RTO   = recovery duration     = set by recovery INFRASTRUCTURE

Lower RPO → more frequent backups → more storage cost
Lower RTO → faster recovery tools → more infrastructure cost

Azure Backup    RPO: hours    RTO: 30min-hours   Cost: low
Azure ASR       RPO: seconds  RTO: minutes        Cost: high
Avail Zones     RPO: ~0       RTO: seconds        Cost: 2-3x VMs

Production minimum: GRS vault + daily backup + tested restore
Production DR:      ASR for critical workloads only
```

---

*AZ-104 Phase 3 · ostebovik.net*
