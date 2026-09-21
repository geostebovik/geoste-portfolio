# Phase 2 Orientation — Where Things Stand (start here each Phase 2 session)

**What this page is:** a snapshot of where things stand now. It isn't a log
(that's `STATUS.md`). It answers two questions: what Phase 2 is building,
and which step comes next. Update it whenever a milestone moves from
*planned* to *built*, or from *built* to *verified*.
**Created 2026-09-16.** Claude drafted it and proposed the milestone
numbering. Gerard confirmed the numbering and the order of work the same
day.

**Still read `m7-orientation.md` for two things:**
- its **session-start and end-of-session checklists**, which apply to every
  session;
- the **M7 Backlog.**

M7 itself is finished: its acceptance test passed at `a915217`, and its
write-up is waiting for outside readers and a joint push with Phase 2.

## Status

**Status as of:** September 21, 2026.
- **Both Phase 2 entry-checklist items are agreed on paper:**
  - the RBAC model, in `phase2-rbac-model-draft.md`;
  - the Conditional Access spec, in `phase2-conditional-access-spec-draft.md`.
- **Current milestone: M8 — built, not yet signed off.**
  The Bicep is written and builds warning-clean:
  `infrastructure/iip/` (`main.bicep`, `dev.bicepparam`, four modules).
  `what-if` reports **3 resources to modify, 6 no change**. Of the three, one
  is the intended `managed-by` tag fix on Search and the rest are properties
  no template can assert. The complete expected output is registered in
  `infrastructure/iip/README.md`, so anything else in a future run is a real
  change.
- **M8's done-when is an open decision** — see the note under the table.

## What Phase 2 builds

**One sentence:** a thumbnail and topic uploaded to Blob storage trigger an
Azure Function (Flex Consumption plan). The Function runs the M7 agent
using a managed identity with no keys, writes the results back to Blob,
and serves a small results page. The page sits behind an Entra ID sign-in
protected by Conditional Access.

**Decisions already made (Gerard, Sep 16).** The review is in the Claude
project doc `claude/2026-09-16-phase2-plan-review.md`.
- **App shape:** as above. The Function runs on **Flex Consumption**,
  because Linux Consumption retires on Sep 30, 2028 and doesn't support
  VNets.
- **Conditional Access is deployed, not just designed.** It uses a 30-day
  Entra ID P2 trial in the `letter7` tenant, **started only once M11 is
  done**, with recurring billing turned off straight away.
- **RBAC:** D1–D7 all option (a); see the RBAC model.
- **Conditional Access design:** C1–C9 all option (a), with one break-glass
  account and passkeys; see the spec.
- **Naming:** new resources follow CAF, even where existing names don't.
- **Agent network isolation is designed, not deployed.** It has to be chosen
  when the Foundry account is created, and it needs Cosmos DB, AI Search and
  Storage accounts of its own.

**Facts that shape the order of work:**
- **Only one script is keyless today.** `m7_orchestrator.py` signs in with
  Entra ID; **eleven scripts use account keys**, including M7's audit
  tool, evaluator and legibility check. The Function must not use keys, so
  the M7 tools are migrated **before** the Function is built.
- **Migrating M7's tools touches files the acceptance test covers,** so the
  test is re-run (about 95 min). That re-run is revisit trigger (b) for the
  accepted `[content]` colour flaw, so one run can cover both.
- **Security defaults are ON in `letter7`** (Gerard's screenshot, Sep 16).
  Conditional Access requires turning them **off** for the whole tenant.
  The baseline policies go on first (see the spec).
- **Nothing in the IIP resource group is in Bicep.** That includes the
  model deployments, which were raised to 300K TPM in the portal.

## Milestones

The numbering continues from Phase 1 (M1–M7), so Todoist, the Friday
check-in and the Sunday punch list keep one sequence. **Claude proposed
this numbering and Gerard confirmed it (Sep 16).** The table is already in
build order. M10 (keyless) comes before M11 (the app) on purpose: the
Function must not use keys.

| # | Milestone | Done when | Rough size | Depends on |
|---|---|---|---|---|
| **M8** | **IaC baseline.** Bicep for what already exists in `rg-iip-dev-wus-01`: the Foundry account and project, the model deployments (with their current TPM), storage, Key Vault and AI Search. Adds the CAF tag set. | `az deployment group what-if` shows **no changes** against the live resources, and the Bicep is committed. | 1–2 sessions | — |
| **M9** | **Identity foundation.** Managed identities `id-iip-dev-wus-01` and `-02`, plus the role assignments from the RBAC model, in Bicep. | The assignments exist and match the RBAC table, and Gerard's own data-plane roles (rows 2–3) are in place. | 1 session | M8 |
| **M10** | **Keyless migration.** The 11 key-based scripts move to Entra ID, M7's tools first. M7's acceptance test is re-run, optionally with one colour-wording attempt bundled in. The M3–M6 scripts are smoke-tested. | The acceptance test passes on the keyless code, and no script reads a key. | 1–2 sessions (includes the ~95 min run) | M9 |
| **M11** | **The app.** The Function app on Flex Consumption, its host storage, Application Insights and Log Analytics, the Event Grid system topic, the blob trigger → agent → results flow, the results page with built-in sign-in, the app registration and the viewers group. Settles the RBAC model's **VERIFY** rows. | An upload produces a result, and a group member can sign in and see it. The VERIFY rows are recorded as confirmed or changed. | 2–3 sessions | M10 |
| **M12** | **Networking.** A VNet with an integration subnet, and private endpoints for Key Vault and storage. Decides Event Grid delivery vs. inbound restrictions (Todoist task), and the two provisioning flags (`networkAcls.defaultAction`, `publicNetworkAccess`). Agent isolation is written up as designed-not-deployed, with the cost stated. | The app still works end to end, with the private paths verified. The cost is estimated with the Azure pricing calculator **before** anything is built. | 1–2 sessions | M11 |
| **M13** | **Conditional Access.** Inside the P2 trial window: the break-glass account, the baseline policies, then security defaults off, then CA001 in report-only mode and then on, test matrix T1–T6, evidence exported, and the rollback before the trial ends. | T1–T6 pass with CA001 on, the evidence is committed, and the rollback is done before the trial end date. | 1–2 sessions, **inside the 30 days** | M11 (ideally M12) |
| **M14** | **Operate.** Foundry tracing into Application Insights, alerts and an action group (reusing the $90 budget alert), and CI/CD from GitHub Actions over OIDC using `id-iip-dev-wus-02`. | A push deploys the Function, and a trace and an alert can each be shown. | 1–2 sessions | M11 |

**M8's done-when — open.** The table says "`az deployment group what-if`
shows **no changes**". Azure will not produce that against this resource
group: `properties.armFeatures` on the Foundry account, and `kind`,
`agentIdentity`, `internalId`, `isDefault` and `endpoints` on the project, are
either flagged `ReadOnly` or absent from the `2025-06-01` schema, so no
template can declare them and `what-if` reports them as deletions forever.

Claude proposed (Sep 21) amending the condition to: *`what-if` reports no
changes other than the documented provider-owned properties listed in
`infrastructure/iip/README.md`.* **Gerard has not decided.** It matters beyond
M8 — it is the standard M9-M14 inherit, and the alternative to amending it is
either leaving M8 permanently open on a condition Azure will not meet, or
deleting properties from the template to force a clean run, which would make
the Bicep a worse description of the infrastructure rather than a better one.

**After M14:** write up Phase 2, then make **one joint push** with the M7
write-up and the two out-of-date site lines.

## Phase 2 Backlog

Deferred items go here, not in `STATUS.md`.
- **Two emergency-access accounts,** as Microsoft recommends, instead of
  one. One is a deliberate choice for a lab with a single admin (C2).
- **Guest access to the results page.** Authentication strength for guests
  depends on the cross-tenant MFA trust settings, so plan that before
  inviting anyone (C4 note).
- **Risk-based Conditional Access,** which needs P2 (C3 option c). A stretch
  goal.
- **Conditional Access for workload identities.** Needs a separate licence;
  out of scope.

## Which doc answers which question

| Question | Doc |
|---|---|
| What is Phase 2 building, and what's next? | this file |
| What happened, and why? | `STATUS.md` session log |
| Who can access what? | `phase2-rbac-model-draft.md` |
| The Conditional Access design and its tests | `phase2-conditional-access-spec-draft.md` |
| Session checklists; the M7 backlog | `m7-orientation.md` |
| Why Phase 2 looks the way it does | Claude project doc `claude/2026-09-16-phase2-plan-review.md` |
| The M7 write-up | `m7-writeup-draft.md` |
