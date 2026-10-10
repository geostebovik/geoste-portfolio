# Phase 2 Orientation — Where Things Stand (start here each Phase 2 session)

---

> ## CURRENT MILESTONE: **M13** — Conditional Access
>
> **This line is the single source of truth for "where are we".** Nothing else
> — not the project instructions, not a scheduled task, not the portfolio site
> — states the milestone number. They all point here. **When a milestone
> moves, change this line and the table's checkmark. That is the whole
> update.**
>
> Last moved: 2026-10-07, M11 → **M13** (Gerard), passing over M12 on
> purpose: M13 must finish inside the Entra ID P2 trial (ends 2026-11-06), and
> M12 has no clock. M12 comes after M13. (M10 → M11 2026-09-23; M9 → M10 and
> M8 → M9 both 2026-09-21.)
>
> **The rule that keeps this true:** a *dated* statement may name a milestone,
> because it was correct on its date and reads as history — STATUS.md session
> entries, Todoist task descriptions, commit messages. *Undated standing
> instructions* must never name one; they point here instead. A milestone
> number in undated guidance is a stale fact waiting to happen.

---

## Road to done (snapshot dated 2026-10-10)

*Added 2026-10-10 at Gerard's request, after he lost track of where the work
stood. This is a dated snapshot, so by the rule above it may name milestones.
**The marker at the top stays the single source of truth for "where are
we".** Update this table in the same edit that moves the marker, so the two
can't drift. Claude drafted it from the Oct 10 recap; Gerard asked for it to be added here.*

**The finished product:** you upload a thumbnail and topic. An Azure Function
runs the M7 agent with no keys and saves the result. The result shows on a page
behind an Entra sign-in that Conditional Access protects. All of it is in Bicep,
monitored, and deployed from GitHub. After that come the write-up, the site
update and the AI-103 exam.

| Step | What it is | State on 2026-10-10 |
|---|---|---|
| M1-M7 (Phase 1) | Documents, search, RAG, evaluation, the M7 agent | Done (acceptance test passed 2026-09-15) |
| M8 | Everything in Bicep | Done 2026-09-21 |
| M9 | Managed identities and roles | Done 2026-09-21 |
| M10 | No keys anywhere | Done 2026-09-23 |
| M11 | The app: upload → Function → result → sign-in page | Done 2026-10-07 |
| M12 | Networking: private endpoints, storage firewall | Built and proven 2026-10-10; **teardown by 2026-10-16** |
| M13 | Conditional Access | Tested 2026-10-09; **rollback in the week of 2026-10-26, before 2026-11-06** |
| M14 | Operate: tracing, alerts, GitHub deploys over OIDC | Not started. No deadline, and doesn't depend on M13 |
| Write-ups | Phase 2 write-up, then one joint push with the M7 write-up | M7's is waiting on outside readers (Gerard) |
| Site | ostebovik.net's AI page updated to match | After the push |
| Exam | AI-103 | No date set (Gerard, 2026-10-10) |

**Why the marker and the work can differ:** the marker stays on M13 until its
rollback, while M12 and M14 can run in the gap, because neither depends on the
trial clock.

**Planned but off the critical path:** the classic-agent migration (before
2027-03-31; first step due Dec 1), which now includes the agent-isolation build
(D-M12-8). Everything else is parked in Todoist or the Phase 2 Backlog.

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

**Status as of:** September 24, 2026.
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
  **Explained 2026-09-23:** a pre-registered fixed-text test-retest showed one
  unchanged item7 draft passing 0–17 of 40 re-reads by the same judge. The
  trigger needs two things at once: drafts that raise returns or pricing (the
  agent wrote 0–9 of 15 per pass) and a favourable read by the judge (~25–30%
  on those drafts; 0 of 44 on the rest). Corrected the same day; the first
  wording blamed the judge alone. **Decision (a), Gerard:**
  item7's judged first-draft row is reported as a rate with an expected band,
  not scored against the key. **Implemented at `67d0e31` (2026-09-23).**
  *(Updated 2026-09-24: this line said "Implementation is the current next
  action in STATUS.md" after it had been done.)*
  The run carries `git_changed_during_run: true`; no `.py` file is in the
  changed set, so the measured code is byte-identical to `aa96bea`.
- **M10 is COMPLETE (2026-09-23, Gerard moved the marker).** Both remaining
  clauses closed that day, and M3's stated exception with them — see STATUS.md
  Sep 23. *As written before closing:* two clauses of its done-when remain:
  1. **Remove `get_search_admin_key()` and the dead `get_subscription_key`
     imports** — in their own commit, not bundled with anything.
     *(Corrected 2026-09-23: this clause said to remove both helpers.
     `get_subscription_key()` cannot go — `m3_analyze.py:250` calls it, inside
     the pipeline the amended done-when names as a stated exception. It and
     `get_storage_key()` leave with M3's migration. Nine tracked scripts still
     import it without calling it; `get_search_admin_key()` has no tracked
     caller at all.)*
  2. **Hand-run `m6_generate.py` and `m6_probe.py`** — the "M3-M6 scripts are
     smoke-tested" clause. Neither can be imported for automated checking
     (module-scope side effects, see the backlog), so
     `probe_keyless_smoke.py` verifies them statically only.
  **Closed 2026-09-23.** Clause 1 at `08bc35c`: `get_subscription_key()`,
  `get_storage_key()` and `get_search_admin_key()` removed with their dead
  imports, after M3's migration (`fcc55b6`) left them uncalled; the eight
  import-safe modules import cleanly. Clause 2: `m6_generate.py` (28 answers, 14
  per model, none empty, `20260923-122420_generate_results.json`) and
  `m6_probe.py` both hand-run keyless.
- **M11 pass 1 (upload → result) is DEPLOYED AND WORKING (2026-09-24).**
  Upload → Event Grid → queue → Function → agent → result in 46 s. Two runs in
  Azure matched item4's answer key. RBAC rows 4-8, 14 and 15 confirmed in
  production, and row 14 is account-scoped (see the RBAC model). Remaining for
  M11: the poison path (row 16) and pass 2, sign-in. Details in `m11-prep.md`
  and STATUS.md Sep 24. *(Row 16 verified 2026-09-25.)*
- **M11 pass 2 (sign-in) is DEPLOYED AND PROVEN (2026-09-30).** Secretless
  built-in authentication through `id-iip-dev-wus-03`'s federated credential,
  the app registration and the group in `infrastructure/iip/entra.bicep`, and
  the results page at `/api/results`. A non-admin test user was refused
  unassigned (AADSTS50105), then reached the page once assigned. The RBAC
  model's VERIFY rows are all settled (its "VERIFY ledger"). **The one
  remaining step for M11 is the "group member" in its done-when.** letter7 is
  on Entra Free and a group-to-app assignment needs P1/P2, so the group swap
  is the P2 trial's first step (STATUS.md Sep 30).
- **M11 is COMPLETE (2026-10-07; Gerard moved the marker to M13).** On the P2
  trial's first day the viewers group was assigned to the app, the interim
  direct assignment was deleted by CLI, and the gate was re-tested with
  `iip-ca-test`: refused with neither path (AADSTS50105), then through as a
  group member. Every VERIFY row is recorded (the RBAC model's VERIFY ledger).
  M12 waits behind M13, because only M13 runs on the trial clock.
- **M13: T1-T6 pass with CA001 On, and the evidence is exported
  (2026-10-09).** Two of the three done-when clauses are met; the export is in
  `evidence/m13-conditional-access/`, the results in the CA spec's "Progress,
  2026-10-09". **The rollback (C9) is the only step left**, planned for the
  week of 2026-10-26 (Gerard), about 10 days before the trial ends
  (2026-11-06). The marker stays on M13 until C9 is done.
- **M12 is under way while M13 waits (2026-10-09).** Cost estimate and design
  done (`m12-prep.md`, decisions D-M12-1 to -7). Build stages 1 (VNet,
  private endpoints, DNS) and 2 (the Function in the VNet) are deployed and
  tested; no NAT gateway is needed. ~~Stage 3, the storage firewall, is next.~~
  **Stage 3, the storage firewall, is deployed and tested (2026-10-10):** the
  app works end to end with the account closed to all but the home IP, so the
  private paths are verified, and the two provisioning flags are decided
  (`defaultAction` Deny, `publicNetworkAccess` Enabled). **Both done-when
  clauses are met**, and the agent-isolation write-up is done the same day
  (`m12-prep.md`; to be built inside the classic-API migration, D-M12-8). Only
  the teardown remains (Todoist, due 2026-10-16). The marker is not moved:
  that is Gerard's call once M13 closes.
- **Current milestone: see the marker at the top of this file.**
- ~~**Nothing is keyless yet.**~~ **Superseded 2026-09-22:** all twelve call
  sites across the nine tracked scripts now authenticate with Entra ID
  (committed `aa96bea`). The key helpers remain in the source, unused, pending
  removal — see the M10 clauses above. *(Removed at `08bc35c`, 2026-09-23.)*

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
  done**, with recurring billing turned off straight away. *(Amended
  2026-09-30: M11's own last step, assigning the viewers group to the app,
  needs P1/P2. So the trial starts once everything else in M11 is done, and
  the group swap is its first step. Found the day pass 2 was built.)*
  *(Started 2026-10-07, from the Entra admin center → Billing → Trials →
  Activate, which hands off to a Microsoft 365 checkout: 100 licences, a card
  on file for identity only, $0. **Recurring billing was Off by default**,
  with its edit control greyed out (Gerard's screenshot). It ends 2026-11-06
  or -07: two portal pages disagree, so plan to the 6th. Todoist reminder due
  Nov 2.)*
- **RBAC:** D1–D7 all option (a); see the RBAC model.
- **Conditional Access design:** C1–C9 all option (a), with one break-glass
  account and passkeys; see the spec.
- **Naming:** new resources follow CAF, even where existing names don't.
- **Agent network isolation is designed, not deployed.** It has to be chosen
  when the Foundry account is created, and it needs Cosmos DB, AI Search and
  Storage accounts of its own.

**Facts that shape the order of work:**
- ~~**Only one script is keyless today.**~~ **Superseded 2026-09-22 (M10,
  `aa96bea`):** all twelve call sites in the nine tracked scripts are keyless;
  `m3_analyze.py`'s own pipeline is the stated exception. As written Sep 16:
  `m7_orchestrator.py` signs in with
  Entra ID; **eleven scripts use account keys**, including M7's audit
  tool, evaluator and legibility check. The Function must not use keys, so
  the M7 tools are migrated **before** the Function is built.
- **Migrating M7's tools touches files the acceptance test covers,** so the
  test is re-run (about 95 min). That re-run is revisit trigger (b) for the
  accepted `[content]` colour flaw, so one run can cover both.
- **Security defaults are ON in `letter7`** (Gerard's screenshot, Sep 16).
  Conditional Access requires turning them **off** for the whole tenant.
  The baseline policies go on first (see the spec).
- ~~**Nothing in the IIP resource group is in Bicep.**~~ **Superseded
  2026-09-21 (M8):** all of it is, model deployments and their TPM included —
  see `infrastructure/iip/`. As written Sep 16: that includes the model
  deployments, which were raised to 300K TPM in the portal.

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
| **M10** ✅ | **Keyless migration.** The **nine tracked** key-based scripts move to Entra ID, M7's tools first. *(The plan said eleven; `m10-prep.md` corrected that to ten on the grounds that `tester3.py` is gitignored; `m6_probe.py` is gitignored on the same `.gitignore` line and was missed. Nine is the tracked count, confirmed 2026-09-22 with `git ls-files`. `m6_probe.py` was migrated anyway.)* M7's acceptance test is re-run, optionally with one colour-wording attempt bundled in. The M3–M6 scripts are smoke-tested. | The acceptance test passes on the keyless code, and no **surveyed** script reads a key. **Amended 2026-09-22, by Gerard:** `m3_analyze.py`'s own Content Understanding pipeline is a STATED EXCEPTION. It reads two keys (`Ocp-Apim-Subscription-Key` at lines 183/206, and an account-key SAS via `get_storage_key()`), and `m10-prep.md` never surveyed it — it treated `m3_analyze.py` as the *home* of the key helper and never looked at the module's own `main()`. M3's migration is tracked separately: the REST auth swap is small, the account-key SAS → user-delegation SAS is a design change that amends the RBAC model. The exception is named here rather than left as a milestone that quietly stays open. **Exception CLOSED 2026-09-23:** `m3_analyze.py` migrated at `fcc55b6` (Entra ID bearer auth; user-delegation SAS for `--blob`, decision (A), Gerard) and verified live on both paths, so "no script reads a key" now holds without exception. | 1–2 sessions (includes the ~95 min run) | M9 |
| **M11** ✅ | **The app.** The Function app on Flex Consumption, its host storage, Application Insights and Log Analytics, the Event Grid system topic, the ~~blob trigger~~ **storage queue → queue trigger** → agent → results flow, the results page with built-in sign-in (via `id-iip-dev-wus-03` as a federated credential, no client secret), the app registration and the viewers group. *(Amended 2026-09-24: Gerard's D-M11-1 (b) and D-M11-2 (b), Sep 23 — see `m11-prep.md`.)* Settles the RBAC model's **VERIFY** rows. | An upload produces a result, and a group member can sign in and see it. The VERIFY rows are recorded as confirmed or changed. | 2–3 sessions | M10 |
| **M12** | **Networking.** A VNet with an integration subnet, and private endpoints for ~~Key Vault and~~ storage. *(Amended 2026-10-09, Gerard, D-M12-1: endpoints on `stiipdevwus01` blob + queue only; Key Vault is empty on purpose, so it gets none. Built for an evidence window, then deleted, Bicep kept (D-M12-2). See `m12-prep.md`.)* ~~Decides Event Grid delivery vs. inbound restrictions (Todoist task),~~ *(Amended 2026-09-24. D-M11-1 (b) removed the Function's inbound webhook, so the original question is gone and the Todoist task was closed Sep 23 — but the constraint **moved to the storage account**, it did not disappear. Microsoft Learn (Event Grid, storage queue handler): once `stiipdevwus01` has a firewall or network rule, Event Grid can deliver to its queue only with the system topic's **system-assigned** identity and only with *Allow Azure services on the trusted service list* enabled; a user-assigned identity is not supported at all. So M11 should give the system topic a system-assigned identity now, and M12 must keep the trusted-services exception on.)* Decides the two provisioning flags (`networkAcls.defaultAction`, `publicNetworkAccess`). Agent isolation is written up as designed-not-deployed, with the cost stated. | The app still works end to end, with the private paths verified. The cost is estimated with the Azure pricing calculator **before** anything is built. *(Amended 2026-10-09, Gerard, D-M12-3: estimated from Azure's retail price list, the calculator's own source. **Done 2026-10-09:** $15.60/month running, about $3.60 for a one-week window; one open item, outbound internet through the VNet, in `m12-prep.md`.)* | 1–2 sessions | M11 |
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
write-up. *(Corrected 2026-09-28: this used to include "the two out-of-date
site lines". They were fixed on 2026-09-21 in `5fccd4a`.)*

## Phase 2 Backlog

Deferred items go here, not in `STATUS.md`.

*Each milestone's pre-build survey lives in its own `m<N>-prep.md`
(`m10-prep.md`, `m11-prep.md`). Read the current milestone's — the marker at
the top of this file says which — results box first, before starting work.
(Amended 2026-09-24: this line pointed only at `m10-prep.md`, after M10
closed.)*
- ~~**Blob soft delete is OFF on `stiipdevwus01`.**~~ **DONE 2026-09-29.**
  Gerard's decision: blob **and** container soft delete, 7 days each (container
  soft delete because deleting a container bypasses blob soft delete). Deployed
  as `m11-softdelete-20260929` and checked with `blob-service-properties show`.
  The original note follows. Found 2026-09-21 from an M9
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
- ~~**Make D1 accurate.**~~ **DONE 2026-09-21; closed out 2026-09-30.**
  `phase2-rbac-model-draft.md`'s "D1 correction" section, written 2026-09-21,
  records the real posture, and both row 1 and the D1 row point to it. This
  item was never struck through, so it stayed open here, in STATUS.md and in
  Todoist. The original text follows. *(Re-confirmed live 2026-09-22 from
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
  **Two known breakages, and a stronger reason (added 2026-09-23).** Turning
  it on stops (1) a **VS Code poll** that retrieves the account key every
  14m42s under Gerard's account (STATUS.md, Sep 23), and (2) **`m3_analyze.py`'s
  exempted pipeline**, until M3 is migrated. "Nothing key-based remains" is
  therefore not yet true, and these two are the list. **(2) resolved
  2026-09-23** — M3 is keyless (`fcc55b6`). The VS Code poll is now the only
  known consumer of the account key. The poll also means
  `listKeys` currently has **no audit value**: at roughly eight retrievals an
  hour under Gerard's own identity, a genuine retrieval is indistinguishable
  from the timer. `disableLocalAuth` makes a retrieved key useless *and* makes
  "who retrieved a key?" worth asking again — a stronger argument than "the
  code no longer needs keys".
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
  module-scope work under `if __name__ == "__main__":`. **Add `m6_evaluate.py`**
  (found 2026-09-23): no `__main__` guard either, so it was left out of the
  import check that closed M10 clause 1 and is covered by a compile check only.
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
| A milestone's pre-build survey and probe results | `m10-prep.md`, `m11-prep.md` |
| Why Phase 2 looks the way it does | Claude project doc `claude/2026-09-16-phase2-plan-review.md` |
| The M7 write-up | `m7-writeup-draft.md` |
