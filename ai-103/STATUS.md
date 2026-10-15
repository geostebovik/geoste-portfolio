# IIP — Current Status

**This is a living document.** No date in the filename — it gets edited in
place each session, not re-copied. If you're looking for full historical
narrative (the "why" behind past decisions, session-by-session), that lives
in the frozen archive `MASTER-REFERENCE-0724.md` in the Drive IIP folder —
closed, not touched or re-read during normal sessions. This file is the only
thing that should need reading/updating at the start of a normal session.

**How this file is organized (restructured 2026-09-06).** Top to bottom:
the current next action, then the reference sections that change slowly
(milestones, live resources, key lessons), then the session log **newest
first**. Sessions from July 27 through August 7 — the completed M2–M6 build —
were split into `STATUS-archive-phase1.md` in this same folder. Sessions from
August 10 through September 16 (the M7 era) were split into
`STATUS-archive-m7.md` on 2026-09-24, moved verbatim.

**Two rules that keep it from decaying again.** (1) A session entry gets its
own `### Session — <date>` heading at the top of the log; it does not get
appended to `## Current next action`, which holds exactly one item — the
current one — and gets *replaced*, not extended. (2) Cross-references name a
date, never a direction: "the Aug 14 session notes", not "the notes above".
Direction words were already wrong in several places before this restructure,
because the file had drifted into three different orderings at once.

**Attribution -- read this before treating anything here as a work claim.**
This is a joint working log. The work it describes was done by Gerard and by
Claude (Anthropic's assistant), in proportions that varied task to task.
Where authorship is known it is named inline -- "Gerard drafted, Claude
critiqued", "Claude wrote the restructure at Gerard's request". **Where no
actor is named, that is not an authorship claim by either party.** Most of
this log is written in passive voice, and passive voice here means
*unrecorded*, not *Gerard's*. An audit on 2026-09-03 found 82 of 101
work-product passages in the Aug 28 - Sep 3 span carried no attributor at
all, including most of the analysis, the root-cause findings and the
architecture decisions. Those gaps are deliberately left unfilled:
reconstructing attribution after the fact is guesswork, and guessing in a
document that feeds a resume is worse than an honest silence.

**Going forward, attribution is written inline at the time the work is
logged, or not at all.** Where it is genuinely unclear, the entry credits
Claude rather than Gerard -- an under-credit costs nothing real, while an
over-credit in resume material can cost a great deal.

> **Restored 2026-09-10.** Everything from "which holds exactly one item"
> down to the end of the attribution rule above, plus the three pointers
> below and the `## Current next action` heading itself, was deleted by
> commit `aef3512` on 2026-09-08 — 37 lines, in a change whose purpose was
> only to replace the next-action content. Rule (1) was left cut off
> mid-sentence and the heading that marks the section boundary went with it,
> which is why nothing caught it for two days. Recovered verbatim from
> `git log -L 16,20:ai-103/STATUS.md`, not reconstructed from memory. The
> sentence destroyed was the one saying this section "gets *replaced*, not
> extended" — the replace operation ate the instruction describing itself.

Commands/CLI reference lives separately: `iip-cli-runbook.md` in this same
`ai-103/` folder — that page already works well as the "code samples"
reference and didn't need rebuilding.

Current-state map lives separately too: `m7-orientation.md` in this same
folder (added Aug 28) — a one-page "what does M7 look like right now, what's
built vs. designed vs. still open" snapshot, kept current on purpose. This
file stays the chronological log; that one is the "you are here" pointer.

A gotchas/tips-and-tricks page and a master index page (once there's enough
split across pages to justify one) are deferred until real material
accumulates for them — no point building empty structure now.

**Status as of:** October 15, 2026 (Oct 15: both "In short" sections
rewritten and reader follow-ups drafted; shared-key access switched off on
`stiipdevwus01`, see the Oct 15 session entry). Phase 1 of the IIP labs is closed: M7
passed its acceptance test at `a915217` (`results/20260915-184006`, 120/120 text
and 120/120 audit rows). Phase 2's M8, M9 and M10 are complete (Sep 21-23), and
M11 closed on Oct 7. M13 is nearly done: CA001 passed T1-T6 while On (Oct 9)
and the policies are exported; only the rollback (C9) remains, planned for the
week of Oct 26. M12 is complete (Oct 12). M14's three done-when items are all
shown (deploys and alerts on Oct 12, tracing on Oct 13), and the Phase 2
write-up is next. For
which milestone is current, read the marker at the top of
`phase2-orientation.md` — that line is the single source of truth. The M7
write-up waits on outside readers and goes out in one group push with the Phase
2 write-up.
*(Updated 2026-10-13, Claude: the Oct 10 text said M12's agent-isolation
write-up and its teardown "(by Oct 16)" remained. Both were done by Oct 12,
and the stale date had also been carried into Claude's suggested session
prompt.)*
*(Corrected 2026-09-30: this paragraph also listed "the two stale
ostebovik.net lines" for that push. Both were fixed on Sep 21 in `5fccd4a`,
per the Todoist write-up task's Sep 28 correction.)*
*(Replaced 2026-09-24, housecleaning — Claude drafted, at Gerard's request.
The previous paragraph was dated Sep 16 and predated M8-M10. Its M7 detail —
the item3 colour flaw moving from `[observed]` to `[content]`, 40/45 then
34/45 — is in the Sep 16 session entry and the Todoist task that accepts it as
a stated limit.)*
---

## Current next action

**Next action: outside readers for `phase2-writeup-draft.md`** (Gerard's
step). Replaced 2026-10-13. **Gerard's edit pass is DONE** (2026-10-13,
section by section, every change approved by him). His rules are recorded in
the draft's header: no Claude-only wrong turns, no clock times or day-level
dates, no operational details about the live tenant. **Don't re-ask:** the
shape, length, the AI-103 table rows, or the "After Phase 2" section. Still
open in the draft: M13's C9 closing line (week of Oct 26), then the joint push
with the M7 write-up. **Settled the same day (Gerard):** the M7 page now
matches Phase 2. Claude-only errors are cut, and the one Gerard helped catch
is kept, credited to him (header of `m7-writeup-draft.md`).

**Outside readers, updated 2026-10-15: 1 reply in; "In short" rewritten;
follow-ups drafted.** Recorded without names (the repo is public) in
`phase2-writeup-draft.md`'s header, "OUTSIDE READERS". Reader 1 (Oct 13):
"IIP" and "M8-M14" stopped him; the troubleshooting point didn't come across;
the admitted limits read as "believable"; he asked for the goal first, then a
diagram. **Decided (Gerard, Oct 15), replacing Oct 14's "wait for the other
four":** rewrite now and make the ask lighter. Two days in, the likelier
problem was the size of the first ask: 731 words plus five written answers
under a "2 minutes" subject line. Rewrite committed in `28a763f`: goal first,
no internal labels, diagram `images/in-short-stages.svg`; Part 1 258 → 213
words, Part 2 260 → 210. Follow-ups are Gmail reply drafts for Gerard to
send: the readers who haven't answered get Part 2's "In short" only, the
diagram and one question ("After a 30-second skim, what do you think this
project is?"); Reader 1 gets both rewrites and "did this fix what stopped
you?". **Unresolved:** Gmail's Sent folder holds 4 request emails to 3 people
(one at two addresses), while earlier entries say 5 requests. **Don't redo:**
the rewrite, the word counts, the diagram.

**M14 part 3 is DONE (2026-10-13), so all three M14 done-when items are shown.
Gerard ticks M14. Settled, don't re-check:**
- `function/tracing.py` is deployed (`8b4dce6`). A traced item4 upload
  matched the answer key, and its trace shows 61 spans under one operation,
  including the three tools by name (D-M14-7).
- Evidence: `evidence/m14-tracing/`.
- About 200 KB of ingestion per upload, of which the spans are 76 KB.
- The judge's model call isn't traced (it uses the `openai` package), so
  tracing doesn't settle the token undercount (`m14-prep.md`, Part 3).

**M14 part 2 is DONE (2026-10-12). Settled, don't re-check:** the budget
`Credits_low` emails Gerard's backup inbox with no action group (left as is,
Gerard); the alert is a log search alert on the poison line, every 15 minutes,
looking back 30; the address is in `IIP_ALERT_EMAIL` (persistent user
variable); proven by deliberate poisoned uploads that fired it (19:22:56Z and
20:37:57Z). **The alert-email fault is closed (2026-10-13):** the
troubleshooter showed the first 3 real notifications as "empty after
resolution", so no email was ever sent. After the action group was re-saved
(Oct 12, 14:27), a Resolved email (Oct 12) and a Fired email (Oct 13, 10:07)
both arrived (`m14-prep.md`, Part 2, "the delivery fault"). **Don't redo:**
the mailbox searches, the filter check, the receiver status, the OTP, or the
ARM-role cross-check (dropped, no longer needed).

**M14 part 1 is DONE (2026-10-12). Settled, don't re-check:** the federated
credential on `-02` (main branch only); the workflow deploys on a push and by
hand (`workflow_dispatch`); the activity log shows `-02` as the deployer; the
regression upload passed; basic auth is off and the OIDC deploy still works.
Register: **6 modify, 30 no change, 11 Unsupported, 2 to ignore**.

**M12 is COMPLETE (2026-10-12; Gerard ticked it). Already done and settled,
so don't re-check:**
- Evidence of the built state: `evidence/m12-networking/` (8 read-only JSON
  captures; home IP counted, never listed; subscription ID replaced).
- Teardown `m12-teardown-20261012`: Function detached (subnet ID read back
  empty), both endpoints, both zone links and both zones deleted; only
  `vnet-iip-dev-wus-01` and the 2 NSGs remain (D-M12-7).
- Regression upload: correct result in 44 s, first delivery.
- Final what-if: **6 modify, 27 no change, 11 Unsupported, 2 to ignore**,
  the register now. `networkStage` is **0**; the firewall is back to the M8
  values (Allow, bypass None, no IP rule).

**Every what-if and deploy of `main.bicep` still needs `IIP_HOME_IP`, at
every stage:** run `.\set-home-ip.ps1` once in each new PowerShell window
(Gerard's choice, Oct 10). At stage 0 the address isn't used by any rule, so
a changed home IP no longer causes 403s; it matters again only if stage 3 is
rebuilt.

**M13 is waiting only on C9, the rollback, planned for the week of
2026-10-26** (Gerard, Oct 9; Todoist). T1-T6 passed with CA001 On and the
policies are exported (Oct 9 session entry). C9 = delete CA001 and
CA900-CA903, then turn security defaults back on. Before that, the same
session: (a) check for Microsoft-managed policies (0 on Oct 8; if any exist,
test whether one that's Off blocks security defaults), (b) recurring billing
still Off, (c) decide what happens to RBAC row 10's group assignment when
P1/P2 lapses (untested). The marker stays on M13 until C9 is done.

**Carried** (details in Todoist):
- Pass 1 follow-ups: deployed-package provenance; the Flex instance-id field;
  trim the Azure SDK's HTTP logging (sized Oct 13: about 99 AppTraces rows,
  122 KB, per upload, larger than the trace itself; not yet checked against a
  pre-tracing run).
- ~~Gerard's steps: update the project instructions~~ Done 2026-10-12
  (Todoist; the instructions now carry every item that was listed here).
  **New Oct 15 (Gerard's step):** add "shared-key access OFF since
  2026-10-15" to the `stiipdevwus01` line.
- Small, any time: the `__main__`-guard refactor; `.gitattributes` for
  `.gitignore`; the token-undercount item; the `az-104` repo's uncommitted
  changes.
- ~~M12 (networking) has no clock; it starts while M13 waits on C9.~~ ~~M12 is
  the current next action (Oct 10).~~ M12 is complete (Oct 12).
- Oct 7 (Todoist): a USB FIDO2 key as `bg-admin-01`'s second method (p2);
  lock the two unlocked pay-as-you-go subscriptions (p4); re-run the inventory's
  service-principal sections once the beta report resumes.
- **New Oct 8 (Todoist):** delete `AzSvcAdmin@ostebovik.net` on Oct 22 if
  nothing complained; migrate off the **classic Foundry Agent Service APIs**
  before 2027-03-31 (Microsoft's notice, tracking ID HYJP-QGZ; first step due
  Dec 1).

**Open observation, not chased:** every host start on Sep 29 logged its
`QueuesOptions` trace **twice, about 30 s apart** (15:48:48/15:49:19Z and
16:40:20/16:40:50Z). A second instance (max is 2) or a restart of the first.
Harmless so far; the instance-id follow-up would tell them apart.

**Settled — do not reopen:**
- The `listKeys` calls are VS Code's.
- item7's judged row is a rate, flagged at 9 of 15.
- M3's `--blob` uses a user-delegation SAS.
- Trigger: Event Grid → queue, delivered with the topic's identity; row 14 at
  ACCOUNT scope (Event Grid checks the account when it creates a subscription).
- Sign-in: a managed identity as a federated credential.
- Python 3.14, remote build.
- `versionUpgradeOption` = `OnceCurrentVersionExpired`.
- One agent per upload; topic as blob metadata.
- Event Grid writes base64 JSON to the queue.
- **Row 16 works** (poison after `maxDequeueCount` 2; verified 2026-09-25).
- **Update Message needs `messages/write`**, which neither built-in in row 15
  has. Proven by a probe and a negative control, 2026-09-25.
- **Row 15 is one custom role, verified alone** (2026-09-29): failure path
  (retry +103 s, no 403, poison move) and scale-from-zero both passed.
- **Soft delete on `stiipdevwus01`:** blob and container, 7 days,
  `allowPermanentDelete: false` (Gerard, 2026-09-29).
- **Sign-in is secretless and works** (2026-09-30): the authorize request
  carries `response_type=code+id_token`, and the code is redeemed with
  `id-iip-dev-wus-03`'s federated assertion. **ID-token issuance must stay
  on**, because built-in authentication always asks for an ID token.
- **Global Administrators bypass "Assignment required"** (Microsoft's
  AADSTS50105 page). Test the gate with `iip-ca-test`, never with an admin.
- **Entra objects live in `entra.bicep`** (Graph Bicep types `1.0.0`: `owners`
  take plain IDs, and a federated credential's name is `parent/child`). They
  get no what-if, so they're verified by reading them back.
- **The `main.bicep` register is 6 modify, 32 no change, 11 Unsupported, 2 to
  ignore** (2026-10-12, after M14 part 2: the Sep 30 register's 6 / 24 / 11 /
  2, plus the VNet and 2 NSGs (M12 skeleton), the federated credential, the
  two basic-auth policies, the action group and the alert rule as No change).
  Confirmed by a what-if after the deploy.
- **Real alert emails are delivered** (2026-10-13: a deliberate re-fire, then
  the Fired email at 10:07). The portal's action-group Test is **not** proof of
  that: it skips the resolution step that failed on Oct 12. Prove a new
  action group with one real fire.
- **Every `main.bicep` what-if and deploy also needs `IIP_ALERT_EMAIL`**
  (2026-10-12, D-M14-5). Set once as a persistent user variable; a new window
  inherits it (unlike `IIP_HOME_IP`, which `set-home-ip.ps1` sets per window). `authsettingsV2` reports No
  change once deployed.
- **Row 10 is the group, as designed** (2026-10-07). `iip-ca-test` is its
  only member, declared in `entra.bicep` with **replace** semantics (Gerard):
  the template is the whole member list.
- **The P2 trial's recurring billing is Off by default** (Your products,
  2026-10-07, edit control greyed out). Nothing to switch off. Re-check once,
  on the Nov 2 Todoist reminder.
- **Gate tests need every Incognito window closed first.** Chrome shares one
  session across Incognito windows, so a leftover sign-in skips Entra.
- **The break-glass account exists and works** (2026-10-07):
  `bg-admin-01@letter7.onmicrosoft.com`, Global Administrator, passkey in
  Authenticator proven. Password on paper only; never in any file.
- **Passkey (FIDO2) is on for All users**: device-bound, attestation enforced,
  no key restrictions. The profile's edit pane shows Device-bound only; trust
  it over the list column, which said "Device-bound, Synced".
- **Authentication-policy changes take minutes to reach sign-in** (6-47 min on
  Oct 7). Wait before testing; a failure in the first minutes proves nothing.
- **Microsoft-managed CA policies don't exist while security defaults is on**
  (Microsoft Learn; the list was empty on Oct 7). Baseline = templates, by hand.
- **Bare-domain DNS is an ALIAS record** (Gerard, 2026-10-06, option A). Its
  Front Door certificate no longer auto-renews: a monthly Todoist task checks
  for "Pending Revalidation". Current cert expires 2027-03-18.
- **Security defaults is OFF; the baseline CA900-CA903 is ON** (2026-10-08,
  11:14 Phoenix), each excluding `bg-admin-01` only. Verified by What If and by
  real sign-ins for `djeemunee`, `bg-admin-01` and `iip-ca-test`.
- **Authentication methods: Migration Complete** (2026-10-08). On: Passkey
  (FIDO2), Microsoft Authenticator (All users, Any, OTP Yes), Email OTP. SMS and
  Voice stay off. The legacy per-user MFA settings no longer apply.
- **A CA template excludes the person who creates it**, and only them. Fix the
  exclusions on every template-built policy (2026-10-08).
- **CA policies can be created in Report-only while security defaults is on**;
  only On is blocked (2026-10-08).
- **`AzSvcAdmin@ostebovik.net`**: all four Azure roles removed, sign-in
  blocked, sessions revoked (2026-10-08). Its only use was an Edge profile on
  the home network. Delete on Oct 22 if quiet (Todoist).
- **CA001 has no "Never persistent" control** (Gerard, C5 amended
  2026-10-08): that control needs a policy targeting All cloud apps. CA001
  keeps the 8-hour sign-in frequency.
- **`iip-ca-test`'s passkey is in Authenticator on the phone** (2026-10-08).
  Passkey tests run in the phone's Chrome: the tower has no Bluetooth, and
  Edge on Android doesn't do same-device passkey sign-in yet.
- **CA001 On passes T1-T6** (2026-10-09). With CA001 applying, Entra offers
  **only the passkey** after the password; the Authenticator push is never
  shown. The Function's identity is unaffected (T6 result).
- **The CA policies are exported** to `evidence/m13-conditional-access/`
  (2026-10-09); the IDs in them were confirmed by name.
- **Chrome on Android blocks screenshots in Incognito.** The sign-in log is
  the record for phone tests.
- **M12: no NAT gateway is needed** (2026-10-09). The Function, inside the VNet
  on a subnet with `defaultOutboundAccess: false`, still reaches Foundry, Entra
  and its host storage (stage 2 upload test).
- **`stiipdevwus01` is reachable over IPv4 only** (`A` record, no `AAAA`), so
  storage firewall rules are IPv4 (2026-10-09).
- **M12 stage 3's firewall works** (2026-10-10): Deny, the home IPv4,
  `bypass: AzureServices`. The Function reaches `stiipdevwus01` only through
  the private endpoints; Event Grid still delivers to the queue; Cloud Shell
  is refused.
- **M3 `--blob` can't work while the firewall is on** (2026-10-10):
  Content Understanding fetches the SAS link from Microsoft's network
  (`ContentSourceNotAccessible`). Use `--file`.
- **Cloud Shell means Azure Cloud Shell** (shell.azure.com), not a Bash window
  on the tower. Check its outbound IP before trusting a network test.
- **`publicNetworkAccess: 'Enabled'` is declared at every stage**
  (2026-10-10): unset behaves the same, and `union()` would have switched off
  Bicep's type checking.
- **Device file writes: always from a fresh staging name, then read back.**
  On Oct 9, re-using a staging path left STATUS.md with old content twice,
  while the write reported success; the read-back caught both. **Oct 12, a
  second way to fail:** an edit and the copy to the tower sent at the same
  time, so the tower got the pre-edit file. Never edit and copy in parallel.
- **A stage-0 deploy does not detach the Function from the VNet**
  (2026-10-12): `virtualNetworkSubnetId: null` leaves the property out of the
  request. Detach by CLI (`m12-prep.md`, section 5).
- **Flex Consumption's `outboundVnetRouting` reads all `false`, and that's
  expected** (Microsoft Learn: on Flex, all traffic already goes through the
  VNet). Not a misconfiguration (`evidence/m12-networking/README.md`).
- **Basic publishing credentials are OFF on the Function** (2026-10-12,
  `app.bicep`). They were on by ARM's default, which put a password in the
  publish profile. Deploys use Entra tokens only (OIDC workflow,
  `config-zip`).
- **A stateful log alert at a 15-minute frequency resolves only after 45
  quiet minutes** (3 periods; Learn, "Alerts and state"), counted from when
  the line leaves the 30-minute look-back. While it's Fired, a new match sends
  nothing. It emails again when it resolves.
- **In PowerShell, `az rest` URLs must not contain `&`**: `az` is a `.cmd`, so
  `cmd` splits the line there (and drops `--query` with it). Pass query
  parameters with `--url-parameters` (2026-10-12).
- **Action group email receivers need a one-time passcode** within 30 minutes
  of saving the group (Learn); verified once per address, tenant-wide.
- **A missing `topic` does NOT fail an upload**: the handler writes an error
  result and returns, so there's no retry and no poison (by design). To force
  the poison path: pause `process_upload`, upload, delete the blob, un-pause
  (Sep 29's method; `m14-prep.md`, Part 2).
- **Workflow files can't be written by the remote tools** (`.github/workflows`
  is protected). Claude leaves the file in the working folder; Gerard copies it
  into place.
- **An ARM deploy can log a second `sites/write` "Succeeded" about 10 minutes
  later, with the same correlation ID** (2026-10-12, seen twice). It's the
  same deploy finishing, not a new action. Check the correlation ID before
  chasing one.
- **The Sunday punch-list task is cloud-only** (2026-10-12, Gerard). It needs
  no computer: it clones the repo and reads Todoist. Don't tie it to a device
  again.
- **Key authentication is OFF on `aif-dev-wus-01`** (2026-10-14,
  `p2-keysoff-20261014`; `disableLocalAuth: true` in `foundry.bicep`). A key
  is refused with **403** `AuthenticationTypeDisabled` (not 401 as Learn says),
  and `listKeys` fails with BadRequest. Entra ID sign-in is proven by a
  regression upload and `probe_keyless_smoke.py` 9/9. **Don't re-test.** The
  register is unchanged: 6 modify, 32 no change, 11 Unsupported, 2 to ignore.
  Record: `infrastructure/iip/README.md`, "Keys off".
- **Shared-key access is OFF on `stiipdevwus01`** (2026-10-15,
  `p2-sharedkeyoff-20261015`; `allowSharedKeyAccess: false` and
  `defaultToOAuthAuthentication: true` in `storage.bicep`). A key is refused
  with 403 `KeyBasedAuthenticationNotPermitted`. Proven without it: a
  regression upload (first delivery), a user delegation SAS (HTTP 200), and
  Bicep deploys and what-ifs. **Don't re-test.** The register is unchanged:
  6 modify, 32 no change, 11 Unsupported, 2 to ignore. Record:
  `infrastructure/iip/README.md`, "Shared key off".
- **An "AccountKey" count in this account's metrics doesn't mean a client has
  the key** (2026-10-15). Azure's own deploy and what-if calls are labelled
  AccountKey (and SAS) and still succeed with the key off (trusted access).
  Split by `ApiName` and `ResponseType` first.
- **`az monitor metrics list` returns only the top 10 dimension values by
  default.** Pass `--top 50` whenever a query splits by a dimension
  (2026-10-15: two tables silently lost rows).
- **Public repo rule** (Gerard, 2026-10-14): the repo and the site are public,
  so no tracked file or site page names the subscription's offer type, its
  billing details or its full ID. Say "the lab subscription" and "cost
  controls". The details live in Todoist and in
  `docs/MASTER-REFERENCE.md` (gitignored). Git history still holds the old
  text; rewriting history was not chosen.
- **Device file writes, a third way to fail** (2026-10-14): one of three files
  in a single commit call came back unchanged, although the call reported it
  written. The staging path had never been used before, so a fresh path alone
  doesn't prevent it. Read back every file, every time. Retry from a new
  unique name.

Still open and unchanged: the M7 write-up waits on outside readers (Gerard's
step), and goes out in one group push with the Phase 2 write-up.

## Milestones (Phase 1)

- [x] **M0:** Tear down West US 3 RG and all resources — zero carryover. Complete.
- [x] **M1:** Redeploy Foundry fresh in West US, quota re-verified. Complete (July 23, 2026).
- [x] **M2:** Custom document analyzer (`iip_loan_agreement_analyzer`) built and validated
  against the clean-PDF loan agreement. Complete (rebuilt July 23, 2026 after a
  collateral-damage purge; original build dated July 17/20).
- [x] **M3:** `m3_analyze.py` (submit-and-poll pipeline) written, fixed, and validated
  end-to-end. **Complete July 27, 2026.**
- [x] **M4:** Extraction validated across all 3 image conditions (clean PDF, flatbed
  scan, angled photo). **Complete July 27, 2026.**
- [x] **M5:** RAG-grounded Q&A working (real vector search/index, not context-stuffing).
  **Complete (Aug 20).** `m5_index.py` (chunking, Search index creation,
  embedding, upload) built and verified end-to-end Aug 18 — 16/16 chunks
  embedded and indexed. `m5_retrieve.py` (embed query → vector search →
  assemble context from *all* retrieved chunks, not just the top-ranked
  one → grounded chat completion) built and verified end-to-end Aug
  19-20 — real live run against `loan-agreement-index`, correct answer
  ($50,000.00) despite the top-ranked chunk being the wrong one, proving
  the `top_k≥2`/join-all-chunks design actually does what it was meant
  to. Full detail, including two live-only bugs caught before the first
  run and a real retrieval-ranking finding, in the Aug 19/Aug 20 session
  notes. One deliberate, non-blocking scope item left open: the
  test question is still hardcoded, generalizing to a CLI arg deferred
  per `main()`'s own docstring plan until a clean run happened — which
  it now has.
- [x] **M6:** Evaluator harness built, used to pick GPT-5.4 vs. GPT-5.4-mini for M5.
  **Complete (Aug 6).** Full pipeline (`m6_generate.py` → `m6_assemble.py` →
  `m6_evaluate.py`) built, debugged, and run twice — once against the original
  10-question rubric (Aug 5), once against a 14-question set stress-tested with
  4 harder questions probing cross-clause reasoning, arithmetic synthesis, and
  abstention (Aug 6). Decision: **`gpt-5-4-mini`**, on confirmed quality parity
  across both runs plus a real ~3x per-token cost advantage. Full evidence
  trail, including a real cross-session reproducibility finding that overturned
  the Aug 5 run's apparent `gpt-5-4` edge, in the Aug 6 session notes
  (`STATUS-archive-phase1.md`).
  Small infra items remain (see Next action) but don't block M5.
- [x] **M7:** Build a single orchestrator agent (Generative AI/agentic exam
  domain) over a neutral, synthetic small-business content-review scenario —
  decoupled from the YouTube-cleanup business thesis as of August 4, see
  `agent-system-project-plan.md`'s "Decoupling note." Same technical shape
  as originally planned: drafts content against a template, reuses M6's
  evaluation-harness pattern (Groundedness/Relevance/F1) to QA drafted
  output against grounding data, and adds a computer-vision module
  (thumbnail-style brand/legibility/info-accuracy audit) — the one AI-103
  exam domain not otherwise touched through M6. No longer tied to Anne's
  engagement or any specific unvalidated business premise; "is this a real
  business" is now a separate, evidence-gated question, not assumed live.
  **Complete: acceptance test passed at `a915217`** (`results/20260915-184006`,
  120/120 text rows, 120/120 audit rows). Phase 1 of the IIP labs is closed.
  *(Updated 2026-09-24, housecleaning: until today this entry still read "Not
  built yet", unticked, from Aug 21.)*

---

## Key resources (current, live)

| Item | Value |
|---|---|
| Resource Group | `rg-iip-dev-wus-01` (West US) |
| Foundry account | `aif-dev-wus-01` (custom subdomain `aif-iip-dev-wus-01`) |
| Foundry project | `proj-iip-dev-wus-01` |
| Storage account | `stiipdevwus01` |
| Sample doc location | container `docs`, blob `loan-agreement-promissory-note.pdf` |
| Key Vault | `kv-iip-dev-wus-01` |
| Chat deployments | `gpt-5-2` (Content Understanding analyzer; 30K TPM) · **`gpt-5-4-mini` — decided M5 RAG/Q&A model** (Aug 6: quality parity + ~3x cost advantage over `gpt-5-4`, full evidence in the Aug 6 session notes, `STATUS-archive-phase1.md`); M7's CV audit model; 300K TPM · `gpt-5-4` — not chosen for M5, but M7's orchestrator and judge (Sep 9); 300K TPM. All GlobalStandard. TPM raised from 30K on 2026-09-16 |
| Embedding deployment | `text-embedding-3-small` |
| Analyzer | `iip_loan_agreement_analyzer` (`ai-103/infrastructure/content-understanding/loan-agreement-analyzer.json`) |
| AI Search service | `srch-iip-dev-wus-01` (Free tier, West US) — `https://srch-iip-dev-wus-01.search.windows.net`, provisioned Aug 7 for M5 |
| Managed identities | `id-iip-dev-wus-01` (Function runtime) and `id-iip-dev-wus-02` (GitHub Actions deploy, OIDC) — deployed by M9, 2026-09-21. `id-iip-dev-wus-03` (sign-in federated credential, D-M11-2 (b)) is planned, not deployed |
| App data containers | `uploads` and `results` on `stiipdevwus01` — deployed by M9, 2026-09-21 |

---

## Key Lessons

**`az role assignment list -o table`'s Principal column is NOT the principal
ID** (added 2026-09-22). For a *user* it prints the UPN — obviously not an ID,
so nobody transcribes it. For a **managed identity** it prints the **appId**, a
bare GUID that looks exactly like a principal ID and is not one. The one case
where the value is wrong is the one case where it is plausible. Query
`principalId` explicitly:
`--query "[].{principalId:principalId, role:roleDefinitionName}"`.
Verified on `aif-dev-wus-01`: `id-iip-dev-wus-01` is principal
`3b6695b3-f1d7-40f9-b21a-5158e6f71739` (shown as `efc6dd4a-…`);
`proj-iip-dev-wus-01` is `39bed562-c0ca-4acb-9d18-8400e806b824` (shown as
`98ee20de-…`).

**Cognitive Services User is a LEGACY role; Foundry User supersedes it** (added
2026-09-22). The Image Analysis / Vision docs still name Cognitive Services
User as the Entra prerequisite. Microsoft Learn's current Foundry RBAC page
lists it as "legacy Azure AI Services role" and Foundry User as the
Foundry-native replacement. Reaching for it assigns a deprecated role.

**Foundry RBAC role NAMES are mid-rename — key on the GUID** (added
2026-09-22). Foundry User / Owner / Account Owner / Project Manager were
previously Azure AI User / Owner / Account Owner / Project Manager. Microsoft's
own guidance is to use the role definition ID in code while the rename rolls
out. Foundry User = `53ca6127-db72-4b80-b1b0-d745d6d5456d`. Role IDs and
permissions are unchanged by the rename; only the display name moves.

**Keyless code is not the same as keys being unavailable** (added 2026-09-22).
Foundry User's `actions` include
`Microsoft.CognitiveServices/accounts/listkeys/action`, and its `dataActions`
are the wildcard `Microsoft.CognitiveServices/*`. An identity granted Foundry
User *in order to stop using keys* can still retrieve them. `disableLocalAuth`
is the control that closes it.

**Azure AI Search free tier: inbound Entra auth works, outbound managed
identity does not** (added 2026-09-22). Learn contradicts itself across five
pages. Measured: a `SearchClient` query with `DefaultAzureCredential` succeeds
on the free tier with Search Index Data Reader assigned. The "billable tier"
prerequisite applies to the *service* holding a managed identity (for indexers
reaching storage), not to clients authenticating to it.

**An RBAC test with no role assigned is not a test of anything else** (added
2026-09-22). 403 means "identity lacks the role" (up to 10 min to propagate);
401 means "RBAC not enabled on the service". A probe designed to answer "does
this tier support keyless?" returns 403 when the answer is really "you have no
role", and that misreading pointed at a paid-tier service recreate. Assign the
role, wait, then measure.

**`AzureOpenAIModelConfiguration` accepts keys its validator rejects** (added
2026-09-22). Introspection shows `credential` among its accepted fields;
passing it fails with `Model config validation failed` (MISSING_FIELD /
USER_ERROR). The working keyless form is to **omit `api_key`**. Accepting a
field and validating it are not the same thing, and introspection cannot tell
you which you have.


**This is a lookup, not a manual.** Azure/infra/git-specific gotchas live
here; general Python language patterns (control flow, data structures,
stray imports) live in `python-patterns.md` instead, so the two don't
overlap — same split `python-patterns.md`'s own header already describes.
Referenced from the Aug 7 and Aug 10 session notes as if it already
existed; it didn't. Created Aug 11 to close that gap.

### `FunctionTool` truncates every tool description at the first newline

Found 2026-09-07 by introspecting the schema `FunctionTool` actually generates,
after a new tool's description came back cut mid-sentence. It applies to the
function description **and to every `:param:` description**, and it is silent —
nothing errors, the tool still works, and the model simply receives a fragment.

Before the fix, this is what the model saw for two tools that had been treated
all along as carefully specified:

```
evaluate_draft
  description: "Evaluate a drafted video title and description for Riverside Hardware &"
  query:       "The drafting instruction the text was written to"
  response:    "The drafted text to evaluate, title and"
```

One description ends on an ampersand. The `query` guidance — "Do not pass a
bare topic: RelevanceEvaluator grades the response as an answer to this, and a
bare title scores as an unanswered question" — **never reached the model at
all**, which is why the agent improvised a different `query` per item on Sep 4
and Sep 7 rather than following it.

**The rule: the entire description must sit on one physical line, and so must
each `:param:` description**, however that reads in source. Prose below the
first line is for human readers only. Both tool modules now carry a note saying
so, so the next person to reformat them does not silently undo it.

**This qualifies the Sep 4 claim that "the reST docstrings functioned as tool
schemas on the first attempt."** They functioned in the weak sense: the model
received tool names and a truncated fragment, and got the calls right anyway.
That is a weaker result than it was recorded as.

### `run_az()` — the subprocess wrapper every script's Azure calls go through

**What it does:** takes a list of CLI arguments (e.g. `["cognitiveservices",
"account", "keys", "list", "--name", account, ...]`), prepends the resolved
`az` executable path, appends `-o tsv`, and runs the result via
`subprocess.run()`. Returns stripped stdout as a plain string; raises
`RuntimeError` with the real stderr on nonzero exit.

**Why args are a list, not a shell string:** `subprocess.run()` with a list
bypasses shell parsing entirely — each flag and its value must be a
separate list element (`"--name", account`, not `"--name " + account` or an
f-string). Side benefit: no shell-injection risk from a resource name
containing spaces or special characters, since nothing passes through a
shell.

**Windows-specific gotcha, already hit once (July 27):** `az` installs as
`az.cmd` on Windows. `subprocess.run(["az", ...])` with the default
`shell=False` calls `CreateProcess` directly, which doesn't resolve `.cmd`
via `PATHEXT` the way an interactive shell does — fails with
`FileNotFoundError: [WinError 2]`. Fixed by resolving the executable
explicitly via `shutil.which("az")` first, then passing that resolved path
into `subprocess.run()`.

**Convention this enables:** every credential (`get_subscription_key()`,
`get_storage_key()`, `get_search_admin_key()`, etc.) is fetched live
through this one function on every run and never written to disk or
cached — the "live-fetch-never-persist" pattern used throughout
`m3_analyze.py` and `m5_index.py`.

**`--query` shape varies by command family, not just by convenience:**
`cognitiveservices account keys list` and `search admin-key show` both
return flat objects (`--query key1` / `--query primaryKey`), but `storage
account keys list` returns a *list* of `{keyName, value}` objects (`--query
[0].value`). Same-sounding command families don't share flag names or
response shapes — check the actual command's real output shape each time,
don't assume it matches a sibling command. Same species of mistake as
`get_search_admin_key()`'s `--name` vs. `--service-name` bug, caught and
fixed Aug 11.

### Azure AI Search's push API is eventually consistent for counts/stats

**What happens:** `SearchClient.upload_documents()` returning
`succeeded=True` for every document means the service accepted the
writes — it does not mean every read path reflects them yet.
`get_document_count()` in particular can report a stale (lower, even
zero) number for a few seconds after a successful upload. Microsoft
describes the push API as "closest to real-time," not instantaneous;
there's no published guaranteed latency, and an open Azure SDK for
Python GitHub issue (#40644) reports the identical symptom — a stale
count immediately after a push write, worked around with a manual
`time.sleep()`.

**Why it's easy to misdiagnose as a bug:** the per-item upload result
(the authoritative signal that a write was accepted) and the aggregate
count (a separately-consistent read) can genuinely disagree for a short
window even when nothing is wrong. A verification check written to run
once, immediately after upload, will intermittently report a false
failure — indistinguishable at a glance from a real one.

**Fix used here:** `main()`'s closing verification (`m5_index.py`) is a
bounded, tolerant loop — recheck `get_document_count()` a few times
with a short pause between attempts (`while True:` / `break` on match or
timeout), rather than a single immediate check. A single retry with a
fixed sleep would also work; the loop just avoids hardcoding a specific
wait time that isn't documented anywhere as sufficient.

**Real instance:** `m5_index.py`'s `main()`, Aug 18 — first end-to-end
run reported `Indexed: 0 documents` immediately after `upload_chunks()`
confirmed all 16 succeeded. Confirmed as lag, not a real failure, via a
standalone recheck a few seconds later (returned 16) before any code was
changed.

### Classic `AzureOpenAI` client vs. v1 GA `OpenAI` + `base_url`

**What happens:** `AzureOpenAI(azure_endpoint=..., api_key=..., api_version=...)`
404s against a deployment (embeddings, here) no matter which `api_version`
string gets passed — including `"v1"`, which looks like it should be the
fix and isn't.

**Why:** `api_version` is a real, required parameter on the classic
client, but `"v1"`/`"preview"` were never valid values for it. Azure's v1
GA surface is a structurally different API contract, not a new version
string on the old one — it requires the plain `OpenAI` client (the same
class used against the public OpenAI API) pointed at
`base_url=f"{endpoint}/openai/v1/"`, with `api_version` dropped from the
constructor entirely, since the parameter doesn't exist on this class.

**Where this showed up:** `m5_index.py`'s `build_embedding_client()` —
found and root-caused against Microsoft's own v1 GA migration guidance
Aug 11, rebuilt and verified live (1536-dim vector returned) Aug 12.

**Habit worth building:** if changing an `api_version` value doesn't fix a
404 no matter what's tried, stop guessing at values — check whether the
API surface itself expects a structurally different client, not just a
different string passed to the one already in hand.

### Vector search's top-1 result is not guaranteed to be the right chunk

**What happens:** a single vector-search query can return its closest
match by cosine score with the actually-relevant chunk ranked second (or
lower) and a superficially-similar-but-substantively-wrong chunk ranked
first — sometimes by a very thin margin. Nothing errors; the search
"succeeds" and returns a real, valid top-1 result, it's just not the
chunk that answers the question.

**Why it's easy to miss:** a manual spot-check that only looks at
`results[0]` (the natural first instinct — "here's the top hit, is it
right?") can look convincingly wrong even when the retrieval step is
functioning exactly as designed. The fix isn't in `search_chunks()`
itself; it's in not asking a single top-1 result to carry more certainty
than vector similarity actually provides.

**Real instance:** `search_chunks()` (`m5_retrieve.py`), first live test,
Aug 20 — query "What is the loan amount?" ranked `III. SECURITY.`
("The loan is unsecured.") first (score 0.6589), with `I. THE PARTIES.`
(contains the actual $50,000.00 figure) second at 0.6501 — a 0.009 gap.
`II. PAYMENTS.` (also genuinely relevant — monthly payment amount)
ranked third at 0.6323. All three came back within `top_k=3`.

**Why this isn't a bug to fix:** the Aug 7 M5 design note deliberately
set `top_k≥2` for exactly this reason, before `search_chunks()` was
written — "top-1 would structurally guarantee the same miss rather than
test whether chunked retrieval does better or worse on it." This test
run is that reasoning confirmed against a real query, not a hypothetical
one: retrieval with `top_k=3` still surfaced both relevant chunks despite
neither ranking first.

**Habit worth building:** when spot-checking retrieval quality, always
look at the full returned set for the configured `top_k`, not just the
top-ranked result — a "wrong" top-1 doesn't mean retrieval failed if the
right chunk still made the cut lower down. Downstream, this is also the
reason `build_context()` should join *all* retrieved chunks into the
prompt, not just the highest-scored one — the chat model gets a chance to
pick the right fact out of several candidates, the same job humans do
scanning a page of search results.

---

## Session log

Newest first. Cross-references name the date of the entry they point at,
not a direction ("above"/"below") — those went stale the moment this file
was reordered, and several were already wrong before it was.

### Session — October 15, 2026 — "In short" rewritten for outside readers; shared-key access off on `stiipdevwus01`

**Attribution:** Claude read the request email in Gerard's Gmail (via the
browser) and measured it, drafted both rewrites, the diagram, the follow-up
emails (left as Gmail drafts), the Bicep change, every command and these doc
edits. Gerard made every decision below and ran every Azure command. Times are
UTC unless marked.

**Outside readers.** Two days after the requests, 1 reply. Claude's read: the
ask was bigger than its subject line. The email was 731 words (about 3.1
minutes of reading at 238 words a minute) plus five written answers, under
"Quick favor: 2 minutes". **Decided (Gerard):** rewrite now and send a
lighter ask, rather than wait for all four replies (replaces the Oct 14
decision). Committed in `28a763f`: both "In short" sections goal first, no
internal labels, and the diagram `images/in-short-stages.svg`. Follow-ups
are Gmail reply drafts for Gerard to send (Part 2 only plus one question for
the readers who haven't answered; both rewrites for Reader 1). Record:
`phase2-writeup-draft.md`'s header, "OUTSIDE READERS".

**Shared key off (Gerard's pick from the backlog).** Full record:
`infrastructure/iip/README.md`, "Shared key off".
1. Measured before changing anything (metric `Transactions` by
   `Authentication`, Sep 15 - Oct 15): OAuth 179,157; AccountKey 415;
   Anonymous 197; SAS 39; DelegationSAS 3.
2. The AccountKey and SAS traffic was Azure's own Bicep deploy and what-if
   calls (container, queue and blob-service operations, deploy days only).
   3 of the 415 fall outside that pattern: GetFileServiceProperties 2,
   ListContainers 1. Oct 5 (9) has no session entry and wasn't traced.
3. The key worked before (container list). What-if 7 / 31 / 11 / 2, as
   predicted. Deployed `p2-sharedkeyoff-20261015`; read back False / True.
4. The key is refused: 403 `KeyBasedAuthenticationNotPermitted`.
5. Regression upload → item4's answer key, first delivery
   (`scripts/results/20261015-171118_function_item4_sharedkeyoff.json`). A
   user delegation SAS still reads a blob (HTTP 200).
6. After the change, the deploy's and a what-if's own calls still succeeded
   while labelled AccountKey: trusted access, as Learn describes.
   Post-deploy what-if: 6 / 32 / 11 / 2, the register unchanged.

**Claude's errors, caught the same session:**
- Predicted that a user delegation SAS would count as "SAS". The metric has a
  separate `DelegationSAS` value.
- Step 2's stop rule ("writes on days you didn't upload by hand") didn't
  allow for deploy days, so it fired on Azure's own traffic.
- `az monitor metrics list` returns the top 10 dimension values by default.
  Two tables lost rows until re-run with `--top 50`.
- Predicted the DelegationSAS counts would be one per `m3_analyze` run. The
  days match the runs; the counts don't, because the metric counts requests.

**Working format, set by Gerard today:** steps come in batches that run up to
the first gate. A message ends at the first step whose result decides what
comes next. Results go in `D:\claude\iip\<date>-results.txt`, and Gerard
types "done" so Claude reads the file.

**Also today:** the D: drive move is deferred until pywalk Lesson 5, so
Gerard's own script checks the copy (Gerard; Todoist updated, with the
note that its paths were read on serenity).

**Still open:** key access on AI Search (its own decision and test).

### Session — October 14, 2026 — outside reader 1 of 5 back; key authentication off on the Foundry account

**Attribution:** Claude read the reviewer's reply (in Gerard's Gmail, via the
browser), recorded it, searched the code for key use, wrote the Bicep change,
every command and these doc edits. Gerard made the decisions below and ran
every Azure command. Times are Phoenix (UTC-7) unless marked Z.

**Outside readers.** Gerard emailed five people on Oct 13 with only the two
"In short" sections and five questions. One reply is in. It's recorded without
a name in `phase2-writeup-draft.md`'s header ("OUTSIDE READERS"), because the
repo is public. The useful parts:
- "IIP" and "M8-M14" stopped him. They are internal labels neither page
  defines.
- The troubleshooting point didn't come across.
- Admitting the limits read as "believable".
- He asked for the goal first, then a diagram.

**Decided (Gerard):** record it anonymously, and don't rewrite "In short"
until the other four replies are in. Then rewrite it goal first, with no
internal labels and a diagram, and send the rewrite back to the same reader.
**Also found (Claude):** a stray drafting sentence at the end of case study 1's
"Root cause" ("Unable to verify this message through Microsoft Learn
documentation."). It was not in what the readers saw. It's listed in the
draft's header for Gerard's OK to remove.

**Keys off (Gerard's pick from the backlog).** Full record:
`infrastructure/iip/README.md`, "Keys off".
1. Connections on the account and the project: `[]` and `[]`.
2. A key fetched before the change: HTTP 200.
3. What-if: 6 / 32 / 11 / 2, the register unchanged. Deployed as
   `p2-keysoff-20261014`; read back `true`.
4. The same key: **HTTP 403**, `AuthenticationTypeDisabled`. **Gerard stopped
   here**, because Claude's step had predicted 401 (from Learn's page) and
   named no other outcome. Claude checked: Microsoft Q&A shows 403
   `AuthenticationTypeDisabled` is the real response to a disabled key, and
   the error text confirmed it.
5. `listKeys`: `(BadRequest) Failed to list key. disableLocalAuth is set to be
   true`.
6. Regression upload `item4-keysoff-20261014.png` → item4's answer key, first
   delivery (`scripts/results/20261014-171536_function_item4_keysoff.json`).
   `probe_keyless_smoke.py`: 9/9.

Write-up updated to match: case study 5's "Status" became "Fix", and the
"Known limits" and "After Phase 2" bullets were removed. "In short" was left
alone. Phase 2 Backlog item struck through; Todoist task completed.

**Working-format rule, set by Gerard after it cost about an hour today:**
every step Claude gives is laid out as **Step N: the command, Expected,
Give result, Stop if, Notes**, with all the steps in one message. Not one
step per message, not commands followed by a separate list of asks, and no
prose mixed into the steps. Every possible result Claude knows of goes under
Expected, or the step says it's unsure.

**Still open:** storage-account shared-key access (`allowSharedKeyAccess` on
`stiipdevwus01`) and AI Search key access. Each is its own decision and test.

**Also today:**
- The stray drafting sentence in case study 1 was removed (Gerard approved).
- **ostebovik.net (Gerard picked it; Claude wrote it):** the planned homepage
  menu fix and link previews were already done and live, so the Todoist note
  was out of date. Instead, 4 dead-end pages now link back to the site: the
  Phase 2, 3 and 4 guides (header links to home and to their section) and
  PowerShell vs Bash (a link to Resources at the top and bottom). Rendered at
  360, 390 and 1280px with no overflow.
- **Portal Steps (found by Gerard on his phone):** in all 3 guides each step
  row was laid out as columns (`display: flex`), so text was cut off on
  phones, and on desktop in Phase 3 and 4. Fixed with CSS only (`ccffe72`).
  Test of all 92 steps at 360, 390 and 1280px: 0 clipped. **Lesson
  (Claude's):** the first test only checked whether the page scrolled
  sideways, not whether content was cut off inside a box. Test for both.
- **PowerShell vs Bash** was 848px wide on a phone (its two tables, plus the
  pipeline cards at 360px). Below 700px the table rows now stack as cards,
  with each code cell labelled PowerShell or Bash. Fits at 360 and 390px.
  Desktop is pixel-identical to before.
- **Current page's menu link** kept in view on phones: new `js/nav.js` on the
  8 pages with an active link (`771d139`). Before: off-screen on 6 of 8 at
  390px. After: in view on 8 of 8.
- **Opened project cards on all 5 section pages cut text off on phones.** The
  card's grid column (`1fr`) couldn't shrink below its widest code line or
  table, so paragraphs were laid out up to 631px wide inside a 268px card.
  Fixed in the shared `css/mobile.css` (`minmax(0, 1fr)`, plus wrapping for
  long code words and hostnames, and a screenshot grid that fits a 360px
  phone). Text past the screen edge went from 13-32 lines per page to 0, at
  360 and 390px, every card opened. Desktop is untouched (all rules are
  inside `max-width: 700px`).
- **Claude's test error, caught the same afternoon:** a finding logged earlier
  ("IaC and Networking are 475/411px wide on a phone") was false. The sandbox
  can't reach Google Fonts, so the title rendered in a much wider fallback
  font. With the real fonts (Fontsource packages from npm) both pages fit.
  **Rule for site tests from now on:** load the real fonts first, and open
  every card.
- **Found, not fixed (Todoist):** the compute comparison reference is 515px
  wide on a phone, and one table in the Phase 4 guide is cut off.
- **Subscription offer details taken out of the public repo and site**
  (Gerard asked; Claude searched and reworded). A search of 177 tracked text
  files found them in 2 live pages (the offer type in a scope label on
  Identity & Governance; the full ID in the Phase 4 guide's bootstrap script,
  now `"<your-subscription-id>"`), an offer-specific line on Compute &
  Storage, and 7 docs (billing details). All reworded. Kept
  on purpose: the truncated `343a8a7e-...` on the IaC page, its Project 11
  write-up and the RBAC model (an 8-character prefix that names no offer).
  Git history is unchanged (Gerard's choice). The rule is under "Settled".

### Session — October 13, 2026 — M14 done-when complete: alert-email fault closed, tracing built and shown

**Attribution:** Claude read the evidence, wrote every command, the log
queries and test image (kept outside the repo, in `D:\claude\iip`),
`function/tracing.py` and its wiring, the offline tests and these doc edits.
Gerard made the decisions marked below, ran every Azure command, git command
and install, and checked the inbox and the alert history. Times are Phoenix
(UTC-7) unless marked Z.

**Overnight:** no Fired email arrived, and the alert history showed nothing
after 13:37 on Oct 12 (Gerard).

**Found (Claude, from a log query Gerard ran): Oct 12's last re-fire never
poisoned anything, so the alert had nothing to fire on.** The cause was two of
Claude's errors:
1. The test file was a `.txt`, which the handler skips (Succeeded,
   22:05:46Z).
2. The pause hadn't reached the running host: a host started at 22:05:45Z and
   took the message 1 second later.
Both queues confirmed it: `upload-events` was empty, and the poison queue held
only Oct 12's two test messages.

**Re-fire, done right** (`m14-prep.md`, Part 2, "the method now"): paused,
waited 5 minutes, uploaded a 1-pixel `.png`, then peeked at 09:53 and 09:56
(still there, `dequeueCount` 0 both times). Deleted the blob, un-paused at
09:57. The message was poisoned at 16:59:35Z, the alert **fired at 10:07**,
and the **Fired email arrived by 10:09**.

**Closed:** the Todoist alert-email item. 0 of 3 notifications were delivered
before the action group was re-saved, and 2 of 2 after. The re-save can't be
separated from the time that passed (`m14-prep.md`). The ARM-role cross-check
was dropped.

**Also corrected:** the status paragraph's "teardown (by Oct 16)". The
teardown was done on Oct 12, and Claude had carried the date into its
suggested session prompt.

**Lesson:** pass KQL to the CLI from a file
(`az monitor log-analytics query -w $ws --analytics-query "@D:\path\q.kql"`).
`az` on Windows runs through cmd, which breaks on the parentheses in a query
typed inline. This worked first time today.

**Left in place:** 3 test messages in `upload-events-poison` (Oct 12 19:18Z
and 20:34Z, Oct 13 16:59Z; they expire with the queue's default TTL), and the
soft-deleted blob `uploads/m14-alert-refire-20261013.png` (7 days).
Committed `933f18c`.

**M14 part 3, tracing: built, deployed and shown** (`m14-prep.md`, "Part 3,
the build and the run").
- **Found before building** (Claude, from the installed SDK's source): the
  Agents SDK 1.1.0 never emits its own tool spans, and with content recording
  off the tool names aren't recorded at all. **D-M14-7 (Gerard):** a span
  around the orchestrator's `logged()` helper, patched at runtime. No certified
  file changed, and `build_toolset()`'s schema check guards it.
- **Offline:** 19/19 tests, plus a negative control on the schema guard
  (Claude, CPython 3.14 with every pin). One of Claude's test assertions was
  too strict (`_MS.sampleRate`, the sampler's own attribute); the test was
  fixed, not the code.
- **Gerard installed** the 6 pins in the venv (`pip check` clean), then
  committed and pushed `8b4dce6`. The workflow went green.
- **Traced item4 upload:** 17:37:22Z, `process_upload` 31.9 s, item4's answer
  key. 61 spans under one operation, all succeeded, the three tools by name.
- **Ingestion:** about 200 KB per upload, of which the spans are 76 KB.
- **Not settled by tracing:** the token undercount. The judge uses the
  `openai` package, which isn't traced.

**M14:** all three done-when items are shown, and **Gerard ticks it**. The
marker stays on M13. **Next action: draft the Phase 2 write-up** (Gerard).

**Phase 2 write-up, first draft** (`phase2-writeup-draft.md`, Claude). Gerard
chose the shape (case studies) and the length (like M7's, about 4,700 words).
Claude drafted it from the record, then checked every figure, date and
attribution against its source. That pass fixed 14 lines before the draft
was written to the repo. The worst of them overclaimed: "each milestone was
shown" (M13 isn't finished), "all of it in Bicep" (the CA policies were built
by hand) and "M10's result didn't change" (one item scored lower, traced to
variance).

**Site: the Identity page gets the AI-103 identity work** (`773fac6`, Gerard's
idea; Claude wrote it). It's a cross-reference card labelled "From the AI-103
build", not an AZ-104 project (Gerard, after Claude raised it). It covers the
four identities, keyless code versus key access, the custom role, Event
Grid's scope, the group gate, Conditional Access worded as a trial, and
secretless deploys. It went live now rather than with the joint push (Gerard).
The card's Conditional Access line changes at C9 (Todoist, on the C9 task).
- **Found while rendering it (Claude):** every "Key Design Decisions" list on
  all five domain pages split into side-by-side columns, because
  `.decision-list li` was a flex container. That was live on the site. Gerard
  chose to fix all five pages, with one CSS rule each. All 69 items were
  checked at 1440 and 390 px, and Gerard confirmed desktop and phone live.
- **Not fixed** (Gerard didn't pick it): Project 2's "policy definition GUIDs
  change between CLI versions" claim, which Claude believes is backwards.
  It's in Todoist, to verify against Microsoft Learn.

**The edit pass, after the site work (Gerard, with Claude applying and
re-checking each change):** six case studies tightened, and three security
cuts made (the break-glass password's location, the storage firewall's state,
how the subscription is funded). One factual fix: "the exam's largest-weighted
area" was wrong. Two AI-103 table rows were cut, and "After Phase 2" was added.
Gerard also caught that "subscription" read as an Azure subscription, where
it meant an Event Grid event subscription. That was fixed in the draft and on
the live Identity card. Claude's own error: the date-stripping pattern left
two broken fragments, caught on the final read and fixed.

**Gerard asked what a span is.** Claude explained it as a stopwatch entry with
a parent, nested like an outline, using the run's own rows. Worth a glossary
line in the write-up.

### Session — October 12, 2026 — M12 closed (evidence, teardown); M14 parts 1-2 done (deploys over OIDC, alerts); the Sunday punch-list task rebuilt cloud-only

**Attribution:** Claude diagnosed the scheduled task, drafted the new prompt,
wrote the evidence script, the `dev.bicepparam` edit, every command and these
doc edits, and read every result. Gerard made the decisions marked below and
ran every Azure command. Times are Phoenix (UTC-7) unless marked Z.

**The Sunday punch-list task, rebuilt.** It hadn't run since Oct 4 ("The
computer this routine runs on isn't connected"), even enabled and run by hand.
**Gerard's diagnosis was right:** the task was approved on serenity and was
tied to it; the folder path is the same on the tower, but it's a different
computer. **Correction:** the Oct 1 entry's "no device binding on record"
(Claude) was wrong. Recreated as **IIP Sunday punch list, cloud-only**
(Gerard's choice: it needs only GitHub and Todoist, so it runs whatever state
the tower is in), Sundays 16:56, email and push on. Prompt changes, each
approved by Gerard:
1. Read the repo with `git clone`; the cache-busted raw URLs are only the
   fallback. A clone is the exact pushed commit, so the Sep 14 stale-cache
   failure can't recur.
2. Core tasks come from "Current next action" and the Road to done table,
   checked against the Milestones table. The marker can sit on a milestone
   that is waiting (today M13, idle until the week of Oct 26), and the old
   wording would have planned a week of M13 tasks.
3. Any task due in the next 7 days is a core item.
4. The closing message reaches Gerard by email and push.
5. **A soft freshness gate on a clone read** (Gerard): if Todoist is newer
   than the commit, it still writes the week but doesn't close or reword
   tasks added after the commit. The hard stop stays for the fallback read.
   Claude's first proposal (compare against the commit date) wouldn't have
   stopped the false stops from tasks added on the phone; Claude corrected it
   before anything was built.

The old task is **disabled, not deleted** (deleting removes its run history).
Delete it once the new one has a clean run. The new one was fired by hand today
for the Week of 2026-10-12. The Friday check-in isn't in the scheduled-task
list (Sep 21 entry: "doesn't exist"; Oct 1: "paused"); left alone.

**M12 evidence, before the teardown (Gerard: "take a few now").** Claude chose
read-only CLI captures over portal screenshots: text, nothing to redact, and
committable like the M13 export. 8 JSON files in `evidence/m12-networking/`;
the home IP is counted, never listed, and the subscription ID is replaced
(Gerard). **Found:** the Function's `outboundVnetRouting` reads all `false`;
Microsoft Learn says Flex routes all traffic through the VNet regardless. It
also makes the Oct 9 "no NAT gateway needed" result more surprising: measured,
mechanism unknown, and the README says so.

**Teardown** (`m12-prep.md`, "The run, 2026-10-12"; README "M12"). Gerard ran
the errand between the evidence and the teardown, so the deploy wasn't split
by a break.
- What-if #1: **7 / 26 / 11 / 10** against a predicted 12 to ignore (the zone
  groups aren't listed). The Function showed no `- virtualNetworkSubnetId`, so
  the deploy left it in the VNet and the CLI detach was required. That made
  the order safe as well.
- Deployed 17:16Z; detached; the 6 deletes; only the skeleton is left.
- Regression upload: 17:26:05Z → 17:26:49Z (44 s), item4's answer key.
- What-if #2: **6 / 27 / 11 / 2**, exactly as predicted. The register now.
- **M12 ticked** in `phase2-orientation.md` (Gerard). The marker stays on M13.
  **Next action: M14 prep** (Gerard).

**Found:** OneDrive is off on the tower (Gerard; local backups go to D: and
Google Drive once the project is at a stable point, already in Todoist). The
runbook's `$d` pointed at `OneDrive\Documents\Data\Claude\m12`; it now points
at `C:\Users\gerar\Documents\Data\Claude\m12`. Older entries naming OneDrive
paths are history and stay as written.

**Claude's error, caught by its own read-back:** the evidence script's last
edit and its copy to the tower went out at the same time, so the tower got the
pre-edit file. It was re-copied from a fresh staging name and confirmed by
hash. The lesson is in "Settled".

**M14 part 1, CI/CD over OIDC, done the same afternoon** (`m14-prep.md`,
"Part 1, the run"; README "M14"). Gerard asked for briefings on GitHub OIDC and
Foundry tracing (alerts familiar) and decided D-M14-1 (order: OIDC, alerts,
tracing), D-M14-2 (trust branch `main` only) and D-M14-3 (trace now, on the
classic API). Claude wrote `m14-prep.md`, the federated credential and the
workflow; Gerard added the 3 GitHub secrets, copied the workflow into place
(the remote tools can't write there) and pushed `fd02de9`. That push was the
first deploy. The activity log shows `-02` (`3a770f3a-…`) calling
`publishxml`, and the regression upload passed in 49 s.
- **Found, by asking what `publishxml` returns:** basic auth was ON for `scm`
  and `ftp` (ARM's default), so the publish profile held a deploy password.
  Switched off in `app.bicep`; a `workflow_dispatch` deploy stayed green.
- **Found and closed:** the two `sites/write` events Gerard hadn't run were
  the 10-minute-late completion records of his own deploys, matched by
  correlation ID. Claude's hypothesis, which the log confirmed.
- **Corrected before it was built:** `m14-prep.md` first named a poison-queue
  *metric* alert; Learn shows `QueueMessageCount` can't single out a queue and
  updates daily.
- **Unchanged and not done:** the Sunday task's notification test (Todoist,
  Oct 19). The project instructions block was pasted by Gerard (Todoist
  closed).

**M14 part 2, alerts, done the same afternoon** (`m14-prep.md`, "Part 2, the
survey and the run"). The survey: the budget emails Gerard's backup inbox with
no action group; there were no alert rules; the poison line is exact; all 14
failed runs in 20 days were deliberate tests (7 × 2 tries). Gerard decided
D-M14-4 (15-minute checks, $0.50/month) and D-M14-5 (address in an
environment variable). Claude wrote `alerts.bicep`; the what-if was the
register plus 2 creates, exactly.
- **Claude's error:** the first proof upload left out `topic`, from a
  misremembered reading of Sep 29. The handler treats that as the uploader's
  mistake (error result, no retry), so nothing was parked. The redo used Sep
  29's real method (pause, upload, delete the blob, un-pause): poison line at
  19:18:39Z, fired 19:22:56Z; a re-fire at 20:37:57Z. **No real alert email
  arrived** (3 handoffs), though the portal test email did; open item in
  Todoist.
- **Part 3 started:** the packages are resolved (the distro adds 25, the lean
  set adds 6, and neither moves a pin). Gerard chose the lean set (D-M14-6).
  Closed out at about 13:45 by choice (Gerard), rather than start the tracing
  code with no time for its regression run.

### Session — October 10, 2026 — M12 stage 3 done: the storage firewall is on and the private paths are verified

**Attribution:** Claude wrote the Bicep, `set-home-ip.ps1`, the
`m3_analyze.py` fix, the commands and these doc edits, and read every result.
Gerard made the two design choices below, and ran every what-if, deploy and
test. Times are Phoenix (UTC-7) unless marked Z.

**Design choices (Gerard), from tests Claude ran with the Bicep CLI first:**
- `readEnvironmentVariable()` with no default fails at compile time even
  inside a ternary branch that isn't taken, so "require the IP only at stage
  3" needs a placeholder value. **Chosen: required at every stage**, with no
  default and no placeholder.
- **Chosen: a tracked script that looks the IP up live** (`curl.exe -4`,
  api.ipify.org) instead of an untracked file holding it. Nothing on disk
  holds the address, and an address change is picked up on the next run.
  Amends D-M12-4's wording; its intent (no IP in the public repo) stands.
- Claude's own change: `publicNetworkAccess: 'Enabled'` at every stage,
  because adding it only at stage 3 with `union()` switches off Bicep's type
  checking (tested: a misspelled property compiled silently).

**Build and tests** (details: README "M12"):
- What-if, saved as JSON outside the repo and read entry by entry: exactly as
  predicted, 11 modify, 30 no change, 11 Unsupported, 4 to ignore. Deployed as
  `m12-stage3-20261010`.
- (a) Upload 17:25:25Z → result 17:26:11Z (46 s), complete and correct. (b)
  Results page on the phone: works. (c) Cloud Shell: refused by the firewall.
  (d) `--blob`: `ContentSourceNotAccessible`, as predicted; `--file` passed.
- **Found:** `m3_analyze.py`'s comment said `raise_for_status()` "raises with
  the real error body"; it doesn't, so (d) first failed with a bare 400.
  `_raise_with_body()` fixed it.

**Agent isolation, written up (M12's last scope item).** Claude drafted it in
`m12-prep.md` from Microsoft Learn and the retail price list. Key facts: VNet
injection can't be added to an existing Foundry account; Learn's isolated tool
support covers only the new Responses API agents; the IIP agent only calls
functions, which Learn routes over Microsoft's backbone. Options: A, inbound
lockdown of today's account, $8.80/month; B, the full network-secured
Standard setup, about $98/month. Gerard asked whether B was "worth a month's
credits"; Claude corrected its own framing (it bills hourly, about $3.25/day,
so time is the real cost). **Gerard decided:** build B inside the classic-API
migration (D-M12-8); A stays design-only (D-M12-9).

**Stopped at about 11:20 (Gerard's choice)** with ~75 minutes left, rather
than start a 60-75 minute teardown with no margin. Claude wrote the teardown
runbook and its predicted what-ifs into `m12-prep.md` instead. Commits:
`m3_analyze.py` fix, then `adfc13c` (stage 3), `306e0da` (agent isolation).

**Claude's error, caught by Gerard's paste:** step (c) said "Cloud Shell
(Bash)", and "Bash" read as any Bash window, so the first run went to Git Bash
on the tower and succeeded from the home IP. The `curl` line put first in the
step showed it. The run became the positive control; the redo in Azure Cloud
Shell was refused. **Also called out by Gerard:** Claude's messages were
printed twice (a mid-task message plus a final reply repeating it), which
risks acting on the first copy. Agreed: one copy per message; Gerard asks for
"actions with steps only" if a message is unclear.

### Session — October 9, 2026 — M13 steps 5-6 done: CA001 On passes T1-T6; policies exported; C9 set for the week of Oct 26

**Attribution:** Claude wrote the steps, the commands, the split of the
export into per-policy files, the folder README and these doc edits. Gerard
ran every test and command and made every decision named here. Times are
Phoenix (UTC-7). Details: the CA spec's "Progress, 2026-10-09".

**Deploy step 5, CA001 On: all six tests pass** (sign-in log, Conditional
Access tab):
- **T6 first:** `item4-t6-ca001-on-20261009.png` uploaded at 09:47:35; the
  Function wrote its result at 09:48:15 (40 s). Claude read the saved copy
  (`scripts/results/20261009-164815_function_item4_t6.json`): status ok, run
  completed, copy passed first time (0 redrafts), audit legible/brand
  FAIL/info accurate, item4's answer key. No managed-identity sign-in row
  appeared; not chased (the result is the proof; tokens are cached).
- **T2 (10:17):** after the password, Entra offered only "Face, fingerprint,
  PIN or security key", no Authenticator push. CA001 Success with the
  requirement "Phishing-resistant MFA". Stronger than the amended matrix
  expected: the push is never offered, so it can't be approved. The first T2
  attempt (09:53: password, then the passkey when asked) proved only the
  passkey path; the 10:17 re-run looked at the method list on purpose.
- **T4** `bg-admin-01` (about 10:00): page loaded, every policy Not applied.
- **T5** `iip-ca-test` at My Sign-ins (10:02:40): CA001 Not applied.
- **T1** passkey (10:04:48): CA001 Success; the page listed the T6 upload.
- **T3** by reference (Oct 7, AADSTS50105), as planned.

**Deploy step 6, evidence (C8):** the five policies exported read-only with
`az rest` (Graph v1.0) to `evidence/m13-conditional-access/`. Claude split it
per policy, read every file back from the tower (byte-identical) and checked
all five against the spec: all match. Gerard confirmed the IDs by name
(`bg-admin-01`, IIP Results Viewers (dev), IIP Results (dev)). **Found:**
CA903 also excludes the role Directory Synchronization Accounts, from the
template; harmless (no sync). Phone screenshots aren't possible (Incognito
blocks them), and the portal log screenshots show home IP addresses, so none
went into the public repo.

**Gerard's decision:** C9 in the week of 2026-10-26, not today and not Nov 2.
CA001 stays live as a demo, with about 10 days of buffer for the
managed-policy risk. The Todoist trial task moved to Oct 26.

**How the work ran:** no shell on the tower again (file read and write
through the bridge only); Gmail reachable through Chrome, Drive and Calendar
through their connectors. **Claude's process error, called out by Gerard:**
the test steps were spread across several long messages and referred to by
matrix codes (T1-T6) defined only at the start, so he couldn't tell what was
done or still open. Corrected mid-session with one plain-words status list.
Doc writes followed the Oct 6/7 rule (written, then read back from the
device and compared). The morning's work was committed as `0d845cc`.

**Afternoon: M12 step 1, the cost estimate (done).** Claude priced it from
Azure's retail price list and Microsoft Learn; Gerard made three decisions
(`m12-prep.md`): **D-M12-1** endpoints on `stiipdevwus01` blob + queue only,
none on the empty Key Vault; **D-M12-2** an evidence window, then delete,
keeping the Bicep; **D-M12-3** the retail price list stands in for the
calculator (done-when amended). Result: **$15.60/month** running, **about
$3.60** for a week. Found: on Flex Consumption all outbound traffic goes
through the VNet, and new VNets default to private subnets, so the Function
may need a NAT gateway to reach Foundry (about $33/month, unverified; the build
tests it with one upload). Also found: the endpoints need their own subnet,
and `storage.bicep`'s `bypass: 'None'` must become `AzureServices` for Event
Grid. Committed as `6a02521`.

**Then M12 step 2, the design (done).** Claude drafted; Gerard decided:
**D-M12-4** the home IP lives in an untracked local file, not the public repo;
**D-M12-5** endpoints named after their target (`pep-stiipdevwus01-blob`,
`-queue`); **D-M12-6** one NSG per subnet; **D-M12-7** after the window, keep
the free VNet, subnets and NSGs. Checked: the storage account has only an IPv4
address (`A` record only), so the firewall rule is IPv4; no VNets exist in the
subscription (Gerard), so `10.20.0.0/24` is free. Design, build order, tests
and teardown are in `m12-prep.md`. Gerard asked why IPv4 rather than IPv6;
Claude's answer (the service decides the family; IPv6 rules would need a
prefix, since Windows rotates its IPv6 addresses) shaped the IPv4 note there.
Committed as `c802ebe`.

**Then M12 build, stages 1 and 2 (done).** Claude wrote `network.bicep`,
`privatelink.bicep`, the `networkStage` switch and the stage 2 change to
`app.bicep`, and compiled each before handing it over; Gerard ran every
what-if, deploy and test.
- **Stage 1** (`m12-stage1-20261009`): what-if exactly as predicted (11 to
  create). Endpoints Approved; zones `10.20.0.36` / `.37`; the tower still
  resolves the public IP.
- **Stage 2** (`m12-stage2-20261009`): the first what-if, saved as JSON and
  read line by line by Claude, showed 7 diffs on the new resources. **Two were
  writable properties the template had dropped** (`privateEndpointVNetPolicies`,
  `resolutionPolicy`), now declared; the rest are registered noise. The re-run
  matched (10 modify, 31 no change). Upload test: a complete, correct result
  in 42 s. **No NAT gateway needed.**
- **Process:** Claude's writes to the tower failed silently twice (old content
  under a new timestamp) until each write used a fresh staging name; every
  write was read back and compared before Gerard was told it was done.
- **Stopped before stage 3** (Gerard, 14:08): about 75 minutes of work left
  against 80 minutes of session, so stage 3 starts fresh on Oct 10.

### Session — October 8, 2026 — M13 steps 3-4 done: methods migrated, baseline CA900-CA903 live, security defaults off; CA001 built, Report-only pass, then On; AzSvcAdmin closed off

**Attribution:** Claude wrote the steps (from Microsoft Learn), the CLI
commands and these doc edits. Gerard ran every portal step and command and
made every decision named here. Times are Phoenix (UTC-7).

**M13 deploy step 3, done** (details and the verification table: the CA
spec's "Progress, 2026-10-08"):
- **Methods first (3a).** Microsoft Authenticator enabled for All users, mode
  Any, OTP Yes (09:50); the legacy methods unticked and the migration set to
  **Complete** (10:12). `djeemunee`'s Authenticator sign-in at 11:07 (past the
  lag) proved the new policy alone carries his MFA. SMS and Voice stay off.
- **Baseline (3b).** `CA900-Baseline-AllUsers-BlockLegacyAuth`,
  `CA901-Baseline-AllUsers-MFA-AzureMgmt`, `CA902-Baseline-Admins-MFA`,
  `CA903-Baseline-AllUsers-MFA`, from the Secure foundation templates, in
  Report-only. The 9xx names are Gerard's choice. Each template came out
  excluding its creator, `djeemunee`; all four were fixed to exclude
  `bg-admin-01` only, and What If confirmed it for three users.
- **Switch (3c).** Security defaults Disabled, the four policies On (11:14).
  From 12:01, real sign-ins for `djeemunee`, `bg-admin-01` and `iip-ca-test`
  matched the expected Conditional Access results, every row.
- **Managed policies (3d):** 0 right after the switch.

**Found today (each is in the spec or the settled list):**
- Report-only creation works while security defaults is on; only On is
  blocked. This settled the spec's one "Unverified".
- The per-user MFA page showed Microsoft's own forced migration in progress
  (the legacy MFA/SSPR policies were deprecated 2025-09-30). It didn't block
  anything.
- The Azure management template targets **Azure Resource Manager**
  (`797f4846-…`), the app older docs call "Windows Azure Service Management
  API".
- **T2 in the test matrix had to change:** with CA903 on, "password only" can't
  reach the results page, so T2 is now an Authenticator push that CA001 must
  refuse.
- On Flex Consumption, `az functionapp show --query defaultHostName` returned
  null; the runbook now has the `az resource show` form and the portal path.

**`AzSvcAdmin@ostebovik.net` (item 5 of yesterday's next action), closed
off.** Its only sign-ins (non-interactive, Oct 6 7:56-8:00 PM) were one Edge
browser profile starting up, from the home network's IPv6 range (Cox). Gerard
didn't recognize it; created 2026-01-10. It held **Owner on the lab subscription, Owner and
Contributor on MG Non-Prod, and Storage Blob Data Contributor on
`stgeostewus301`** (the likely reason it existed: manual site uploads).
Nothing in `geoste-portfolio` references it except STATUS.md. No Entra roles.
Gerard chose: all four roles removed (list confirmed empty), sign-in blocked,
sessions revoked; **delete on Oct 22** if nothing complains (Todoist).

**Two Microsoft emails (Oct 7), read through Chrome:** the Azure Resource
Graph CVE schema change doesn't affect this project. **The classic Foundry
Agent Service APIs retire on 2027-03-31**, and Microsoft says this
subscription uses them, so the M7 orchestrator and the Function's agent path
need checking. Todoist, first step due Dec 1.

**How the work ran:** no shell on the tower again, only file read and write
through the bridge. Early on, the Chrome extension wasn't connected and
screenshots wouldn't attach in chat; Gerard signed in to the extension, and
screenshots went through a connected folder instead. About 40 minutes lost to
this. Claude's instruction errors today, each caught by Gerard: the What If
blade's labels and required fields didn't match Claude's steps; Claude asked
for a "Client app" column the non-interactive log doesn't show by default; and
an "Undo" line read like an instruction. Doc writes followed the Oct 6/7 rule
(a fresh staging name per write, read back from the device and compared).
The morning's work was committed as `b4d80b0`.

**Afternoon: M13 step 4, CA001** (details: the CA spec's "Progress, 2026-10-08
afternoon"):
- `iip-ca-test` got a device-bound passkey in Authenticator on the phone
  (Gerard's choice; a test user, so the one-phone risk is accepted).
- **C5 amended (Gerard):** CA001 keeps the 8-hour sign-in frequency and drops
  "Never persistent", which Microsoft Learn says needs All cloud apps. Caught
  by Claude checking the settings against Learn before the build, not after.
- CA001 built by hand in Report-only. What If matched for all three users.
  The Report-only pass (T1, T2, T4, T5) matched; T3 is covered by Oct 7's gate
  test 1, since every non-member is an admin; T6 moves to the On pass.
- **CA001 switched On at 13:41** (Gerard's choice), so the propagation wait
  runs between sessions. Next session starts at the On-pass tests.
- Claude's instruction error: step 3's What If was written so that it read
  like a sign-in test on the phone. Gerard asked; corrected.

### Session — October 7, 2026 — P2 trial started; M11 closed (group swap); marker to M13; tenant cleanup; break-glass account

**Attribution:** Claude wrote the `entra.bicep` edits, the CLI commands and
these doc edits. Gerard ran every command and portal step and made every
decision named here.

**Entra ID P2 trial, started:**
- **The portal path has changed.** Microsoft 365 admin center → Purchase
  services redirected to the **Entra admin center → Billing → Trials →
  Activate** (Microsoft Entra ID P2), which hands off to a Microsoft 365
  checkout: "One month free with payment details", 100 licences, $0, the card
  on file "used to verify your identity".
- **Recurring billing: Off by default**, with "Edit recurring billing" greyed
  out (Billing → Your products, Gerard's screenshot). Claude's reading
  wavered on the way: it first called the conversion risk smaller from the
  Activate page's wording, then reversed that on the checkout's "with payment
  details" and Microsoft Learn ("some self-service trials ... automatically
  convert to a paid version"). The product page settled it: Off.
- **Ends 2026-11-06 or -07.** Your products says 11/7; each user's licence
  tab says 11/6 (probably UTC vs local time; unconfirmed). Plan to the 6th.
  Todoist reminder due Nov 2.
- P2 assigned to `djeemunee` and `iip-ca-test`. The usage location is set on
  the user's **Licenses and apps** tab in the Microsoft 365 admin center.
  `subscribedSkus`: `AAD_PREMIUM_P2`, 100 enabled, 2 used.

**M11 closed: the group swap and both gate tests** (details:
`infrastructure/iip/README.md`, "The group swap"):
- `m11-entra-20261007a` assigned **IIP Results Viewers (dev)** to the app.
  The direct `iip-ca-test` row was deleted by CLI. **The first gate test
  caught a missed step:** the delete hadn't been run, and `iip-ca-test`
  reached the page through the leftover row. Run again, the list showed the
  Group only.
- **Gate test 1:** AADSTS50105 (sign-in log 17:43:23Z, error 50105, Correlation ID `6a3aaa06-6190-441f-a6da-3f60416c8cdf`). `m11-entra-20261007b` made
  `iip-ca-test` the group's only member. **Gate test 2:** the results page
  (sign-in log 17:53:18Z, Correlation ID `f3e78331-3d8e-421d-95dd-14383249ccc5`). M11's done-when is met. RBAC row 10 is confirmed as designed; the
  VERIFY ledger has no open or interim rows.

**Decisions (Gerard):**
- The viewers group's members use **replace** semantics (the template is the
  whole list); owners stay on the default, append.
- **The marker moves M11 → M13**, passing over M12. Claude's case, which
  Gerard chose: only M13 runs on the trial clock, and M12's private endpoints
  don't touch the sign-in path that CA protects.

**How the work ran:** this session had no shell on the tower, only file read
and write through the bridge, so the git checks were Gerard's. Every Claude
file write went to a unique staging name and was read back from the device
and compared byte for byte (the Oct 6 fix). **One didn't:** at the end of the
day, STATUS.md landed without two small fixes, because Claude had edited a
staging file in place after first writing it, instead of writing a new name.
The read-back caught it, and a rewrite under a fresh name matched. The rule is
stricter than "a unique name per write": a staged file is never edited
again.

**Afternoon: M13 prep (tenant cleanup, break-glass), after the M11 commit
`3f51098`.** Claude wrote the scripts and these notes; Gerard made every
decision and ran every step.
- **Inventory with last sign-in:** `Get-EntraInventory.ps1` gained sections
  8-10. Section 8 (users) works but runs about a day behind. Sections 9-10
  (beta service-principal and credential reports) are **unusable for now**:
  the report's newest entry anywhere is 2026-01-13.
- **Cleanup (`Remove-EntraRemnants.ps1`, dry run first):** Gerard identified
  the unfamiliar objects as **AZ-900-era** leftovers (early Entra experiments
  and an abandoned genealogy site). Removed: 9 users and 6 app registrations
  (soft delete, restorable until about Nov 6), 4 empty security groups
  (permanent), and 8 role assignments. Among them is `familytree-api-01881`'s
  **Contributor on the whole lab subscription with a live secret**, the
  tenant's biggest standing risk. The dry run said 26 actions where Claude's
  message had said 31: Claude's arithmetic, and Gerard stopped before
  `-Apply` to ask. One delete hit the ReadOnly lock `Not4Deployment` on Legacy
  PAYG 1 (Gerard's AZ-900 cost guard). It was lifted for that delete and
  recreated exactly. Left: 3 users, 1 group, 2 app registrations. Record and
  logs: OneDrive `Data\Claude\entra-inventory` (kept out of the repo: names
  and object IDs).
- **Break-glass (M13 deploy step 2):** `bg-admin-01`. Details and the known
  gap are in the CA spec's "Progress, 2026-10-07".
- **A diagnosis worth keeping:** the first passkey sign-in failed (135016,
  "FIDO sign-in is disabled via policy"). Claude guessed twice and was wrong
  twice: first a Google-synced passkey, then the profile's synced setting. The
  sign-in log showed it was the Authenticator passkey on the default profile.
  **Gerard retried before changing anything, and it worked:** propagation lag,
  not configuration.
- **M13 step 3 checked, not started:** Conditional Access list empty, security
  defaults Enabled. C7 amended (templates, by hand). Step 3 moved to next
  session (Gerard): it changes every sign-in, and with the lag it needs 60-90
  minutes with nothing left half-done.

### Session — October 6, 2026 — site and resume fixed, Entra inventory, subscription risk sized (P2 trial moved to Oct 7)

**Attribution:** Claude wrote the inventory script, every file edit and the
diagnoses below; Gerard ran every command, made every decision named here,
and reworked the resume himself (`bcf7858`, in his job-search work).

**Subscription risk, sized** (read-only; Gerard ran it):
- The **whole ostebovik.net prod stack** is on the same subscription as the
  labs, so the public site depends on that subscription staying available.
- Last cycle (Aug 18 - Sep 17) cost **$69.16**. Front Door is ~$32 of each
  cycle, so the site on a subscription of its own would be ~$35-40/mo.
*(Reworded 2026-10-14: the offer details are kept out of the public repo.
The full record is in the Todoist task on this risk.)*
- Three pay-as-you-go subscriptions exist in the tenant, **all empty**.
  Fallback plan and the move-or-wait decision: Todoist.

**Site: the a1ddb40 phone check failed, and it wasn't the deploy.**
- **Claude's error, Oct 5:** `a1ddb40`'s message claims "hero count 15 -> 14"
  and a Monitoring link restyle. Neither edit was in the commit or the working
  tree. Fixed in `841f563`. *[Later the same day: this may not have been a
  wrongly written message. See "Claude's file writes" below: the same
  symptom was reproduced twice on Oct 6, and on Oct 5 Claude also wrote files
  through the device bridge. Not proven for Oct 5.]*
- Front Door had cached a **404 for `/img/og-card.png`** (the plain URL 404'd;
  the same URL with `?v=` served the image). One `/*` purge cleared it.
- **LinkedIn couldn't read the bare domain** ("Bad DNS") while
  `www.ostebovik.net` worked: `@` was a literal CNAME, which the DNS rules
  forbid at the zone apex. Gerard switched it to **ALIAS** at Namecheap;
  Google DNS then returned A records and Post Inspector worked. Trade-off,
  from Microsoft Learn: Front Door no longer auto-renews that certificate
  (expires **2027-03-18**), so a monthly Todoist task checks for "Pending
  Revalidation".

**Resume and homepage, support-first** (Gerard's direction: senior technical
support, growing toward admin):
- `e0d9cc2` (Claude): an AI-103 IIP block in Hands-on Azure Projects (three
  bullets Gerard approved) and a fixed link (`/monitoring-security/` was a
  404). Its message also claims the preview text; that change actually
  landed in `23497f4`.
- Homepage (Claude, Gerard's answers), `a9b381f`: support-first tagline and
  intro, the preview text, "Resources deployed" (was "in production") and 3
  certifications (was 2, but the resume lists 3).
- Resume lab section (Gerard's call, Claude's edit): header "AZ-104 projects:
  14 hands-on Azure labs" (2025 - 2026), parallel to the AI-103 block, and the
  live production environment moved to the first bullet. `23497f4`'s message
  claims this, but it carried only the preview text; the change itself is in
  the commit after `8f1a77c`.

**Claude's file writes lagged one version behind (found by Gerard, 14:28).**
Gerard saw the resume in the repo didn't match what Claude said it had
changed. Evidence, from the commits themselves:
- Two resume writes 14 s apart (13:24:42, 13:24:56) to the same staging path:
  `e0d9cc2` got only the first. A third write at 13:59 delivered the
  **second** write's content, so `23497f4` got that.
- Two STATUS.md writes about 5 min apart to the same path: only the first
  landed (`8f1a77c` lacks the second).
- The homepage's two writes to one path, about 3 h apart, both landed.
- Likely cause (inferred, not proven): the bridge reused content for a
  repeated staging path. **Fix, in Claude's practice:** a unique file name for
  every write, and re-read the file from the device after every write to
  compare it with what was intended. The resume fix at 14:35 was verified
  that way. Claude also never checked a commit's diff against its message;
  that's the second half of the miss.

**Entra inventory, step 1 (structure only).** `Get-EntraInventory.ps1`
(Claude; read-only Graph GETs and `az` lists) in OneDrive
`Data\Claude\entra-inventory`, with a findings file beside it. Kept out of
the repo: it names users and object IDs.
- **Every IIP identity and assignment maps to an RBAC model row.**
- **Only one Global Administrator**, with a permanent assignment and no
  break-glass account. Fix before M13.
- `familytree-api-01881` has **Contributor on the whole lab subscription** and
  a live client secret. It's the largest standing risk in the tenant.
- letter7.net is a **verified** domain with 4 users on it, so the
  registration matters.
- **Found:** last sign-in (`signInActivity`) needs Entra ID P1/P2 (Microsoft
  Learn), so that column waits for the trial.

**Not done:** the P2 trial and group swap. Moved to Oct 7 by Gerard; the steps
are in Current next action.

**Working tree left dirty overnight, on purpose (Gerard, 2026-10-06):**
`ai-103/infrastructure/iip/entra.bicep` is edited and uncommitted. Committing
it before the deploy would put a template on `main` that disagrees with
Entra (it drops an assignment that still exists and declares one that
doesn't yet). It gets committed with the M11 close on Oct 7. Until then:
stage files by name, never `git add .`, and any measurement run's provenance
will record the tree as dirty. Claude verified its contents on the device
before this was written.

**Deploys:** push one commit, wait for its deploy to go green, then push the
next. Two pushes 13 s apart (`23497f4`, `8f1a77c`) made the first deploy fail
with "No matching Static Web App environment was found".

### Session — October 1, 2026 — M11 docs brought up to date (short session)

**Claude wrote every edit in this entry. Gerard chose the plan** (scheduled
tasks, then the M11 docs, then stop: about 45 min, after a morning of job
search).

**The laptop (`serenity`) died for good on battery.** It still runs on AC, so
the files that lived only on it (Gerard's prompt-crafting notes) can be copied
off while it's plugged in. His recent session prompts are already in Google
Drive.

**Scheduled tasks: no action needed.**
- The Sunday punch-list task has no device binding on record. Its folder path
  exists identically on the tower, and its prompt reads only GitHub and
  Todoist. Its last run succeeded (Sep 28). If the Oct 4 run fails, its
  run status will show it.
- The Friday check-in was **paused by Gerard earlier**, not lost with the
  laptop.

**Docs (STATUS item 1, done):**
- `phase2-rbac-model-draft.md`:
  - a status note saying the model is built;
  - the Resources table now reads "deployed" (11 rows);
  - rows 10, 11 and 17 record what was built and proven on Sep 30, with row
    10 marked **interim**;
  - row 5's stale "still VERIFY" is struck, with a pointer to Sep 24's
    confirmation;
  - D4 is confirmed;
  - the D1 table's Foundry User row is marked superseded;
  - a completeness note on the D1 table;
  - a new **VERIFY ledger**: rows 4, 5 and 16 and D4 confirmed, and row 10
    changed (interim). That settles that half of M11's done-when.
- `phase2-orientation.md`: a pass 2 status bullet, and the P2 trial decision
  amended, because M11's last step now needs the trial.
- `m11-prep.md`: a pass 2 row in the results box.

**Correction to the Sep 30 entry:** it called the Search Index roles missing
from `phase2-rbac-model-draft.md`. They're there, under "Deliberately given
nothing". Only the D1 table omits them. Foundry User at account scope is
**deliberate**: the subscription grant was removed on 2026-09-22 (the
orientation Backlog). The D1 table was stale, not the permissions.

**Tower setup, recorded here because it's in no other doc:** Node.js LTS
(`winget install OpenJS.NodeJS.LTS`), and PowerShell
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, which `npx.ps1`
needed. Together they fixed the pdf-viewer plug-in (`'npx' is not
recognized`). Both belong on the Drive migration checklist for any future
machine.

### Session — September 30, 2026 — moved to the tower; M11 pass 2 (sign-in) built and proven

**Claude checked the docs, Todoist and the laptop's untracked files and wrote
these edits. Gerard chose the order.** Late start. Started from the Sep 29
handoff and the Todoist punch list, which agreed.

**D1 was already fixed.** `phase2-rbac-model-draft.md` has carried a "D1
correction" section since 2026-09-21: the full role table, Owner on
`Non-Prod`, Contributor at the tenant root. Row 1 and the D1 row point to it.
Only the bookkeeping was stale: the `phase2-orientation.md` backlog item,
STATUS item 4 and the Todoist task. All three are closed now. No Azure change.

**Order: switch machines before pass 2.** Pass 2 is 1-2 sessions, so starting
it on the laptop today would have put the machine switch in the middle of
sign-in work, which depends heavily on local state (`az login` token cache,
tenant, two GitHub accounts). Two changes at once, two suspects. Gerard's
choice.

**What a fresh clone would lose** (from `git status --ignored` on the laptop):
`scripts/.env`, `Claude outputs/` (292 KB), 30 untracked files in
`scripts/results/`, `scratch.py`, `tester.py`, `m6_probe.py`, `.vscode/`,
`Get-RgResources.ps1` and the Axon .docx files at the repo root. The 9 results
files the M7 write-up cites are all tracked. Hence: copy the folder, don't
clone.

**The move: done.** Gerard ran steps A-G of the Drive checklist
`2026-09-30-tower-migration-checklist.md` on the tower: installs; git settings
matched to the laptop (`core.autocrlf=true`, Git Credential Manager, GitHub
username `geostebovik`); robocopy of `geoste-portfolio` and `az-104` with
**Failed 0**; `git status` clean at `393fa57`; the venv rebuilt at
`C:\Users\gerar\venvs\ai-103` from both requirements files; Bicep, `az login`
and the subscription set. The laptop's untracked files (`scripts/.env`,
`Claude outputs/`, the 30 older results files) came across with the folder.
Left behind on purpose: `geoste-portfolio-purge-tmp` and the `az104_id_rsa`
SSH key.

- **What-if on the tower: 6 modify, 22 no change**, which matches the register.
  It also confirms the post-soft-delete totals that
  `infrastructure/iip/README.md` had listed as "expected, not yet confirmed"
  since Sep 29. That line is updated in this commit.
- **`az` identity: correct.** Gerard thought he had picked the wrong account at
  `az login`. The check showed `djeemunee@letter7.onmicrosoft.com`, tenant
  `e0249b00-…`, object ID `fdc0b6bb-…`. Both IDs match `dev.bicepparam`.
  The unfamiliar subscription name was simply its display name. No re-login
  was needed.
- **Noticed, not chased:** the full role list shows **Foundry User at the
  account scope** (`aif-dev-wus-01`), where the D1 correction table says
  subscription. It also shows **Search Index Data Reader and Contributor** on
  `srch-iip-dev-wus-01`, which that table doesn't list. It's a documentation
  gap in `phase2-rbac-model-draft.md`, not a permission problem.
- **First push from the tower:** this commit. It is also the credential test,
  because only a push authenticates.
- **The checklist's step D was wrong.** It said `git fetch` would prompt for
  sign-in. It doesn't: the repo is public, so only a push authenticates. No
  prompt on fetch is the expected result, not a fault.
- **The Claude app's link to the computer did not move within a conversation.**
  The Sep 30 laptop conversation stayed bound to the laptop. Messaging it from
  the tower and quitting the laptop app both failed, so the rest of the day ran
  in a new conversation. Claude confirmed from there that the device is
  `tower`, and read `main` = `origin/main` = `393fa57` from the tower's `.git`
  ref files. Claude has no shell on the tower, so git checks are still
  Gerard's.

**Still open, not today:** see Current next action (items 3 and 6).

#### M11 pass 2, sign-in: built, deployed and proven (afternoon, on the tower)

**Claude wrote all the Bicep, the Function code, the offline tests and the doc
edits, and researched each step in Microsoft Learn. Gerard made every decision
below, and ran every Azure CLI command, deployment, commit and browser test.**
Commits `8bdae42` → `482fe58`. The details are in
`infrastructure/iip/README.md` ("M11 pass 2") and `function/README.md` ("The
results page").

**Gerard's decisions:**
- the Entra objects go in Graph Bicep, in a separate `entra.bicep` (Graph
  resources get no what-if, so they're kept out of the registered
  `main.bicep`);
- RBAC row 10 goes **user first**. letter7 has no Entra licences, and a group
  assignment needs P1/P2, so the group swap waits for the P2 trial's day 1.
  This was found today: row 10 and "start the trial after M11" were circular;
- the test user is created by CLI;
- the page is a list plus a detail view, at `/api/results`, with `host.json`
  unchanged;
- a regression upload before wrapping up.

**What was built:**
- **Step A:** `id-iip-dev-wus-03` (`m11-signin-id-20260930`). Verified: no
  Azure role.
- **Step B:** `entra.bicep` creates the app registration **IIP Results
  (dev)**, the federated credential `fic-id-iip-dev-wus-03`, the enterprise
  app with assignment required, consent for `openid profile email` only, and
  the group **IIP Results Viewers (dev)**. Deployed `m11-entra-20260930b`.
  Every object read back and matched.
- **Step C:** `app.bicep` attaches `-03`, adds
  `OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID`, and turns on `authsettingsV2`
  (`m11-signin-easyauth-20260930`).
- **The test user** `iip-ca-test` (RBAC row 11), a non-admin. Its password
  never left Gerard's machine.
- **The interim row 10 assignment** (`m11-entra-20260930d`).
- **The results page:** `results_page.py`, two HTTP routes, and
  `RESULTS_BLOB_ENDPOINT` (`m11-results-setting-20260930`), deployed by
  remote build. Its second lock refuses any request without built-in
  authentication's identity headers. Every value is escaped. 21 offline
  checks pass.

**Proven in Azure:**
- **Secretless sign-in:** `response_type=code+id_token`, and the sign-in
  completed.
- **The gate:** unassigned `iip-ca-test` got **AADSTS50105**; assigned, it
  reached the page.
- **The page:** as `iip-ca-test`, the list shows every result, and the detail
  shows the audit and the final drafted copy.
- **Regression:** `regress-20260930.png` (item4's image) went through
  upload → Event Grid → queue → agent → result. Status `ok` at 23:01:49Z,
  with the same verdicts as item4's earlier runs. It shows up on the page.
  The upload path survived two identities, sign-in, and a code redeploy.

**Not done:** the "group member" in the done-when (item 2 of Current next
action), and the RBAC and orientation doc updates (item 1).

**Claude's errors today, for the record:**
- **The first identity check was clumsier than needed.** `dev.bicepparam`
  already held the tenant and object IDs.
- **Graph Bicep `owners`:** Claude wrote the object form. Types `1.0.0` wants
  plain IDs (BCP034).
- **The federated credential's name** was written as one segment. The first
  Entra deploy failed on it (`m11-entra-20260930`).
- **ID-token issuance off**, on a wrong reading of the flow, gave
  AADSTS700054. Fixed by redeploying `m11-entra-20260930c`.
- **AADSTS50105 predicted for a Global Administrator**, who bypasses the gate.
- **`authsettingsV2` predicted to stay a Modify.** It reports No change.
- **The file-transfer tool repeatedly delivered stale copies** of just-edited
  files to the tower. Claude first blamed VS Code (wrong; Gerard hadn't opened
  the file). From the Bicep fixes onward, every write was re-read from the
  tower and compared byte for byte. **The first write wasn't checked, so
  `52bbfc3` shipped this file with two unfilled placeholders
  (`IDENTITY_LINE`, `IDENTITY_BULLET`).** Fixed in this entry's commit.
- **Process:** one early message mixed several changing command sets. Pass 2
  also ran past "if time allows" without a stated plan, until Gerard asked
  where the day stood.

### Session — September 29, 2026 — row 15 verified alone; blob and container soft delete on

**Claude designed the tests and verdict queries and wrote the Bicep and doc
edits in this entry. Gerard made the soft delete decisions and ran every Azure
CLI command and the deployment.** A split day: the rest went to the tower
rebuild. Started from the Sep 28 handoff and the Todoist punch list, which
agreed. Claude couldn't see git this session: the bridge mounted only
`ai-103`, and the repo root is one level up. Granting `geoste-portfolio`
instead would allow read-only git checks. The question tool's answer was lost
to an app disconnect once (as on Sep 25). Gerard re-supplied it, and
decisions went to plain text after that.

**Row 15, failure path (about 24 h after the Sep 28 deletes): passed.**
Paused `process_upload`, waited, and confirmed the pause with `appsettings
list`, per the Sep 25 caveat. Uploaded `row15-retest-fail.png` **without**
`topic` ($0), peeked it at `dequeueCount` 0 (15:39:55Z), deleted the blob, and
un-paused by deleting the setting at 15:48:26Z. Try 1 at 15:48:50Z, try 2 at
15:50:33Z: **+103 s, not 10 min.** **Zero** `AuthorizationPermissionMismatch`
rows, searched across every column of `AppExceptions` and `AppTraces`. Moved
to `upload-events-poison` at 15:50:33Z and peeked there.

**Row 15, scale-from-zero: passed.** The first test's host was started by the
un-pause, so it said nothing about scaling from zero. Claude caught that from
the `QueuesOptions` startup trace. After about 50 min idle, Gerard uploaded
`row15-scale0.png` with a topic at 16:40:04Z. A **new host started at
16:40:20Z**, `process_upload` **Succeeded** in 43.9 s, and the result is
`results/row15-scale0/20260929T164105Z.json`. **RBAC row 15 is verified:** the
custom role alone does everything the two built-ins did. Rollback to `46bdbd6`
is no longer needed.

**Blob soft delete: done** (Phase 2 Backlog; overdue since the Function began
writing results on Sep 24). Gerard's decisions: **7 days**, and **container
soft delete too**, because deleting a container bypasses blob soft delete.
`storage.bicep` changed from "declared as found" to on. The what-if matched the
register plus exactly one new Modify on `stiipdevwus01/blobServices/default`:
7 modify, 21 no change, 11 Unsupported, 2 to ignore. The 11 role-assignment
diagnostics include the custom role and neither retired built-in. Deployed
`m11-softdelete-20260929`: Succeeded. `blob-service-properties show`: blob
enabled/7 days/`allowPermanentDelete: false`; container enabled/7 days. Row
16's upload-then-delete method still works with soft delete on, because a
soft-deleted blob is invisible to `get_blob_properties()`.

**Observation, not chased:** each host start logged `QueuesOptions` twice,
about 30 s apart. See Current next action.

**Claude's errors today, for the record:**
- V3 was predicted to return "exactly one row" and returned three; the filter
  also matched the startup trace. The verdict was unaffected.
- The peek query guessed the message `id` field name wrong, and the column
  came back blank. Not needed for the test.

**Left in place:** one test message in `upload-events-poison` (15:50:33Z,
expires with the queue's default TTL); `uploads/row15-scale0.png` and its
result.

### Session — September 28, 2026 — row 15 stage 2b deployed (re-test deferred on purpose); then site cleanup

**Claude wrote the Bicep and doc edits in this entry and did the analysis.
Gerard made both decisions below and ran every Azure CLI command and the
deployment.** Short window: the rest of the day went to the tower rebuild. The
Sunday punch-list task hadn't run (the machine was idle). Gerard chose to skip
it, and Claude read the punch list against STATUS by hand instead.

**Decision (Gerard): split stage 2b.** STATUS's "about 30 min" left out the
tests, and the tests couldn't have proved anything today anyway. Found by
Claude while sizing the session: **IIP Queue Trigger (dev) is a superset of
both built-ins, so there is no test that tells it apart from them.** That
holds before the deletion, which is why stage 2a's "confirm effective first"
step couldn't be done as a test and was satisfied by elapsed time (3 days),
and after it, while the deletion propagates. A pass at +30 min could have
been leftover built-in permissions. So the build happened today, and the test
waits until the propagation window has surely closed.

**Done:**
- `rbac.bicep`: `functionQueueReader`/`functionQueueProcessor` removed, their
  two `roleIds` entries retired (GUIDs kept in a comment), the stage log and
  the row 15 header rewritten.
- **What-if: exactly as registered.** 6 modify (all registered), 22 no change,
  **11 Unsupported** (13 → 11, both built-ins gone), 2 to ignore, and the role
  definition `=`. Claude checked it line by line against the register.
- **Deployed** `m11-row15-stage2b-20260928`: Succeeded.
- **Built-ins deleted by hand** (Incremental never deletes), by role GUID,
  filtered to `id-iip-dev-wus-01`'s principal so Gerard's own row 18 Reader
  on the queue was untouched. Before: 3 rows, as expected. After (about 09:00
  local, 16:00Z): **1 row, IIP Queue Trigger (dev)**.
- `infrastructure/iip/README.md`: Unsupported count 13 → 11.
- RBAC row 15 now shows the one custom role, marked unverified until the re-test.

**Read-only work while Gerard was on the other PC (his pick):** the Todoist
role-GUID audit and the token-undercount diagnosis. Findings are in
`Claude outputs/2026-09-28-unattended-findings.md`. No Azure calls, and no
repo changes beyond this commit.

**Afternoon, not IIP: ostebovik.net cleanup** (Claude wrote the changes and
tested them headless; Gerard found the issues noted, made the calls and
pushed). Commits `8104f8c`..`cab4706`:
- M9 shown as Complete.
- The claim that two site lines were stale corrected in three docs; they had
  been fixed Sep 21, in `5fccd4a`.
- Tracking on every page via `js/telemetry.js`; it had been on the homepage
  only, so every visit looked like a bounce.
- Three orphaned project pages removed. They carried a wrong name and a wrong
  GitHub account.
- One shared nav; the AI page was missing from every menu (Gerard found it).
- Phone layout fixes in `css/mobile.css`.
- Owner-browser opt-out (`/?internal=1`).

Open site items live in Todoist, not here. The first is Gerard's find: the
homepage shows no menu on phones, so it has no path to the resume.

### Session — September 25, 2026 — row 16 verified; row 15's failure path found broken and fixed

**Claude wrote every doc edit and the Bicep in this entry, and did the analysis
and test design, except where a design is credited to Gerard below. Gerard
made every decision named below, ran every Azure CLI command and deployment,
and caught two of the problems himself: the what-if's unregistered diffs, and
the empty peek before R2.** Two app-side disconnects before 10:15 lost the
first run's questions and answers. The session restarted from the handoff, and
decisions were asked in plain text from then on. Claude kept running notes in
`Claude outputs/2026-09-25-session-notes.md` (gitignored).

**Housekeeping.** The VS Code "Initialize Azure Functions project" prompt
appeared because `40f9199` added `function/host.json`. Gerard dismissed it;
`.vscode/` is gitignored, and initializing would add a second, untested deploy
path. The previous entry's step 4 (project-instruction key files) was already
done.

**Row 16 verified.** The method is Gerard's upload-then-delete idea. Claude
added pausing the Function (`AzureWebJobs.process_upload.Disabled`), which
removes the race. A real Event Grid message named a deleted blob, and
`get_blob_properties()` raised on both tries. The host logged the move to
`upload-events-poison`, and the message was peeked there. Two tries, not the
row's "five": five is the runtime default, and `host.json` says 2. The test
needed **row 18** (Gerard: Storage Queue Data Reader on both queues, CLI, not in
Bicep; kept as an operator role). Model cost $0 throughout. **Method caveat:**
confirm the pause with `appsettings list` about 2 min before uploading. One
re-test didn't, and was voided.

**Found: a failed message couldn't be released.** Failed tries retried after
**10 min, not 1**, each time with a 403 `AuthorizationPermissionMismatch` from the
queue service. The stack trace (`QueueProcessor.ReleaseMessageAsync` →
`QueueClient.UpdateMessageAsync`) identified Update Message. Microsoft's
permissions table maps it to `messages/write`, which row 15's documented
minimum (Reader + Message Processor) lacks. There's a latent risk too: the
listener renews visibility every 5 min during a run with the same call, so a
run over ~10 min could be processed twice.

**The fix, and a detour.** Gerard chose a custom role (option a) over the
built-in Contributor, ending as one role reached in two stages ("A then R",
his reasoning: cleaner, one point of change). Stage 1, **IIP Queue Trigger
(dev)** with `messages/write` only, was deployed as
`m11-row15-stage1-20260925`. The re-test **still got 403, 65 min after
assignment.** A temporary built-in Contributor fixed it within ~20 min, which
pointed at the custom role. A probe on Gerard's own identity (poison queue,
`az storage message get`/`update`) showed the custom role **works**: update
allowed with it, refused without it (a negative control, run in plain text at
Gerard's option 1). With Contributor removed, the Function passed at 20:14Z
(inconclusive: only 6 min after the removal) and **cleanly at 21:00:28Z: no 403,
retry at +100 s.** **The 65-min delay is open:** a slow custom-role assignment
for a managed identity, or a permission refresh triggered by the Contributor
add and remove. It's recorded both ways; not claimed either way.

**Claude's errors today, for the record:**
- Called row 8 "unproven"; it was confirmed on Sep 24, and today's check was a
  re-check.
- Two "Expected" outputs were wrong (`role assignment create` doesn't return
  the role name; `appsettings set` hides values).
- The first 403 diagnosis was right about *what*, but the fix had to be proven.
- Probe P0 had no negative control until N1.
- One verdict query started after try 1, and missed it.
- The upload came too soon after a pause (the voided run).

**What-if, first since the M11 deploy.** The stage 1 what-if showed the create
and 13 Unsupported, as expected. It also showed **8 unregistered diffs**, none
from today's change:
- `appi-…` `+Flow_Type`/`+Request_Source`;
- `func-…` `+siteConfig` ×3, and `~deployment.storage.value` (literal vs
  `reference()`);
- `func-…/config/appsettings` `+` block;
- `stiipdevwus02/blobServices/default` `-deleteRetentionPolicy`;
- the `app-package-…` container `-defaultEncryptionScope`/`-denyEncryptionScopeOverride`.

The last two are the writable class, to be declared as found. Next action, item 2.

**After the wrap-up (14:20-14:35), two more changes (Gerard's choice):**
- **Stage 2a deployed** (`m11-row15-stage2a-20260925`): the custom role expanded
  in place to the full queue-trigger set, with the built-ins still assigned.
  It was deployed now so the propagation wait happens over the weekend.
- **The `what-if` register caught up.** Six rows were added (appi `Flow_Type`/
  `Request_Source`; func `siteConfig` ×3; func `deployment.storage.value`;
  func `appsettings`; and two fixed rows), and `stiipdevwus02`'s
  `deleteRetentionPolicy` and the package container's encryption-scope pair
  were declared as found. The what-if before the deploy **matched the
  register exactly**: 7 modify (the role definition + 6 registered), 13
  Unsupported, 2 to ignore, and both `stiipdevwus02` entries now `=`.
  Gerard reviewed it first; Claude checked it line by line.

**Cleaned up:** the temporary Contributor on the Function (removed ~20:08Z);
Gerard's temporary Message Processor and custom role on the poison queue.
**Left in place:** 6 test messages in `upload-events-poison` (17:41:38Z to
21:02:08Z), which expire 2026-10-02; one "missing topic" result, `results/row16-retest5/20260925T203810Z.json`.

### Session — September 24, 2026 — housecleaning, then M11 pass 1 built, deployed and working end to end

**Claude wrote every doc edit, all the code and all the Bicep in this entry, and
ran the offline checks. Gerard made every decision named below, and ran every
Azure CLI command, commit and deployment.**

**Housecleaning, first.** Stale lines found and fixed:
- STATUS.md's Sep 16 status paragraph, M7 still unticked, and a Key resources
  table missing M9;
- phase2-orientation.md's M10 bullets, the M11/M12 table rows, the backlog
  header and the doc table;
- m7-orientation.md's checklist item 7;
- in Todoist: 3 tasks closed and 4 annotated.

Gerard's project-instruction edits (key files, the M9 identities) were handed
to him. Commit `a184630`.

**`versionUpgradeOption`: decided and deployed.** `OnceCurrentVersionExpired` on
all four deployments, now set per deployment (Gerard). It's a fourth option the
original task had missed. The first `what-if` exposed three unregistered but
writable storage properties, which were declared as found. Verified afterwards:
gpt-5-4 is still on `2026-03-05`, and the `what-if` shows the register only.
Commit `c923daa`.

**M11 decisions (Gerard):**
- remote build first;
- Python 3.14;
- the event queue on `stiipdevwus01`, with queue-scoped Function roles;
- the poison queue declared in Bicep, with Message Sender on it only;
- the topic carried as blob metadata;
- one agent per upload (D-M11-3);
- row 14 moved to account scope (below).

**M11 pass 1 (upload → result), built and working:**
- `function/` holds the code (`b713df9`), with the Function's requirements
  fully pinned to Gerard's venv (`577bad3`).
- One change to certified code: `expected_audit` is now optional (own commit, `97038fb`).
- A live laptop run of the handler matched item4's key.
- The Bicep adds `app.bicep`, `eventsub.bicep`, the two queues, and RBAC rows 7,
  8, 12 and 14–16, all priced first.

**Row 14 needed account scope.** The event subscription failed 3/3 over about
20 minutes with "Managed Identity Authorization Error". The queue-scoped grant
existed; Gerard confirmed it with `az role assignment list`. Hypothesis (Claude):
Event Grid checks the identity when it creates the subscription, against the
destination's `resourceId`, which is the account; Microsoft Learn also says "on
the storage account". Gerard approved widening the role. The redeploy succeeded
first time, and the orphaned queue-scoped grant was deleted. Recorded in
`rbac.bicep` and the RBAC model.

**First light:** upload → Event Grid → queue → Function → agent → result in
**46 s**, cold start included. The remote build succeeded first time. Both
Azure runs matched item4's key (run 2 on the committed code, `2ac2c34` +
`40f9199`). Settled by evidence:
- **Event Grid writes base64 JSON** to the queue.
- Rows 4, 5, 6, 7 and 15 are confirmed. Row 7 needs **no** Queue Data
  Contributor.

**Defect found in the Function's first result, fixed in its own commit
(`2ac2c34`):** `provenance.py` recorded `git_dirty: false` where git doesn't
exist. It now records None plus a reason. Laptop records are unchanged.

**Row 8 confirmed.** The Entra-only App Insights received 491 traces and 2
requests in 3 h. One `ConnectionAbortedException` at 19:07:19Z has no operation
name and falls 4 minutes before the first upload, inside the deploy window:
likely host noise at deploy time (an inference from the timing, not a traced
cause). Claude's `-o table` in the first query printed nothing even though rows
existed, and `-o json` showed them.

**STATUS.md split:** Aug 10 – Sep 16 moved verbatim to `STATUS-archive-m7.md`
(hash-checked). The file went from 5,527 lines to about 1,040.

**Claude errors this session:**
1. Ended a turn on a status message with two questions buried in its prose.
   Gerard had to prompt a restart, and the rule is now "question tool, or
   WAITING ON YOU".
2. Wrote that D-M11-1 (b) "dissolved" the M12 inbound question. It moved the
   question to the storage account; corrected the same turn.
3. Said to drop `python-dotenv` from the Function. Six modules import it;
   corrected before any deploy.
4. Timed "3.14" on a 3.14.0 release candidate without noticing; re-measured on
   3.14.7.
5. Wrote row 14 at queue scope, which cost three failed deploys and about 20
   minutes.
6. Gave `-o table` for an App Insights query. Its nested output printed
   nothing, and briefly looked like "no telemetry".

### Session — September 23, 2026 — the `listKeys` caller named, the judge test-retest, item7 becomes a rate, and M10 closed

**Claude drafted this entry and every doc edit in it, and proposed the VS Code
hypothesis (Sep 22). Gerard ran every Azure CLI command, supplied the Sep 22
evidence from the previous chat, and caught that the handoff never reached the
repo.**

**The session opened on a process failure.** Sep 22 closed with a "threads for
next time" list that lived only in the chat's closing summary. `## Current next
action` was not replaced after the day's last commit, so it still said "read
the acceptance run", and nothing from the late Sep 22 work was in this log
(now bracketed onto the Sep 22 entry). A new session reads the repo, not the
last chat: it rebuilt the agenda from stale docs and re-questioned a finding
Gerard had already settled. The same summary gave HEAD as `5498ece`; the real
hash is `5798ece` — typed, not copied. New end-of-session rule in
`m7-orientation.md`: the closing summary is derived *from* `## Current next
action`, and hashes are copied from `git log -1 --oneline`.

**The `listKeys` caller is Visual Studio Code.** Evidence, strongest first:
- **appid.** Every `Microsoft.CognitiveServices/accounts/listKeys/action` row in
  a 2-day window carries `claims.appid` `aebc6443-996d-45c2-90f0-388ff96faa56`,
  which Microsoft Learn's first-party app list names as Visual Studio Code;
  caller Gerard's account. (`az ad sp show` finds no service principal for it:
  VS Code is a Microsoft client with none in the tenant. Expected.)
- **Cadence.** Sep 22 baseline: calls arrive in pairs a fraction of a second
  apart, on a fixed 14m42s timer (20:19:37, 20:34:18, 20:49:00, 21:03:42 UTC).
  Not a person, not event-driven.
- **Shutdown.** VS Code closed ~21:35 UTC Sep 22; a query afterwards returned
  nothing. VS Code was not reopened until after attribution on Sep 23.
- **Not determined: which extension.** The Activity Log sees the VS Code client
  ID, which every Azure extension signs in with.
- Also in the window: two `Microsoft.Search/searchServices/listAdminKeys/action`
  rows, appid `c44b4083-…` (Azure Portal) — the portal loading Search pages,
  the same pattern as the Sep 16 note. Benign.

**What it changes** (both now in the `disableLocalAuth` backlog entry):
turning local auth off at M11 has two known breakages, this poll and
`m3_analyze.py`'s exempted pipeline; and the poll leaves `listKeys` with no
audit value, since roughly eight retrievals an hour under Gerard's own identity
hide any genuine one.

**THREAD 2 — the judge test-retest. Pre-registered in Todoist 10:02 MST,
before any data (Claude proposed; Gerard approved and raised n from 20 to 40).**

*The reframe that shaped it (Claude, from existing data):* Sep 9's "gpt-5-4
groundedness 4.0 x10, no variance" was test-retest on ONE fixed text; Sep 22's
two 2.0s were on DIFFERENT drafts, so they could not contradict it. But two
Sep 22 first drafts differing by one clause (runs 1 and 13) had scored 4.0 and
2.0, and across all 39 item7 judge calls in that pass groundedness was 4.0 x32,
2.0 x4, 1.0 x3. So the question became: is gpt-5-4 stable on a fixed text?

*Instrument:* `probe_judge_isolation.py`, judge gpt-5-4, build `2026-03-05`
recorded in every file (`model_builds`, added at `ba54311`), n=40 per text,
all at `ba54311` with a clean tree, 200/200 calls measured, 0 errored.

| Text | Source | Originally | Groundedness x40 | Relevance x40 | all_passed |
|---|---|---|---|---|---|
| A | `20260909-122233` item7 run 1 d1 | 4.0 x10 (Sep 9, gpt-5-4) | 4.0 x38, 2.0 x2 | 1.0 x20, 2.0 x20 | 0/40 |
| B | `20260922-131551` item7 run 13 d1 | 2.0 | 4.0 x38, 2.0 x2 | 2.0 x32, 3.0 x8 | 8/40 |
| C | `20260922-131551` item7 run 15 d1 | 2.0 | 4.0 x29, 2.0 x11 | 2.0 x17, 3.0 x23 | 17/40 |
| D | `20260922-131551` item7 run 1 d1 | 4.0 | 4.0 x37, 2.0 x3 | 2.0 x25, 3.0 x15 | 14/40 |
| E | `20260922-131551` item7 run 2 d2 | 1.0 | 1.0 x23, 2.0 x5, 4.0 x12 | 1.0 x40 | 0/40 |

Files: `20260923-101620`, `-102419`, `-103341`, `-105824`, `-110516`
`_judge_isolation.json`, in that order.

**Verdict, by the pre-registered rule: R2 and R3 both fired.** Every text drew
at least two distinct groundedness scores. Claude predicted R2 with A stable:
B and D unstable was right, A stable was wrong.

**What it means:**
1. **The judge CHOICE stands; two claims about it narrow.** On text A gpt-5-2
   scored 1.0 in 8 of 10 (Sep 9) and gpt-5-4 scores 4.0 in 38 of 40 — still
   clearly the most faithful of the three. But "no variance" and "applies the
   definition on every call" were n=10 artifacts: a 1-in-20 wobble is invisible
   in 10 reads about 60% of the time. Sep 9 was not wrong; it could not see this.
2. **item7's judged verdict is a rate, not a property.** One unchanged draft
   passes 0 to 17 of 40 re-reads depending on its wording. Sep 22's 3/15 (and
   B's 2.0) are fully explained by judge variance on fixed text; no change in
   agent behaviour is needed to explain them. The Sep 11 revisit trigger was
   the judge, not the agent.
   **[Corrected same day, after `4d52012` — the last two sentences overclaim.**
   The agent's draft mix moved too. Counting item7 first drafts that raise
   returns or pricing (regex `bring something back|pricing|better price|return`,
   chosen by Claude AFTER seeing the data, so exploratory, not pre-registered):
   Sep 10 2/15, Sep 11 0/15, Sep 15 5/15, Sep 22 9/15. Across all four passes,
   those drafts passed first time 4 of 16; drafts without it, 0 of 44 — matching
   text A's 0/40 and B–D's 8–17/40. So a first-draft pass needs BOTH a draft
   that raises the topic (the agent's variance) AND a favourable read (the
   judge's). Sep 22's 3/15 is what nine such drafts at ~25–30% produce. Neither
   factor alone explains it.**]**
3. **On an unanswerable query, groundedness imports relevance.** E is the one
   draft that makes no unsupported claim — it describes what the store does
   offer — and it draws gpt-5-4's LOWEST groundedness: 1.0 in 23 of 40, and 22
   of those 23 reasons say "not responsive", "unrelated" or "irrelevant" (the
   23rd says it "does not answer" the query). Both of A's 2.0 reads
   say "off-target relative to the query". The failure Sep 9 attributed to
   gpt-5-2 is present in gpt-5-4 at a lower, text-dependent rate.

**Decision (a), Gerard:** item7's judged first-draft row is reported as a rate,
not scored against the answer key; its deterministic rows stay pass/fail. Not
circular in the way re-keying from the Sep 22 run would have been: the evidence
is this pre-registered fixed-text measurement, with no agent in the loop.

**Decision (a) implemented (afternoon).** `m7_orchestrator.py`: item7's key
gains `mode: "rate"`, `first_pass_flag_at: 9`, `flag_defined_for_runs: 15`; for
a rate item `text_matches_expected` is None (not asserted) and the per-run line
says so. `probe_orchestrator_stability.py`: `summarize()` prints and records a
`rate_item` block — count, threshold, whether the flag applies and whether it
fired. The original first_pass/final_passed/redrafts keys are kept as the
registered expectation, unasserted. **Gerard chose the threshold** (9 of 15) from
three offered. Claude wrote the code; `summarize()` was checked offline against
the Sep 22 file (3/15 within range; a forced 10/15 flags; a 7-run batch reports
"not evaluated"). Known wart, left alone: the pre-existing STABLE/NOT STABLE
label still prints for item7 and means only "80% of runs agreed", which for a
rate item says nothing.

**Smoke of the rate code (live, one run):** `20260923-115337_orchestrator_stability.json`
at `287d740`, clean tree, build `2026-03-05`. The record carries the rate key
with `text_matches_expected: None`; the summary's `rate_item` reads
`flag_applies: False` for a 1-run batch. Both code paths confirmed.

**THREAD 3 — M3's migration, and M10 closed.**
- **Service auth** (`fcc55b6`): `submit_analyze()` and `poll_result()` send an
  Entra ID bearer token for `cognitiveservices.azure.com/.default` — the scope
  the Content Understanding 2025-11-01 REST reference names — refreshed per
  request. The module docstring's old claim that Entra ID "doesn't apply" on a
  laptop was corrected: it conflated managed identity with Entra ID.
- **`--blob`: decision (A), Gerard** — a user-delegation SAS
  (`--as-user --auth-mode login`), chosen over downloading and sending inline.
  **Claude's reading found the Todoist task wrong on one point:** it did NOT
  amend the RBAC model — Gerard already held Storage Blob Delegator and Storage
  Blob Data Contributor on `stiipdevwus01`. Letting the Foundry account's own
  identity read the blob was ruled out: no Microsoft documentation shows it for
  Content Understanding.
- **Verified live on both paths:** `20260923-121256` (`--file`) and
  `20260923-121335` (`--blob`) against the July 27 key-based run: all 21
  non-generative extracted values identical, markdown identical in length
  (4,186 characters). Only the 11 model-written KeyPhrases differ, in wording
  — and today's two keyless runs differ from EACH OTHER in 2 of them, so that
  is generation variance, not auth.
- **M10 clause 1** (`08bc35c`, own commit): `get_subscription_key()`,
  `get_storage_key()` and `get_search_admin_key()` removed with dead imports in
  nine scripts. Import check on the eight import-safe modules passed.
  Gitignored `m6_probe.py` fixed to match; gitignored `tester3.py` left broken.
- **M10 clause 2:** `m6_generate.py` hand-run (`20260923-122420_generate_results.json`,
  28 answers, 14 per model, none empty) and `m6_probe.py` hand-run — both keyless.
- **M10 COMPLETE. Gerard moved the marker to M11.** Every clause of the
  done-when is met and M3's stated exception is closed.

Claude wrote all the code and doc changes in thread 3. Gerard chose (A), ran
every command, and made the milestone call.

**M11 PREP — the survey, started the same afternoon (`m11-prep.md`, `390eb55`).**
Claude surveyed the M7 code paths and Microsoft Learn; nothing was built.
- **Headline: the M7 code assumes a laptop.** `get_endpoint()` shelled out to
  `az`, and `m7_evaluator_tool.py` calls it at module scope — so importing the
  evaluator in a Function would fail while the host loads. **Fixed at
  `71b90b9`:** an `AIF_ENDPOINT` setting wins; `az` is the fallback. Verified
  with a deliberately bogus account name (no `az` error) and a live `m6_probe`.
- **Two keys hiding in the textbook design** — the blob trigger's
  `blobs_extension` webhook key and Easy Auth's client secret. **Gerard chose
  the keyless alternative for both:** D-M11-1 (b) Event Grid → storage queue →
  queue trigger (no inbound endpoint; the M12 inbound-restriction question
  dissolves); D-M11-2 (b) a dedicated `id-iip-dev-wus-03` as a federated
  credential on the app registration.
- **Probes (Gerard ran all three):** `westus` supports Flex Consumption, with
  Python 3.10–3.14; `import m7_orchestrator` takes **4.57 s** on the laptop
  (`openai` 2.07 s, `azure.ai.evaluation` 1.51 s) against a 30 s ceiling; the
  dependencies install to **235 MB**. Sizing that surfaced the real risk:
  remote build has a documented **60-second** timeout.
- **Claude error:** drafted a placeholder where a commit hash belonged in
  `m11-prep.md`, the third hash slip of the day; caught before commit and
  replaced with `71b90b9` from `git log`.

Recorded as dated corrections in `m7-orientation.md` (two closed backlog
entries), `m7-writeup-draft.md` sections 4 and 5, `phase2-orientation.md`'s M10
bullet, and `m7_evaluator_tool.py`'s docstring (own commit). Cost ~780K tokens,
~$3 estimated.

**Claude errors this session:** (1) questioned the validity of the Sep 22
shutdown test without knowing it was Claude's own design and already settled; (2) attributed the `5498ece` hash to a typo of
Gerard's — it was in Claude's summary; (3) put a `<placeholder>` inside a
copy-paste command block, which Gerard ran as written; (4) said "eight" tracked
scripts import `get_subscription_key` unused — it is nine; (5) reported
text B's relevance as 3.0 x9 in the interim read — it is x8; (6) buried the
item7 decision inside an analysis instead of asking it as a question — Gerard
had to find it, and chose with less confidence than the decision deserved; (7) counted E's
"irrelevant" reasons as 16 of 23 with a substring match that also hit "offer"
— the correct count is 22 of 23; (8) typed a commit hash from memory into a
Todoist comment ("3de3…") hours after writing the rule against it — corrected
with the real `67d0e31`; (9) estimated m6_generate at 13 questions — it has 14.

### Session — September 22, 2026 — M10: the keyless migration, and four probes that reshaped it

**Claude wrote every probe, the migration script and all code changes in this
session. Gerard directed the work, ran every Azure CLI and Python command, made
the scope decisions, and caught the Cognitive Services User deprecation that
Claude had wrong.**

**Plan on entry:** housekeeping, then the two tests at the top of `m10-prep.md`
— Vision Read, then the Search token. Both ran, plus two more that the first
pass of review showed were needed.

**Before anything ran, five contradictions surfaced in the docs** — the M8
bullet contradicting the M9 bullet four lines above it, two verbatim duplicate
backlog entries, the M10 script count, an unsatisfiable backlog precondition,
and a test design that could not distinguish its own outcomes. All fixed the
same day; see `phase2-orientation.md`, `phase2-rbac-model-draft.md` and
`m10-prep.md`.

**The test-design problem was the important one.** `m10-prep.md`'s Group C test
said a 401/403 meant the free tier does not support keyless. But the RBAC model
deliberately assigns nothing on Search, so the run would have 403'd for a
missing role and been read as a tier limit — pointing M10 at a service recreate
on a paid tier, a one-way door with a recurring bill. Search Index Data Reader
was assigned first. That single change is what made the result mean anything.

**The subscription-scope Foundry User grant was removed BEFORE the probes, not
after.** The backlog said to remove it only after M10's acceptance test passed
"on the account-scope grant" — but the broad grant silently carries that test,
so the condition could never be met. Removing first (one reversible command)
put Gerard and `id-iip-dev-wus-01` on the same grant at the same scope, which
is what makes the results transfer to the Function.

**Results — four probes, all green:**
- **Vision Read:** Foundry User covers it. Row 4's first half closed.
- **AI Search, free tier:** keyless query works. `m10-prep.md`'s "PROBABLE
  BLOCKER" retired. The query was carried by Search Index Data Reader, a
  dataAction; Owner inheritance cannot have masked it because Owner has no
  dataActions. Step [3/3] (`get_index`) *did* ride Owner — Claude predicted it
  would fail, it passed, and the reason means it proves nothing about what a
  workload identity could do.
- **Evaluation SDK:** works with `api_key` omitted. Row 4's second half closed.
- **`/openai/v1/` audience:** both `cognitiveservices.azure.com` and
  `ai.azure.com` accepted; a callable works as `api_key`, so no expiry ceiling.

**Migration:** all 12 call sites keyless, committed at `aa96bea`.
`get_subscription_key()` and `get_search_admin_key()` deliberately kept and
unused until the acceptance test passes.

**Scope correction, twice over.** The plan said eleven scripts. `m10-prep.md`
corrected that to ten because `tester3.py` is gitignored. `m6_probe.py` is
gitignored on the same `.gitignore` line and was missed. **Nine tracked.**
It was migrated anyway.

**Two mistakes Claude made and corrected in-session, recorded because the
corrections are the useful part:**
1. Recommended assigning **Cognitive Services User** as the remedy if Vision
   Read 403'd. Gerard remembered it was deprecated. It is: Learn lists it as a
   legacy role superseded by Foundry User. Had the 403 happened, the RBAC model
   would now carry a deprecated role as a documented decision, in resume
   material.
2. Wrote `credential=DefaultAzureCredential()` into the two Evaluation SDK
   sites on an argument about explicitness, overriding the probe's own finding
   that `api_key` should simply be omitted. The SDK's validator rejected it and
   the smoke test caught it. The empirical result was right; the aesthetic
   argument was not.
   A third, smaller one: the first smoke test imported `m6_generate`, which
   runs a full generate loop at module scope. Caught before it ran.

**8x1 smoke before the long pass** (`20260922-114320`, `git_head aa96bea`,
`git_dirty false`): 8/8 deterministic audit rows and 8/8 judged text rows match
the answer key. 366 seconds for 8 item-runs — ~46s each, so the 15-run pass is
~92 min. That is **latency-bound, not TPM-bound**: the 300K TPM quota increase
does not shorten it, and the old ~95 min figure stands.

**THE ACCEPTANCE PASS — `20260922-131551_orchestrator_stability.json`.** 15 runs,
all eight items, 89.5 minutes, `git_head aa96bea`, INSTRUCTIONS_V4, temp 0.0,
judge and model both `gpt-5-4`.

- **Deterministic layer: 240/240.** Every audit row on every item on every run
  matches the key, including the three carrying the deliberate flaws (item3
  `text_legible`, item4 `brand_consistent`, item5 `info_accurate`). This is the
  layer that evidences the migration: it runs at temperature 0 / seed 42 through
  `m7_legibility_check.py` and `m7_cv_audit_tool.py`, the two files whose auth
  changed most.
- **Judged layer: 7 of 8 items at 15/15.** item7 came in at 12/15.
- **M10's acceptance test is CERTIFIED on this basis** (Gerard's call). The
  migration changed how calls authenticate and nothing about what they return.

**item7 at 12/15 is NOT a migration regression, and the Sep 11 punch list said
so in advance.** First-draft relevance across 15 runs:
`[3,2,1,2,3,2,1,2,1,1,2,3,2,2,3]` — four draws at 3.0, three of which passed
(run 15 drew relevance 3.0 and still failed on groundedness 2.0). The Sep 11
task recorded item7 recovering **once in 18 runs** and said explicitly: *"if a
future pass shows item7 recovering at a materially higher rate, revisit whether
it should be re-registered the way item6 was on Sep 9."* **1-in-18 then, 3-in-15
now. That trigger has fired.** The key was NOT changed on the strength of this
run — certifying a migration and rewriting the answer key it was judged against,
using the same run, is circular. Re-registration needs its own evidence and its
own decision. Logged in Todoist.

**A SECOND shift that nobody pre-registered: item7's groundedness moved.**
Values `[4,4,4,4,4,4,4,4,4,4,4,4,2,4,2]` — two 2.0 draws. The Sep 9
judge-isolation probe recorded item7 on gpt-5-4 as groundedness 4.0 x10, *"no
variance"*, and that was the evidence for choosing gpt-5-4 as judge at all.
Three candidates, cheapest first: (1) the judge deployment's model build changed
under us — check `versionUpgradeOption`, because if it is
`OnceNewDefaultVersionAvailable` the judge moves without anyone deciding, and
every longitudinal comparison in the M7 write-up is then comparing two judges;
(2) the 500s (below) injected retried samples; (3) real variance that n=10 on
one item never surfaced.

**Transient judge 500s, invisible to the results file.** At least one
`InternalServerError: The model produced invalid content` fired from
`azure.ai.evaluation._legacy.prompty` during run 2 and was retried internally by
the Evaluation SDK ([0/10], 3s backoff); the run completed with all three tools
called. **The probe cannot see these** — the retry happens below `unmeasured()`,
which only catches runs that complete without a verdict. The only trace is
terminal scrollback. A retried call is a fresh sample, so this is a plausible
contributor to the variance above and there is currently no way to count it.

**`stop_on_pass` STILL has zero observations** after another 120 item-runs. The
three item7 first-draft passes are not stop-on-pass — that needs a pass *after*
a failure. Unobserved now across 33+ runs.

**PROCESS FAILURE, Claude's: `git_changed_during_run: True`.** Claude proposed
doing the documentation pass while the 15-run measurement was in flight, and
that tripped the provenance guard built to prevent exactly this. `git_at_end`
records `.gitignore`, `STATUS.md`, `m10-prep.md`, `phase2-orientation.md`,
`phase2-rbac-model-draft.md` and the 8x1 results file as dirty at the end.
**The measurement stands, for a specific and checkable reason: not one `.py`
file is in that list** — nothing under `ai-103/scripts/` changed, and `git_head`
is identical at start and end, so the code that ran is byte-identical to
`aa96bea` throughout. Recorded rather than waved off, because the flag is
permanently in the results file and a reader deserves the reason. **Lesson: do
not touch the repo while a measured run is in flight, even documentation. The
guard cannot tell docs from code and should not have to.**

**Governance findings, both new and both in the Phase 2 backlog:** Foundry
User's dataAction is the wildcard `Microsoft.CognitiveServices/*`, and its
actions include `listkeys`. Keyless code does not remove the permission to
retrieve a key — `disableLocalAuth` does. And Principle 2 cannot be satisfied
for row 4 while one shared AIServices account serves both OpenAI and Vision;
that is now stated as an accepted trade-off rather than left implicit.

**[Added 2026-09-23 — late Sep 22 work that never reached this log.** Committed
at `5798ece`, after the entry above was written: (1) `provenance.deployment_builds()`
now records each deployment's model build and `versionUpgradeOption` at run
start; (2) the Activity Log shows no `Microsoft.CognitiveServices/accounts/deployments`
write between Sep 7 and Sep 21 from any caller, and the live build reads
`2026-03-05`, so the Sep 9, 10, 11, 15 and 22 runs are comparable; (3) M10's
done-when amended to name `m3_analyze.py`'s own pipeline as a stated exception.
Claude wrote the code and the amendment. Gerard directed the work, ran every
command, chose to amend the done-when rather than leave the milestone open, and
pushed back on certifying data whose provenance was in question — which is
what surfaced (1) and (2). The commit message has the full reasoning. Why this
bracket exists: see the Sep 23 entry.**]**


### Session — September 21, 2026 — M8: the IaC baseline, written and what-if'd

**M8's Bicep is written and builds warning-clean.** `what-if` reports 3
resources to modify and 6 no change, and every remaining diff is either
intended or a property no template can assert. The register of accepted diffs
is `infrastructure/iip/README.md`; it is the complete expected output, so
anything else in a future run is a real change.

Gerard ran every Azure CLI call — the property dump, three build/what-if
cycles. Claude wrote the Bicep, the README and this entry.

**Structure.** `infrastructure/iip/` — `main.bicep` (orchestrates only),
`dev.bicepparam`, and `modules/{storage,keyvault,search,foundry}.bicep`,
matching the portfolio prod stack's shape rather than inventing a second one.

**The finding worth keeping: `what-if`'s noise disclaimer hides real
changes.** The first run showed 7 resources to modify. Five of those diffs
looked exactly like provider noise — a `-` on a property reading like a status
field, on a resource nobody meant to touch — and were writable properties the
template had silently dropped:

| Property | Consequence had it deployed |
| --- | --- |
| `accounts/properties.defaultProject` | data-plane calls without an explicit project name break |
| `accounts/properties.associatedProjects` | `proj-iip-dev-wus-01` detached from the account |
| `deployments/properties.currentCapacity` (x4) | the 300K/30K/10K TPM settings cleared |
| `searchServices/properties.computeType` | the Default vs confidential-compute choice cleared |

**Nothing in the `what-if` output separated those from the two that really
were noise.** The only reliable test is the resource provider's schema: a
property with no `ReadOnly` flag is a property a deployment can clear. Read
`what-if`'s "may contain false positive predictions" banner as a reason to
check each line, not as a licence to dismiss them.

**A related error, made and corrected the same session.** `networkRuleSet.bypass`
on Search was dropped on the stated grounds that it existed only in preview API
versions. It does not — it is absent from `2023-11-01` and present and writable
in `2025-05-01`, which is GA. The module had been pinned to a stale API version
and the missing property was then rationalised as unsupported. Bumping the API
version was the fix. **A "the schema does not support it" conclusion should be
checked against the current API version before it is written down.**

**Three findings about the live resources the docs did not have:**

- **The Foundry subdomain inverts the documented naming exception.** The
  account resource is `aif-dev-wus-01`, without the `iip` token, which is the
  known exception. Its `customSubDomainName` is `aif-iip-dev-wus-01` — *with*
  the token — and that is what every endpoint in `scripts/` is built from. It
  is pinned in `dev.bicepparam`. Left to default it would change the endpoint
  host and break every script at once.
- **`srch-iip-dev-wus-01` was missing the `managed-by` tag** that the other
  four resources carry. The baseline applies the full tag set, so the one
  intended `what-if` change is `+ tags.managed-by`.
- **The `managed-by: bicep` tag has been asserting something untrue since
  July.** Four resources carried it while nothing in the resource group was in
  Bicep. M8 is what makes it true. Recorded rather than quietly fixed.

**Also this session, outside M8:**

- **The stale Claude project doc `claude/2026-09-10-m7-session-prompt.md` was
  deleted**, at Gerard's instruction. Its own rule — promote anything durable
  before replacing — was checked first: `first_text_passed` vs
  `final_text_passed`, judge-invariance, the Plan9 mount failure mode, the
  item6 answer-key trap, the four probe scripts and the redraft cap are all
  already in `m7-orientation.md` or this file. `ACTIVE_JUDGE_DEPLOYMENT` is
  documented at the constant in `m7_evaluator_tool.py`. Nothing lost.
- **The Sunday punch-list scheduled task was rewritten.** It still named
  `m7-orientation.md` as the source of truth and carried a standing assumption
  "He is on M7", so the Sep 20 run seeded all three tasks from the M7 backlog
  and M8 got no slot in the week it was the working milestone. It now reads
  `phase2-orientation.md` for core items and takes its single `[stretch]` item
  from the M7 backlog. Gerard decided the MS Learn video series stays paused
  through all of Phase 2, not merely until M7 was stable. The cache-buster
  warning, freshness gate, no-questions rule and attribution rule were kept
  verbatim.
- **There is no Friday check-in scheduled task.** Only the Sunday punch list
  and the mid-October job-search checkpoint exist. Noted, not acted on.

**Open, and it is a real decision:** M8's done-when in `phase2-orientation.md`
reads "`what-if` shows **no changes**". Azure will not produce that here, for
the reasons in the register. Claude proposed amending it to "no changes other
than the documented provider-owned properties listed in
`infrastructure/iip/README.md`". Not yet decided — it is the standard M9-M14
inherit.

### Session — September 21, 2026 (afternoon) — M9: identities and RBAC, first real deployment

**M9 is complete, and it was the first time any of this left the template.**
Deployment `m9-identity-rbac` succeeded in 39 seconds. Gerard ran every Azure
CLI call; Claude wrote the Bicep, the verification queries and this entry.

**Created:** `id-iip-dev-wus-01` (purpose `function-runtime`) and
`id-iip-dev-wus-02` (`github-deploy`), the `uploads` and `results` containers,
and RBAC rows 2, 4, 5, 6 and 9. All five verified afterwards with
`az role assignment list` — rows 5 and 6 at **container** scope, not account
scope, as the model's principle 2 requires.

**M9's done-when was wrong as written, and was amended before any code.** It
said "the assignments exist and match the RBAC table." Eight of the table's
twelve rows cannot be assigned until M11 creates their scope resources. Gerard
chose to scope M9 to the identities plus every row whose scope exists — the same
correction made to M8's done-when earlier the same day.

**Four corrections to the RBAC model, found by checking before writing.** Full
detail is in `phase2-rbac-model-draft.md`'s new build-time findings section. The
one that matters:

- **Row 9 was marked "(automatic)" and is not.** The Foundry account had zero
  direct role assignments. Microsoft Learn: the automatic Foundry User
  assignment happens only via the portal or Foundry UI, and "doesn't apply when
  deploying Foundry from SDK or CLI". So the project managed identity had been
  running since July without one of the two assignments Microsoft documents as
  the minimum. **M10 would have hit this**, because the keyless migration removes
  the account keys that were concealing it.
- **Row 3 already existed** and is deliberately not in the template: Azure
  enforces uniqueness on the (principal, role, scope) triple, so declaring it
  would have failed the deployment with `RoleAssignmentExists` partway through.
- **Row 2 is redundant today** — Gerard holds Foundry User at subscription
  scope, which is how `m7_orchestrator.py` authenticates. Declared anyway, so
  the narrow grant is in IaC; removing the broad one is backlogged until after
  M10.

**M8 is now tested, not predicted.** The deployment applied the baseline without
recreating anything — the Foundry account and project principal IDs are
unchanged from the morning's dump — and the pinned `customSubDomainName` held,
so `https://aif-iip-dev-wus-01...` is intact. The `managed-by` tag applied to
`srch-iip-dev-wus-01`, which was M8's one intended diff.

**The `properties.endpoint` question is settled empirically.** It was left
undeclared on Search on the reasoning that a search endpoint is derived rather
than settable. The deployment left it unchanged, so the missing `ReadOnly` flag
is a schema inaccuracy. Recorded in the register with the reasoning, because the
method generalises: when a property's writability is ambiguous, prefer the error
that self-corrects.

**One more instance of the same mistake, caught by what-if.** `blobServices/default`
was declared with no properties, purely as a parent for the containers, and
`deleteRetentionPolicy` is writable — the third time in one day that a writable
property left undeclared produced a real diff. Now declared as found. The
standing rule: **declare every writable property you found a value for, or
expect what-if to report it every run.**

**`Unsupported` is not `-`.** what-if reported rows 4, 5, 6 and 9 as
`Unsupported`, naming the cause: the resource ID "cannot be calculated until the
deployment is under way", because each contains `reference(...).principalId` for
an identity the same template creates. Row 2 analysed cleanly — its principal ID
is a literal parameter. Same type, same file, same run: the only difference is
literal versus reference. **`Unsupported` means what-if declined to predict;
`-` means it predicted a removal.** Only the predictions needed checking against
the provider schema.

**Blob soft delete is OFF on `stiipdevwus01`** (`deleteRetentionPolicy.enabled:
false`). Declared as found, not changed. Backlogged against M11, when the
Function starts writing results there and an accidental delete stops being
theoretical.

### Session — September 18, 2026 — short session, one backlog item

**Scope was chosen deliberately small.** One self-contained backlog item with
no Azure calls and no acceptance-test exposure, rather than starting M8.
Gerard chose the item and ran the import check in the Windows venv; Claude
wrote the change, the verification and this entry.

**`cells_correct()` is fixed — judged and deterministic audit cells are now
counted separately.** It iterated all three fields per record, so every
`N/225` and `N/360` figure it produced credited the model with the
deterministic `text_legible` cells. Same defect `probe_fixture_stability.py`
carried until Sep 11, and it got the same fix.

- `cells_correct()` is replaced by `cell_counts()`, returning a `CellCounts`
  NamedTuple: `judged_correct`, `judged_total`, `deterministic_correct`,
  `deterministic_total`. **It carries no combined total, deliberately** — not
  even as a convenience property. A combined number that can be reached for is
  a combined number that gets quoted.
- `MODEL_JUDGED_FIELDS` and `DETERMINISTIC_FIELDS` are now explicit module
  constants, matching `probe_fixture_stability.py`. An audit field in neither
  raises `ValueError` rather than defaulting to judged.

**Verified with no Azure calls**, against
`results/20260910-123321_orchestrator_stability.json` — which is what the
Sep 11 entry predicted, and why the deferral "that would require another
orchestrator run" was wrong when it was made:

| population | all 8 items | matrix (items 1-5) |
| --- | --- | --- |
| old combined | 357/360 | 222/225 |
| model-judged | 237/240 | 147/150 |
| deterministic | 120/120 | 75/75 |

The two populations partition the old total exactly, in both slices. **The
deterministic cells were 120/120**, so the old combined figure was padded by a
population that cannot vary: 357/360 reads as 99.2% where the model's own
score is 98.75%.

**The row figure is untouched: 117/120, as the Sep 11 entry predicted.** A row
matches only if all three fields match, so an always-true conjunct cannot
inflate a conjunction.

**Results JSON keys changed.** `cells_correct`, `cells_total`,
`matrix_cells_correct` and `matrix_cells_total` are replaced by
`model_judged_*`, `deterministic_*` and the two field lists. Runs written
before today keep the old keys, so anything that later reads across runs must
handle both shapes. No script reads them today — checked.

**One verification caveat.** The check that loaded the whole module ran on the
Linux VM behind the folder bridge, which has no azure SDK, so the azure
imports were stubbed. Gerard ran `python -c "import m7_orchestrator"` in the
Windows venv, which closes that gap.

**The rest of this file was swept for the old name, and annotated rather than
rewritten.** Three past entries referenced `cells_correct()`, which no longer
exists in the code: the Sep 11 open-defect pointer, the Sep 11 "never needed a
run" lesson, and the Sep 8 unmeasured-items note. Each now carries a dated
bracket saying what changed on Sep 18; none of the original sentences were
altered, because each was true on the date it was written. **The standing figure
rule in Key Lessons was updated in place**, since that section is live guidance
rather than history: a combined `N/225` or `N/360` is no longer merely
forbidden, it is now unobtainable from the orchestrator.

**Not touched, deliberately.** `probe_orchestrator_stability.py`'s `agreement`
counter still counts passes rather than matches. Separate backlog entry,
separate session.

## Archived sessions

August 10 – September 16, 2026 — the M7 build through its acceptance test, and
the Sep 16 Phase 2 planning session, plus the superseded Aug 12–20 "Next action"
appendix — lives in `STATUS-archive-m7.md` in this same folder. Split out
2026-09-24 (moved verbatim) because this file had grown to about 5,500 lines, 80%
of them closed history. A "see the <date> entry" for those dates resolves there.


July 27 – August 7, 2026 — the M2–M6 build, all milestones complete — lives in
`STATUS-archive-phase1.md` in this same folder. Split out 2026-09-06 to keep this
file to the live milestone. Same repo, nothing lost; open it when you need the
history behind M2–M6.
