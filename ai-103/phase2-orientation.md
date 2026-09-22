# Phase 2 Orientation — Where Things Stand (start here each Phase 2 session)

---

> ## CURRENT MILESTONE: **M10** — Keyless migration
>
> **This line is the single source of truth for "where are we".** Nothing else
> — not the project instructions, not a scheduled task, not the portfolio site
> — states the milestone number. They all point here. **When a milestone
> moves, change this line and the table's checkmark. That is the whole
> update.**
>
> Last moved: 2026-09-21, M9 → M10. (M8 → M9 also 2026-09-21.)
>
> **The rule that keeps this true:** a *dated* statement may name a milestone,
> because it was correct on its date and reads as history — STATUS.md session
> entries, Todoist task descriptions, commit messages. *Undated standing
> instructions* must never name one; they point here instead. A milestone
> number in undated guidance is a stale fact waiting to happen.

---

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

**Status as of:** September 22, 2026.
- **Both Phase 2 entry-checklist items are agreed on paper:**
  - the RBAC model, in `phase2-rbac-model-draft.md`;
  - the Conditional Access spec, in `phase2-conditional-access-spec-draft.md`.
- **M9 is COMPLETE** (deployed and verified 2026-09-21). The first real
  deployment: `id-iip-dev-wus-01` and `-02`, the `uploads` and `results`
  containers, and RBAC rows 2, 4, 5, 6 and 9 — all verified at the intended
  scope with `az role assignment list`. Rows 7, 8 and 12 are deferred to M11,
  which creates the resources they point at. Build-time corrections to the RBAC
  model are recorded in `phase2-rbac-model-draft.md`.
- **M8 is COMPLETE** (signed off 2026-09-21, at `86c53bb`), and **now tested
  rather than predicted**: M9's deployment applied the M8 baseline against the
  live resource group without recreating anything — the Foundry account and
  project principal IDs are unchanged — and the pinned `customSubDomainName`
  held, so the endpoint every script calls is intact.
  `infrastructure/iip/` holds `main.bicep`, `dev.bicepparam` and four modules.
  `what-if` reports **3 resources to modify, 6 no change**; all three are
  registered in `infrastructure/iip/README.md`, which is the complete expected
  output. Anything else in a future run is a real change.
  The one intended diff (`+ tags.managed-by` on Search) applied on M9's
  deployment, which was the first real one. *(Corrected 2026-09-22: this
  bullet previously ended "Nothing has been deployed yet … which M9 will be",
  contradicting the M9 bullet four lines above it. Written before M9 ran and
  never updated when it did.)*
- **M10's acceptance test is CERTIFIED (2026-09-22),** on
  `20260922-131551_orchestrator_stability.json`: 15 runs, `git_head aa96bea`,
  **240/240 deterministic audit rows** and 7 of 8 items at 15/15 on the judged
  rows. item7 came in at 12/15 — a pre-registered known variance whose Sep 11
  revisit trigger has now fired, **not** a migration regression, and the answer
  key was deliberately left unchanged. See STATUS.md's Sep 22 entry.
  The run carries `git_changed_during_run: true`; no `.py` file is in the
  changed set, so the measured code is byte-identical to `aa96bea`.
- **M10 IS NOT FINISHED.** Two clauses of its done-when remain:
  1. **Remove `get_subscription_key()` and `get_search_admin_key()`** — kept
     deliberately unused until the acceptance test passed, and removed in their
     own commit, not bundled with anything.
  2. **Hand-run `m6_generate.py` and `m6_probe.py`** — the "M3-M6 scripts are
     smoke-tested" clause. Neither can be imported for automated checking
     (module-scope side effects, see the backlog), so
     `probe_keyless_smoke.py` verifies them statically only.
- **Current milestone: see the marker at the top of this file.**
- ~~**Nothing is keyless yet.**~~ **Superseded 2026-09-22:** all twelve call
  sites across the nine tracked scripts now authenticate with Entra ID
  (committed `aa96bea`). The key helpers remain in the source, unused, pending
  removal — see the M10 clauses above.

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
| **M8** ✅ | **IaC baseline.** Bicep for what already exists in `rg-iip-dev-wus-01`: the Foundry account and project, the model deployments (with their current TPM), storage, Key Vault and AI Search. Adds the CAF tag set. | `az deployment group what-if` reports **no changes other than the documented provider-owned properties registered in `infrastructure/iip/README.md`**, and the Bicep is committed. | 1–2 sessions | — |
| **M9** ✅ | **Identity foundation.** Managed identities `id-iip-dev-wus-01` and `-02`, plus the role assignments from the RBAC model, in Bicep. | The assignments exist and match the RBAC table, and Gerard's own data-plane roles (rows 2–3) are in place. | 1 session | M8 |
| **M10** | **Keyless migration.** The **nine tracked** key-based scripts move to Entra ID, M7's tools first. *(The plan said eleven; `m10-prep.md` corrected that to ten on the grounds that `tester3.py` is gitignored; `m6_probe.py` is gitignored on the same `.gitignore` line and was missed. Nine is the tracked count, confirmed 2026-09-22 with `git ls-files`. `m6_probe.py` was migrated anyway.)* M7's acceptance test is re-run, optionally with one colour-wording attempt bundled in. The M3–M6 scripts are smoke-tested. | The acceptance test passes on the keyless code, and no script reads a key. | 1–2 sessions (includes the ~95 min run) | M9 |
| **M11** | **The app.** The Function app on Flex Consumption, its host storage, Application Insights and Log Analytics, the Event Grid system topic, the blob trigger → agent → results flow, the results page with built-in sign-in, the app registration and the viewers group. Settles the RBAC model's **VERIFY** rows. | An upload produces a result, and a group member can sign in and see it. The VERIFY rows are recorded as confirmed or changed. | 2–3 sessions | M10 |
| **M12** | **Networking.** A VNet with an integration subnet, and private endpoints for Key Vault and storage. Decides Event Grid delivery vs. inbound restrictions (Todoist task), and the two provisioning flags (`networkAcls.defaultAction`, `publicNetworkAccess`). Agent isolation is written up as designed-not-deployed, with the cost stated. | The app still works end to end, with the private paths verified. The cost is estimated with the Azure pricing calculator **before** anything is built. | 1–2 sessions | M11 |
| **M13** | **Conditional Access.** Inside the P2 trial window: the break-glass account, the baseline policies, then security defaults off, then CA001 in report-only mode and then on, test matrix T1–T6, evidence exported, and the rollback before the trial ends. | T1–T6 pass with CA001 on, the evidence is committed, and the rollback is done before the trial end date. | 1–2 sessions, **inside the 30 days** | M11 (ideally M12) |
| **M14** | **Operate.** Foundry tracing into Application Insights, alerts and an action group (reusing the $90 budget alert), and CI/CD from GitHub Actions over OIDC using `id-iip-dev-wus-02`. | A push deploys the Function, and a trace and an alert can each be shown. | 1–2 sessions | M11 |

**M8's done-when — amended Sep 21, by Gerard.** It originally read
"`what-if` shows **no changes**". Azure will not produce that against this
resource group: `properties.armFeatures` on the Foundry account, and `kind`,
`agentIdentity`, `internalId`, `isDefault` and `endpoints` on the project, are
either flagged `ReadOnly` or absent from the `2025-06-01` schema, so no
template can declare them and `what-if` reports them as deletions forever.

Gerard chose to amend the condition rather than either leave M8 permanently
open or delete the stubborn properties to force a clean run — on the grounds
that the amended version is more accurate and does not hide the warts. **It is
a stricter standard than it sounds:** every accepted diff must be individually
justified in writing in the register, and any line not in the register is a
real change. **This wording is inherited by M9-M14.**

**After M14:** write up Phase 2, then make **one joint push** with the M7
write-up and the two out-of-date site lines.

## Phase 2 Backlog

Deferred items go here, not in `STATUS.md`.

*`m10-prep.md` holds the surveyed plan for M10 — read it before starting that
milestone; it records a probable blocker on the free-tier Search service.*
- **Blob soft delete is OFF on `stiipdevwus01`.** Found 2026-09-21 from an M9
  what-if: `deleteRetentionPolicy.enabled` is `false` on the app data account's
  blob service. M9 declares it as found rather than changing it. Worth revisiting
  at **M11**, when the Function starts writing results there — an accidental
  delete of a results blob is currently unrecoverable, and turning soft delete on
  is a one-line change with a small storage cost. A deliberate decision, not a
  default.
- ~~**Remove the subscription-scope `Foundry User` grant.**~~ **DONE
  2026-09-22.** Removed before M10's probes, not after.
  **Its stated precondition was unsatisfiable and that is worth recording.**
  The item said to remove the grant "only after M10's acceptance test has
  passed on the account-scope grant" — but while the subscription grant
  exists it silently carries that test, so the test can never run *on the
  account-scope grant* and the condition can never be met. The item would
  have sat open forever, and the eventual removal would have broken M11's
  Function with no diagnosis, because `id-iip-dev-wus-01` has no subscription
  grant to fall back on.
  The safe order was the reverse: remove first (one reversible command), then
  measure. Gerard and `id-iip-dev-wus-01` now hold the same grant at the same
  scope, which is what makes M10's results transfer to the Function.
  **Lesson:** a precondition that the thing being gated would itself defeat is
  not a safety check.
- **Make D1 accurate.** *(Re-confirmed live 2026-09-22 from
  `az role assignment list --include-inherited`: Owner on the `Non-Prod`
  management group, Contributor on management group `e0249b00-…`. Still open;
  this is now a read-twice fact, not a single observation.)*
  D1 documents the admin posture as "keep subscription
  Owner and document it as a single-admin exception." The real posture, read on
  2026-09-21, is broader: **Owner on the `Non-Prod` management group** and
  **Contributor on the tenant root management group**, both wider than
  subscription Owner and neither mentioned. This is a documentation fix, not a
  permissions change — the access is reasonable for a single-admin lab, but the
  RBAC model is resume material and currently understates the privilege it is
  meant to disclose.
- **`disableLocalAuth` on the Foundry account — this is what makes M10 mean
  something.** Found 2026-09-22 while reading the Foundry User role definition
  (`53ca6127-db72-4b80-b1b0-d745d6d5456d`). Its `actions` include
  `Microsoft.CognitiveServices/accounts/listkeys/action`, so an identity
  granted Foundry User *for keyless operation* can still retrieve the account
  keys. M10 stops the code reading keys; it does not remove the permission to
  read them, on the Function identity, in production. `m10-prep.md` lists
  `disableLocalAuth` as optional step 6 tidy-up. It is not tidy-up — it is the
  step that renders a retrieved key useless. Decide it deliberately at **M11**,
  once nothing key-based remains.
- **Foundry User is a wildcard role, and Principle 2 cannot currently be met.**
  Its `dataActions` are `Microsoft.CognitiveServices/*` — everything on the
  account, not "Vision Read and chat". There is no narrower built-in role
  covering *both* OpenAI inference and Vision Read, because `aif-dev-wus-01`
  is one shared AIServices account serving both (the decision
  `m7_legibility_check.py` records as "no second Azure resource"). So the
  shared-account choice has a governance cost, and the RBAC model should state
  it as an accepted trade-off rather than leave Principle 2 reading as though
  it were satisfied. Also worth evaluating at M11: **Foundry Agent Consumer**,
  which Microsoft documents as least-privilege for principals that only call
  agents — neither the RBAC model nor `m10-prep.md` considered it.
- **`m6_generate.py` and `m6_probe.py` run real work at module scope.**
  Importing either one executes it — `m6_generate` runs a full generate loop
  across two deployments and writes a results file. They therefore cannot be
  imported for testing, only executed, which is why `probe_keyless_smoke.py`
  verifies them by reading their source instead. `m5_retrieve.py`'s docstring
  flagged this about `m6_generate` on 2026-08-20; it is now also the reason
  two scripts sit outside every automated check. Small refactor: move the
  module-scope work under `if __name__ == "__main__":`.
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
