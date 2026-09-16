# Phase 2 — Conditional Access policy spec (outline)

**Status: DESIGN AGREED ON PAPER, 2026-09-16.** This is the second item on
the Phase 2 entry checklist. Claude drafted the structure and options from
Microsoft Learn. **Gerard chose option (a) for all nine decisions (C1–C9)**,
and added the two notes recorded under the decisions table. Nothing here is deployed. Deployment happens during the
30-day Entra ID P2 trial, which starts only once the results page and its
sign-in exist (Todoist task; turn recurring billing off right after
signup).

## Read this first: this touches the whole tenant, not only the app

1. **Conditional Access and security defaults cannot be on together.**
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
| **Session** | Sign-in frequency **8 hours**; persistent browser session **Never persistent** | C5 |
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

With these in place, turning off security defaults does not leave the
tenant weaker than it was for the length of the trial.

## Decisions (Gerard chose option (a) for all nine, Sep 16)

| ID | Question | Options; **(a) was chosen for every one** |
|---|---|---|
| C1 | Policy naming standard | (a) `CA###-<Scope>-<Who>-<Control>`, numbered so they sort and can be referred to briefly. (b) Plain English names. |
| C2 | Emergency-access account | (a) **Create one** cloud-only Global Administrator account, used for nothing else. Give it a long random password stored offline and a phishing-resistant method (a passkey), and exclude it from *every* policy. Microsoft recommends two for organizations; one is reasonable for a single-admin lab, and the page should say so. (b) Exclude your own admin account instead. That is simpler, but it means your daily account is the one that bypasses policy. |
| C3 | Conditions | (a) **None:** every sign-in to the app gets the control. (b) Location-based, with a named location for "home". That is weaker for a public demo and harder to test. (c) Sign-in risk (P2): shows Identity Protection, but a second condition makes the test matrix larger. It is a stretch goal, not the core. |
| C4 | Authentication strength | (a) **Phishing-resistant MFA.** It's the strongest story, but the test user must register a passkey (for example in Microsoft Authenticator) or a FIDO2 key. (b) The built-in **MFA strength**, which is easiest to test. Fall back to (b) if registering a passkey blocks testing. |
| C5 | Session controls | (a) **8-hour sign-in frequency, and sessions never persist in the browser.** (b) Leave the defaults. |
| C6 | Report-only period | (a) **Until the test matrix below passes in report-only mode** (a few days, not a fixed number), then switch to On. (b) A fixed 7 days. |
| C7 | Baseline | (a) **Turn on the Microsoft-managed policies** when security defaults goes off. (b) Write the four baseline policies by hand: more to show, more to maintain. |
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
| T2 | Test user, in the group, password only | Results page | Report-only: "would require authentication strength". On: blocked until a strong method is used |
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
4. Create CA001 in report-only mode and run T1–T6 with What If and the
   sign-in logs.
5. Turn CA001 on and run T1–T6 again.
6. Export the evidence (C8).
7. Before the trial end date, carry out C9.

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
