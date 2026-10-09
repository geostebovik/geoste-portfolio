# Phase 2 — Conditional Access policy spec (outline)

**Status: DESIGN AGREED ON PAPER, 2026-09-16.** This is the second item on
the Phase 2 entry checklist. Claude drafted the structure and options from
Microsoft Learn. **Gerard chose option (a) for all nine decisions (C1–C9)**,
and added the two notes recorded under the decisions table. *(2026-10-09: deploy steps 1-6 are done — the baseline is
live, CA001 is On and passed T1-T6, and the policies are exported. Only C9,
the rollback, remains: planned for the week of 2026-10-26. See the progress
notes below. The 2026-10-08 version of this line, "CA001 is not built yet",
was stale by that afternoon.)* Deployment happens during the
30-day Entra ID P2 trial, which starts only once the results page and its
sign-in exist (Todoist task; turn recurring billing off right after
signup).

> **Progress, 2026-10-07 (Claude drafted; Gerard made every decision and ran
> every step).**
> - **Deploy step 1 done:** the P2 trial started 2026-10-07 (recurring billing
>   Off by default; ends 2026-11-06).
> - **Deploy step 2 done (C2):** `bg-admin-01@letter7.onmicrosoft.com`,
>   cloud-only, Global Administrator (permanent, active, not PIM), password on
>   paper only, one device-bound **passkey in Microsoft Authenticator**
>   (Android). Proven: it signed in to the Entra admin center with the passkey
>   alone. For that, **Passkey (FIDO2)** was enabled for All users; the
>   default passkey profile is device-bound, attestation enforced, no key
>   restrictions (Microsoft's suggestion for admin accounts).
> - **Known gap in C2, accepted for now:** one method, on the same phone as
>   djeemunee's Authenticator, and the tower has no Bluetooth, so the passkey
>   only works on the phone itself. Fix: a USB FIDO2 key as a second method
>   (Todoist, p2).
> - **Found:** an authentication-methods change took **more than 6 and less
>   than 47 minutes** to reach sign-in (error 135016 "FIDO sign-in is disabled
>   via policy" at 12:33-12:34, success by about 13:15). Every policy change
>   in M13 gets a wait before it is tested.
> - **C7 amended**, and deploy step 3 reordered: see both, below.

> **Progress, 2026-10-08 (Claude wrote the steps from Microsoft Learn; Gerard
> ran every portal step and made every decision).** Times are Phoenix (UTC-7).
> - **Deploy step 3 done: security defaults is OFF and the baseline is ON**
>   (11:14). All four policies were verified with What If and with real
>   sign-ins (table below).
> - **3a, methods:** legacy MFA had all four methods ticked (call, text, app
>   notification, app code); self-service password reset was None. Microsoft
>   Authenticator was enabled for All users, mode Any, Authenticator OTP Yes
>   (09:50). The legacy methods were unticked and the migration set to
>   **Migration Complete** (10:12). `djeemunee` signed in with Authenticator at
>   11:07, past the lag window, so the new policy alone carries his MFA. SMS
>   and Voice stay **off**: weaker, and the portal says users enabled for them
>   get an unrestricted system-managed passkey profile.
> - **Found:** the per-user MFA page showed Microsoft's own forced migration
>   "in progress" ("may take up to one hour"; the legacy policies were
>   deprecated 2025-09-30). It didn't block the Authenticator save.
> - **3b, the baseline:** built from the Secure foundation templates, created
>   in Report-only while security defaults was still on. **That works:** the
>   portal blocks only the On state ("You must first disable security
>   defaults"). This settles the "Unverified" in step 3b below.
> - **Found: a template excludes the person who creates it** (Microsoft Learn,
>   "Conditional Access policy templates"). Each policy came out excluding
>   `djeemunee`, the daily admin account it most needs to cover. Fixed on all
>   four by hand: `djeemunee` removed, `bg-admin-01` added.
> - **Found: the Azure management template targets "Azure Resource Manager"**,
>   app ID `797f4846-ba00-4fd7-ba43-dac1f8f63013`, the app older docs call
>   "Windows Azure Service Management API". Same app, new display name.
> - **3c:** security defaults Disabled, then the four policies On (last save
>   11:14). Verified from 12:01 (past the 47-minute lag), sign-in log →
>   Conditional Access tab, every row as expected:
>
>   | Sign-in | CA900 | CA901 | CA902 | CA903 |
>   |---|---|---|---|---|
>   | `djeemunee`, portal.azure.com | Not applied | Success | Success | Success |
>   | `bg-admin-01`, entra.microsoft.com, passkey (phone) | Not applied | Not applied | Not applied | Not applied |
>   | `iip-ca-test`, the results page (Authenticator prompt) | Not applied | Not applied | Not applied | Success |
>
>   What If (Azure Resource Manager, Windows, Browser) agreed beforehand:
>   `bg-admin-01` none; `djeemunee` CA901-CA903; `iip-ca-test` CA901 and CA903.
> - **3d:** Microsoft-managed policies **0** right after security defaults went
>   off (11:14). Microsoft creates them on its own schedule; check again before
>   C9 (Todoist, Nov 2).
> - **Design change for step 4, T2 (Claude, not yet run):** with CA903 on, a
>   password-only sign-in can't reach the results page whatever CA001 says, so
>   T2 as written can't happen. T2 becomes: `iip-ca-test` with an
>   **Authenticator push** (MFA, but not phishing-resistant) → Report-only
>   "would require authentication strength"; On → blocked until the passkey is
>   used. The test matrix is amended to match.

> **Progress, 2026-10-08 afternoon (Claude wrote the steps; Gerard made every
> decision and ran every step).**
> - **`iip-ca-test`'s passkey (C4):** device-bound, in Microsoft Authenticator
>   on the same Android phone (Gerard's choice). For a test user the
>   single-phone risk is accepted; it is the *admins* on one phone that the USB
>   key task fixes. The tower has no Bluetooth, so every passkey test runs in
>   the phone's Chrome (Microsoft Learn: same-device passkey sign-in in Edge on
>   Android isn't supported yet).
> - **C5 amended (Gerard): CA001 keeps the 8-hour sign-in frequency and drops
>   "Never persistent".** Microsoft Learn ("Configure adaptive session lifetime
>   policies"): the persistent-browser-session control requires All cloud apps,
>   because every tab in a browser shares one session token. CA001 targets one
>   app. A separate tenant-wide policy was considered and declined (scope, and
>   more to roll back in C9).
> - **Deploy step 4 done.** CA001 built by hand (not a template) in
>   Report-only: group IIP Results Viewers (dev), exclude `bg-admin-01`, target
>   IIP Results (dev), Phishing-resistant MFA strength, sign-in frequency 8 h.
>   What If (IIP Results (dev), Android, Browser): `iip-ca-test` CA001 + CA903;
>   `bg-admin-01` not CA001; `djeemunee` CA903 only. All matched.
> - **Report-only pass, from the sign-in logs' Report-only tab** (13:38), all
>   as expected: **T1** passkey → Report-only: Success; **T2** password +
>   Authenticator push → Report-only: Failure (strength not met); **T4**
>   `bg-admin-01` → Not applied; **T5** `iip-ca-test` to mysignins → Not
>   applied.
> - **T3 not run, by design:** every account outside the group is a Global
>   Administrator, and admins bypass "Assignment required". T3's evidence is
>   M11's gate test 1 (2026-10-07, AADSTS50105, sign-in log 17:43:23Z,
>   Correlation ID `6a3aaa06-6190-441f-a6da-3f60416c8cdf`). **T6** moves to the
>   On pass.
> - **Deploy step 5 started: CA001 On at 13:41 (Phoenix).** The On-pass tests
>   wait for the next session, past the propagation window.

> **Progress, 2026-10-09 (Claude wrote the steps and the export split;
> Gerard ran every test and command and made every decision).** Times are
> Phoenix (UTC-7). CA001 had been On for about 20 hours.
> - **Deploy step 5 done: T1-T6 pass with CA001 On.** Read from the sign-in
>   logs' Conditional Access tab:
>
>   | Test | What was done (phone, Chrome Incognito) | Sign-in log | Result |
>   |---|---|---|---|
>   | T1 | `iip-ca-test`, passkey, the results page | 10:04:48, CA001 Success, CA903 Success | Page loaded and listed the T6 upload |
>   | T2 | `iip-ca-test`, password first | 10:17:43 / 10:17:50, CA001 Success (SignInFrequency), CA903 Success; Authentication details: requirement "Phishing-resistant MFA" for both factors | After the password, Entra offered **only** "Face, fingerprint, PIN or security key" plus Cancel. **No Authenticator push was offered at all.** |
>   | T3 | (by reference) | M11 gate test 1, 2026-10-07, AADSTS50105 | Every non-member is an admin, and admins bypass assignment |
>   | T4 | `bg-admin-01`, passkey, the results page | about 10:00, **every policy Not applied** | Page loaded |
>   | T5 | `iip-ca-test`, `mysignins.microsoft.com` | 10:02:40, CA001 **Not applied** | Signed in |
>   | T6 | Upload `item4-t6-ca001-on-20261009.png` (09:47:35) | The result: status ok, run completed, copy passed first time, audit = item4's answer key | The Function's identity is unaffected |
>
> - **T2, as observed, is stronger than the amended matrix predicted.** The
>   matrix expected an Authenticator push that CA001 would refuse. In fact
>   Entra never offered a method that can't meet the strength: Conditional
>   Access is evaluated after the first factor, and with CA001 and CA903 both
>   applying, the only second-factor choice shown was the passkey (Microsoft
>   Learn, "How Conditional Access authentication strengths work": the user
>   must satisfy every applicable strength). So the push is refused at the
>   method picker, before anything is sent to the phone. The 09:52:53 row
>   (Failure, CA Not applied) is the first T2 attempt's interrupted first
>   step, before the passkey (Claude's reading of the row).
> - **T6 has no managed-identity sign-in row**, filtered on
>   `id-iip-dev-wus-01` (last 24 hours). Not chased: the successful result
>   needed the identity's tokens for storage and Foundry, which is the proof.
>   Entra logs a managed-identity sign-in only when it issues a new token, and
>   those are cached; the filter also used the user-principal-name field,
>   which may not match managed-identity rows (Claude's reading, untested).
> - **No screenshots from the phone:** Chrome blocks screenshots in Incognito
>   on Android. The sign-in log rows above are the record. Screenshots of the
>   portal sign-in log show home IP addresses, so they stay out of the public
>   repo unless cropped.
> - **Deploy step 6 done (C8):** all five policies exported read-only from
>   Microsoft Graph (`az rest`, v1.0 `identity/conditionalAccess/policies`)
>   to `evidence/m13-conditional-access/` (its README has the details). Claude
>   checked every policy against this spec: all match. The excluded user,
>   group and app IDs were confirmed by name with `az ad`.
> - **Found in the export:** CA903 also excludes the directory role
>   **Directory Synchronization Accounts** (`d29b2b05-…`). It came with the
>   template; harmless here, since the tenant has no directory sync.
> - **C9 scheduled (Gerard): the week of 2026-10-26**, about 10 days before the
>   trial ends. That keeps CA001 live as a demo, and leaves time for the open
>   risk in step 7 if a Microsoft-managed policy appears.

## Read this first: this touches the whole tenant, not only the app

1. **Conditional Access and security defaults cannot be on together.**
   **Security defaults are ON in `letter7`, confirmed from Gerard's
   screenshot of Entra ID → Properties on Sep 16.**
   Before the first policy can be created, security defaults must be
   *disabled* for the whole `letter7` tenant. That is the tenant that holds
   the Azure subscription and the ostebovik.net production stack.
   Microsoft's guidance is to turn on replacement policies right away. That
   means **the "one policy" in the July plan becomes one app policy plus a
   small baseline.** See the baseline section below.
2. **When the trial ends, the policies stay and keep being enforced, but
   they can no longer be edited.** They can still be viewed and deleted, so
   the plan needs a rollback step (C9).
3. **Service principals and managed identities are not affected.** A
   Conditional Access policy that targets users doesn't block them. The
   Function's identity and the CI/CD identity keep working. Conditional
   Access for workload identities is a separate licence and out of scope.
4. **Azure's mandatory MFA for portal and CLI sign-in still applies either
   way.** It is enforced by Microsoft, not through Conditional Access.

## The app policy (the deliverable)

| Setting | Proposed value | Decision |
|---|---|---|
| **Name** | `CA001-IIPResults-Viewers-RequireAuthStrength` | C1: naming standard |
| **Users: include** | Group **IIP Results Viewers (dev)**, from the RBAC model | — |
| **Users: exclude** | Emergency-access (break-glass) account | C2 |
| **Target resources** | Enterprise app **IIP Results (dev)** only | — |
| **Conditions** | None. It applies to every sign-in to the app. | C3 |
| **Grant** | Require authentication strength: **Phishing-resistant MFA** | C4 |
| **Session** | Sign-in frequency **8 hours**. *(Amended 2026-10-08: "Never persistent" dropped; it requires All cloud apps. See C5.)* | C5 |
| **State** | **Report-only**, then **On** after the tests pass | C6 |

**Why this policy.** It protects the one thing a person reaches through
this project, the results page. It demonstrates *authentication strength*,
Microsoft's current control, which is more precise than the older "require
MFA" checkbox. The two cannot be combined in one policy. It is also small
enough to test completely within the trial.

## Baseline policies (needed because security defaults goes off)

Microsoft offers **Microsoft-managed Conditional Access policies** that
reproduce what security defaults provided: block legacy authentication,
require MFA for admins, require MFA for all users, and require MFA for Azure
management.

| Name | What it covers | Decision |
|---|---|---|
| `CA000-Baseline-*` (a Microsoft-managed set) | Security defaults' protections, now as policies | C7 |
| **As built, 2026-10-08:** `CA900-Baseline-AllUsers-BlockLegacyAuth`, `CA901-Baseline-AllUsers-MFA-AzureMgmt`, `CA902-Baseline-Admins-MFA`, `CA903-Baseline-AllUsers-MFA` | Hand-built from templates (C7 amended); a 9xx band keeps them unique and sorted after the app policies (Gerard's choice) | C1, C7 |

With these in place, turning off security defaults does not leave the
tenant weaker than it was for the length of the trial.

## Decisions (Gerard chose option (a) for all nine, Sep 16)

| ID | Question | Options; **(a) was chosen for every one** |
|---|---|---|
| C1 | Policy naming standard | (a) `CA###-<Scope>-<Who>-<Control>`, numbered so they sort and can be referred to briefly. (b) Plain English names. |
| C2 | Emergency-access account | (a) **Create one** cloud-only Global Administrator account, used for nothing else. Give it a long random password stored offline and a phishing-resistant method (a passkey), and exclude it from *every* policy. Microsoft recommends two for organizations; one is reasonable for a single-admin lab, and the page should say so. (b) Exclude your own admin account instead. That is simpler, but it means your daily account is the one that bypasses policy. |
| C3 | Conditions | (a) **None:** every sign-in to the app gets the control. (b) Location-based, with a named location for "home". That is weaker for a public demo and harder to test. (c) Sign-in risk (P2): shows Identity Protection, but a second condition makes the test matrix larger. It is a stretch goal, not the core. |
| C4 | Authentication strength | (a) **Phishing-resistant MFA.** It's the strongest story, but the test user must register a passkey (for example in Microsoft Authenticator) or a FIDO2 key. (b) The built-in **MFA strength**, which is easiest to test. Fall back to (b) if registering a passkey blocks testing. |
| C5 | Session controls | (a) **8-hour sign-in frequency, and sessions never persist in the browser.** (b) Leave the defaults. **Amended 2026-10-08 (Gerard): 8 hours only.** The persistent-browser-session control works only when a policy targets All cloud apps (Microsoft Learn), and CA001 targets one app. |
| C6 | Report-only period | (a) **Until the test matrix below passes in report-only mode** (a few days, not a fixed number), then switch to On. (b) A fixed 7 days. |
| C7 | Baseline | (a) **Turn on the Microsoft-managed policies** when security defaults goes off. (b) Write the four baseline policies by hand: more to show, more to maintain. **Amended 2026-10-07 (Gerard): build them by hand from the "Secure foundation" Conditional Access templates.** Found the same day (Microsoft Learn, "Microsoft-managed Conditional Access policies"): Microsoft creates its managed policies only in P1/P2 tenants *where security defaults aren't enabled*, on its own timetable, in report-only for 30+ days, and they **can't be deleted**. The tenant's policy list was empty on 2026-10-07. So (a) would leave no baseline at the moment security defaults goes off, and undeletable policies would complicate C9. The four to build are Microsoft's "upgrade from security defaults" set: block legacy authentication; MFA for Azure management; MFA for admins; MFA for all users. Each excludes `bg-admin-01`. |
| C8 | Evidence for the write-up | (a) **Export each policy as JSON** (Microsoft Graph, read-only) into the repo, plus screenshots of the report-only results and of an enforced sign-in. (b) Screenshots only. |
| C9 | When the trial ends | (a) **Export the policies, delete them, and turn security defaults back on,** so the tenant returns to a state that can be managed. (b) Leave them in place, enforced but frozen. |

**Gerard's notes on two of the decisions (Sep 16):**
- **C2:** "One break-glass account should be sufficient for our needs
  here." The write-up should say plainly that Microsoft recommends two for
  organizations, and that one is a deliberate choice for a lab with a
  single administrator.
- **C4:** passkeys are the better choice. Gerard expects some people to
  push back on having to register a passkey or use an authenticator app,
  and accepts that as "the cost of accessing the work and the architecture
  behind it."

**A design note that follows from C4 (Claude, for later):** only members of
**IIP Results Viewers (dev)** can sign in at all (app assignment is
required). Public readers of ostebovik.net will see the evidence
(screenshots, the exported policy, the demo video), not the live page. If an
outside reviewer is ever invited, it would be as a B2B guest. Authentication
strength works differently for guests: which methods satisfy it depends on
the cross-tenant MFA trust settings. Plan that case before inviting anyone;
nothing needs to be decided now.

## Test matrix (report-only first, then On)

| # | Who | Signs in to | Expected result |
|---|---|---|---|
| T1 | Test user, in the group, with a phishing-resistant method | Results page | Granted |
| T2 | Test user, in the group, **Authenticator push** (MFA, not phishing-resistant). *Amended 2026-10-08: was "password only", which CA903 now makes impossible.* | Results page | Report-only: "would require authentication strength". On: blocked until the passkey is used. *Observed On, 2026-10-09: after the password the push is not offered at all; the passkey is the only choice.* |
| T3 | A user not in the group | Results page | Blocked by app assignment, before Conditional Access applies (this is the RBAC model's row 10) |
| T4 | Break-glass account | Results page | Not in scope of the policy |
| T5 | Test user | Any other app | Not in scope of the app policy; the baseline MFA applies |
| T6 | The Function's managed identity | Foundry, storage | Unaffected |

Use the **What If** tool before each state change, and read the sign-in
logs' Conditional Access tab for T1–T5.

## Order at deploy time (inside the trial window)

1. Sign up for the trial and turn recurring billing off.
2. Create the break-glass account (C2), register its method, and store its
   credentials offline.
3. Turn on the baseline (C7), **then** turn off security defaults. Keeping
   this order means the tenant is never without protection.
   **DONE 2026-10-08** (3a-3d all run; results in "Progress, 2026-10-08").
   **Amended 2026-10-07 (Claude, after checking the live tenant):**
   - **3a. Authentication methods first.** On 2026-10-07 only Email OTP and
     Passkey (FIDO2) were enabled in the Authentication methods policy, and the
     legacy MFA/SSPR migration showed "In progress". `djeemunee`'s
     Authenticator MFA works today only through the legacy settings. Enable
     **Microsoft Authenticator** in the methods policy and finish the migration
     before anything else, so no admin depends on a deprecated setting.
   - **3b. Build the four baseline policies** (C7, amended) in **Report-only**,
     each excluding `bg-admin-01`. **Unverified:** whether the portal allows
     creating them while security defaults is still on. If it doesn't, turn
     security defaults off and create them straight to **On**. For a tenant of
     4 users that gap is minutes, and it is accepted.
   - **3c.** Security defaults off, then the baseline On. **Wait** (see the lag
     above), then check with What If and the sign-in logs: `djeemunee` is asked
     for MFA, `bg-admin-01` is excluded, `iip-ca-test` is covered.
   - **3d. Watch the policy list.** Microsoft-managed policies may appear once
     security defaults is off. Exclude `bg-admin-01` from any that do, and set
     them to Off if they duplicate the baseline.
4. **DONE 2026-10-08** (T3 by reference, T6 moved to step 5).
   Create CA001 in report-only mode and run T1–T6 with What If and the
   sign-in logs.
5. Turn CA001 on and run T1–T6 again. *(On since 2026-10-08 13:41.)*
   **DONE 2026-10-09:** all six pass ("Progress, 2026-10-09").
6. Export the evidence (C8). **DONE 2026-10-09:**
   `evidence/m13-conditional-access/`.
7. Before the trial end date, carry out C9. **Planned for the week of
   2026-10-26** (Gerard, 2026-10-09).
   **Open risk (2026-10-07):** C9 turns security defaults back on, which needs
   the Conditional Access policies gone. Microsoft-managed policies can't be
   deleted, only turned off, and Microsoft Learn doesn't say whether an Off
   managed policy blocks re-enabling security defaults. If any managed policy
   appears after 3c, test this well before 2026-11-06 (Todoist reminder, due
   Nov 2).

## Sources (Microsoft Learn, 2026-09-16)

- Plan a Conditional Access deployment; What is Conditional Access? (the
  license, and what happens when it expires)
- Security defaults in Microsoft Entra ID (disabling them; moving to
  Conditional Access; Microsoft-managed policies)
- Conditional Access authentication strengths (the built-in strengths, and
  the fact that they can't be combined with "Require MFA")
- Require phishing-resistant MFA for administrators (portal steps,
  report-only mode)
- Manage emergency access accounts; Microsoft cloud security benchmark
  PA-5
- Added 2026-10-08: Conditional Access policy templates (templates exclude
  only the creating user; created in Report-only); How to migrate MFA and SSPR
  policy settings to the Authentication methods policy; Set up multifactor
  authentication for Microsoft 365 ("If security defaults are turned on, you
  can create new Conditional Access policies, but you can't turn them on")
