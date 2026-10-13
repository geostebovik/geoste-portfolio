# Phase 2: taking the M7 agent from a laptop to an operated Azure app

<!--
DRAFT, NOT FOR PUBLICATION. First draft written 2026-10-13.
Goes up in one joint push with the M7 write-up (m7-writeup-draft.md), after
outside readers. /ai-103/* returns 404 on ostebovik.net
(staticwebapp.config.json), so pushing this file does not publish it.

WHO WROTE THIS DRAFT: Claude drafted all of the prose on 2026-10-13 from
STATUS.md (Sep 21 - Oct 13 entries), the prep docs (m10-, m11-, m12-,
m14-prep.md), phase2-orientation.md, the RBAC model, the CA spec,
infrastructure/iip/README.md and the commit log. Gerard chose the shape
(case studies, "symptom -> evidence -> root cause -> fix"), the length (about
the M7 page's) and the audience, and is the editor. Record his edits and
decisions inline as he makes them.

CONVENTIONS CARRIED OVER FROM THE M7 PAGE:
- "Acceptance test" means the project's own definition of done, never a
  Microsoft certification.
- Attribution only where the log records it. Where it's silent, this page is
  silent. Claude's errors are named.
- Times are UTC (Z) unless marked Phoenix.

STILL OPEN BEFORE PUBLISHING:
- M13's rollback (C9, the week of 2026-10-26): add one closing line to the
  M13 row and to "Known limits". Nothing else depends on it.
- Gerard's edit pass, then outside readers for "In short".
- At publish time: an "On this page" link list, and the evidence table's
  repo-relative paths turned into GitHub links.
-->

## In short

- **What it is:** the second phase of the IIP lab build for AI-103. Phase 1
  ended with an AI agent that worked on a developer's laptop: it drafts
  marketing copy for a fictional hardware store, checks the draft, and audits
  the thumbnail image. Phase 2 turned that into an app that runs in Azure.
  You upload a thumbnail and a topic. An Azure Function runs the agent with no
  keys and saves the result. The result shows on a web page behind an Entra
  ID sign-in. Almost all of it is defined in Bicep (the Conditional Access
  policies were built by hand and exported), and it's monitored and deployed
  from GitHub.
- **What it proves:** each of the seven milestones (M8-M14) has a written
  definition of done, shown rather than asserted. Six are complete; M13's
  last step, a scheduled rollback, is still ahead. The same test
  upload, with a known correct answer, was re-run after every change that
  could break it. It gave the right answer every time.
- **What it's really about:** troubleshooting. Most of the time in this phase
  went into things that looked right and weren't: a role that matched
  Microsoft's documented minimum and still failed, an alert that fired but
  never emailed, a deployment preview whose "noise" would have wiped real
  settings. Six of those are written up below as case studies, in the order a
  support engineer would work them.
- **What it doesn't do yet:** some of what was built is deliberately not left
  running. The private networking was built, proven and then torn down to
  save cost, and the Conditional Access policies are deleted when a free
  licence trial ends. "Known limits" lists these and the rest.

## Terms used on this page

- **Bicep / what-if:** Bicep is Azure's language for describing resources in
  files. `what-if` is a dry run that lists what a deployment would change
  before anything changes.
- **Managed identity:** an identity Azure gives to a resource, such as a
  Function, so it can sign in to other services without a password or key.
- **Role, scope:** a role is a set of permissions. Its scope is what it
  applies to: a whole subscription, one storage account, or one queue.
- **Keyless:** every service call signs in with Entra ID instead of a shared
  key.
- **Queue, poison queue:** each upload becomes a message in a queue. A message
  that fails every allowed try is moved to a second, "poison" queue, so it
  stops retrying and someone can look at it.
- **Alert, action group:** an alert rule watches for a condition. Its action
  group says who gets told and how (here, one email address).
- **Trace, span:** a trace is the full timeline of one piece of work. Each
  span is one timed step in it, with a name, a duration and a link to the
  bigger step it belongs to, so they nest like an outline.
- **Conditional Access:** Entra ID rules that decide how someone must sign in
  (for example, with a passkey) before they reach an app.
- **Acceptance test / answer key:** the project's own definition of done for
  the agent, scored against written expected results. Not a Microsoft
  certification.

## What was built

| Milestone | What it is | Shown by |
|---|---|---|
| **M8** (Sep 21) | Everything that already existed, described in Bicep | A `what-if` that lists only diffs written down and justified one by one in a register |
| **M9** (Sep 21) | Two managed identities and their roles, from a written RBAC model | The role assignments exist and match the model, row by row |
| **M10** (Sep 23) | No keys: every tracked script moved to Entra ID sign-in | The M7 agent's acceptance test re-run on the keyless code, and no surveyed script reading a key |
| **M11** (Oct 7) | The app: upload, Event Grid, queue, Function, agent, result, and a sign-in page | An upload produces a correct result, and a member of the viewers group can sign in and see it |
| **M12** (Oct 12) | Private networking: private endpoints and a storage firewall | The app still worked end to end with the private paths verified. Then torn down, Bicep kept |
| **M13** (tested Oct 9) | Conditional Access: phishing-resistant sign-in for the results page | Six sign-in tests passed with the policy On, and the policies are exported. Rollback due before the licence trial ends |
| **M14** (Oct 13) | Operate: deploys from GitHub, alerts, tracing | A push deploys the Function; a failed upload emails an alert; one upload's trace shows every step |

```
 you ──upload (thumbnail + topic)──► stiipdevwus01 / uploads
                                         │  BlobCreated
                                         ▼
                        Event Grid system topic (its own identity)
                                         │
                                         ▼
                        queue: upload-events ──2 failed tries──► upload-events-poison
                                         │                                │
                                         ▼                                ▼
            Function app, Flex Consumption (managed identity)      log alert ─► email
              └─ runs the M7 agent in Foundry Agent Service
                   tools: fact sheet · judge (evaluation SDK) · image audit (Vision)
                                         │
                                         ▼
                              stiipdevwus01 / results
                                         │
                                         ▼
          results page /api/results ◄── Entra sign-in: app assignment (group)
                                         + Conditional Access (phishing-resistant)

 Around it: Bicep for all of it · App Insights + Log Analytics (Entra-only ingestion)
            GitHub Actions deploys over OIDC (a second managed identity, no secret)
```

Mapped against Microsoft's AI-103 study guide (skills measured as of April 16,
2026), Phase 2 covers the operational half of the exam's largest-weighted
area:

| Exam skill area (weight) | Skill named in the study guide | Where Phase 2 does it |
|---|---|---|
| Plan and manage an Azure AI solution (25-30%) | Design Azure infrastructure for AI apps and agent-based solutions | M8, M11 (the architecture above) |
| Plan and manage an Azure AI solution (25-30%) | Integrate Foundry projects with continuous integration and continuous deployment (CI/CD) pipelines | M14: GitHub Actions over OIDC. Strictly, the pipeline deploys the Function that calls the Foundry project, not the project itself |
| Plan and manage an Azure AI solution (25-30%) | Configure security, including managed identity, private networking, keyless credentials, and role policies | M9, M10, M12; case studies 2, 3 and 5 |
| Plan and manage an Azure AI solution (25-30%) | Manage quotas, scaling, rate limits, and cost footprints for model and agent workloads | Every build priced first from Azure's retail price list (M11, M12, M14) |
| Implement generative AI and agentic solutions (30-35%) | Set up observability by implementing tracing, token analytics, safety signals, and latency breakdowns | M14: case study 6 |
| Implement generative AI and agentic solutions (30-35%) | Integrate monitoring into deployed agents, evaluate agent behavior, and perform error analysis | M14: case studies 1 and 6 |

M13, Conditional Access, isn't an AI-103 skill. It's the identity work an app
with a sign-in page needs either way.

**One rule held across the phase.** After every change that could affect the
app, the same test image (item4 from the M7 answer key, with one planted brand
flaw) was uploaded again. The correct answer is: copy passes first time; the
audit says legible PASS, brand FAIL, accurate PASS. It came back correct with
the Function inside the private network, after the storage firewall went on,
after the teardown, with Conditional Access On, after the first GitHub deploy, and after
tracing was added. Each of those result files is committed.

## Case studies

Each one follows the same order: what was seen, what was checked, what the
cause turned out to be, and what changed. Several include a wrong turn,
because that's part of the record.

### 1. The alert that fired but never emailed (M14)

**Symptom.** An alert was built to email when an upload fails every try and
lands in the poison queue. That's the one signal that means "the app is
broken". To prove it, a failure was caused on purpose: pause the Function,
upload, delete the image, un-pause. That's Gerard's method from Sep 25, with
the pause added by Claude. The alert fired at 19:22:56Z on Oct 12,
and its history said "Action group executed" 0.2 seconds later. No email
arrived. Neither did one for the alert resolving at 20:23:57Z, or for a second
firing at 20:37:57Z.

**Evidence, and what it ruled out.** The action group's portal **Test** email
*did* arrive, from the same sender. So the mailbox could receive it. Microsoft
Learn's "missing email notification" checklist was worked through item by
item:
- no alert processing rule was suppressing it;
- the receiver was a plain email address;
- searches of every folder for all three sender addresses Learn lists found
  nothing, and no inbox filter matched;
- the receiver was Enabled, and its one-time verification code had been
  confirmed.

Every item came back clean.

**Root cause.** Gerard ran the action group's own troubleshooter ("Diagnose
and solve problems"). It reported all three real notifications as failed:
*"The group receiver … was found to be empty after resolution."* **No email
had ever been sent.** The portal Test sends straight to the receiver, so it
skips the step that was failing. Real alerts resolve the group's receivers
first, and that came back empty. The portal also showed the receiver as
Verified, which retired the obvious theory, an unverified address. Learn has
no page for this message.

**Fix.** The action group was re-saved with no change to any property, which
causes no drift from the Bicep. Twelve minutes later, at 21:39Z, the Resolved
email for the second alert arrived: the first real alert email ever
delivered. The next day a deliberate re-fire produced a Fired email within two
minutes of the alert (10:07 Phoenix). That's 0 of 3 delivered before the
re-save, and 2 of 2 after.

**What it doesn't prove.** The re-save can't be separated from the time that
passed. Background propagation would look the same. Separating them would
mean breaking a working group on purpose, and the lesson is the same either
way.

**A wrong turn on the way (Claude's errors).** The first overnight re-fire
never fired, and the alert wasn't at fault. The test file was a `.txt`, which
the Function deliberately skips, so nothing failed. Also, the pause hadn't
reached the running Function yet: the log showed it taking the message one
second after a restart. The re-fire that worked used a real image, and
checked twice, two minutes apart, that the message was still waiting before
deleting the image.

**Lesson.** A portal "Test" button proves the last step of a path, not the
path. Prove a new action group with one real alert.

### 2. The failed upload that couldn't be released (M11)

**Symptom.** A failed upload should be retried after one minute
(`visibilityTimeout`), and after two failed tries move to the poison queue.
On Sep 25, failed tries retried after **10 minutes, not 1**.

**Evidence.** Each retry was preceded by a 403
`AuthorizationPermissionMismatch` from the queue service. The stack trace
named the call: `QueueProcessor.ReleaseMessageAsync` →
`QueueClient.UpdateMessageAsync`. To release a failed message back to the
queue early, the Functions host calls **Update Message**. Microsoft's
permissions table maps that to `messages/write`. The Function's role was
exactly the documented minimum for an identity-based queue trigger: Storage
Queue Data Reader plus Message Processor. **Neither includes
`messages/write`.** Without it, the host couldn't release the message, so it
reappeared only when its 10-minute lock ran out. There was a latent risk too:
the host renews that lock every 5 minutes during a long run with the same
call, so a run over about 10 minutes could have been processed twice.

**Fix.** Gerard chose a custom role over the built-in Storage Queue Data
Contributor. Contributor would also have granted Clear Messages and the
right to delete or change the queue itself. He also chose to reach it in two
stages, so each test changed one thing. The custom role, **IIP Queue Trigger
(dev)**, holds only what the trigger needs.

**Where it got harder.** The first re-test still got a 403, 65 minutes after
the role was assigned. A temporary built-in Contributor fixed it within about
20 minutes, which pointed at the custom role. So the custom role was tested on
its own, on Gerard's identity, with a negative control: the update was allowed
with it and refused without it. With Contributor removed, the Function then
passed cleanly (no 403, retry after about 100 seconds). On Sep 29 the custom
role was verified alone, about 24 hours after the old roles were deleted:
retry at +103 seconds, then the poison move, with zero permission errors
in the Function's logs.

**Still open.** Why the first assignment took more than 65 minutes. It was
either a slow custom-role assignment for a managed identity, or a permission
refresh triggered by adding and removing Contributor. Both are recorded, and
neither is claimed.

**Lesson.** A documented minimum is where to start, not proof. The failure
path (release, retry, poison) only runs when something goes wrong, so it has
to be tested by making something go wrong.

### 3. The right role at the wrong scope (M11)

**Symptom.** On Sep 24, creating the Event Grid subscription that turns "a
blob was uploaded" into a queue message failed three times in about 20
minutes: *"Managed Identity Authorization Error."*

**Evidence.** The role was there. Gerard confirmed with `az role assignment
list` that the topic's identity held Storage Queue Data Message Sender on the
queue. Least privilege says to grant that on the one queue it writes to, and
that's what had been granted.

**Root cause.** Claude's hypothesis, which the next deploy confirmed: Event
Grid checks the identity's permission **when it creates the subscription**,
and checks it against the destination's resource ID, which is the storage
account, not the queue. Microsoft Learn's steps also say "on the storage
account".

**Fix.** Gerard approved widening the grant to the account. The redeploy
succeeded first time, and the orphaned queue-level grant was deleted. The
trade-off is written into the RBAC model: the topic can now add messages to
any queue on the account (there are two), but it can't read or delete them.

**A wrong turn:** the queue-scoped version was Claude's, and cost three failed
deploys and about 20 minutes.

**It mattered again in M12.** Once a storage account has a firewall, Event
Grid can deliver to it only with a system-assigned identity and the "trusted
Microsoft services" exception (Microsoft Learn). The topic was given a
system-assigned identity in M11 for that reason. With the firewall on in M12,
the test upload still produced a correct result in 46 seconds.

**Lesson.** Scope is part of the role. When the role is clearly present and
access still fails, ask *what the service checks against*, and *when* it
checks.

### 4. The deployment preview whose "noise" would have wiped real settings (M8)

**Symptom.** M8 described the existing resources in Bicep. The first
`what-if` on Sep 21 reported 7 resources to modify, where the goal was none.
Azure labels `what-if` output with a banner saying it "may contain false
positive predictions (noise)", and most of the lines looked like noise: a `-`
on a property that reads like a status field, on a resource nobody meant to
touch.

**Evidence.** Each property was checked against the resource provider's
schema. Properties flagged `ReadOnly` can't be set by any template, so a `-`
on them is genuine noise. Several weren't flagged. They were **writable settings
the template had left out**, and a deployment would have cleared them:

| Property | Looked like | What deploying would have done |
|---|---|---|
| `defaultProject` (Foundry account) | provider bookkeeping | broken data-plane calls that don't name a project |
| `associatedProjects` (Foundry account) | derived from the child | detached the project from the account |
| `currentCapacity` (×4 model deployments) | a status field | cleared the tokens-per-minute settings (300K, 30K, 10K) |
| `computeType` (AI Search) | a status field | cleared the Default vs confidential-compute choice |

A sixth, `networkRuleSet.bypass` on Search, had first been dropped as
"preview only". It isn't: it's in the GA API version. The module was pinned
to an old API version, and the missing property had been explained away.
Updating the API version fixed it.

**Fix.** Every writable property was declared as it was found. Every remaining
diff, a property no template can set, went into a **register** with a written
reason. Gerard then amended M8's definition of done from "what-if shows no
changes", which Azure can't produce for these resources, to "no changes
other than the registered ones". That's stricter than it sounds: any line
not in the register is treated as a real change. The register has been
checked at each what-if since. The latest is 6 modify, 32 no change,
11 Unsupported and 2 to ignore (Oct 12), every line accounted for. M12's
build found two more dropped writable properties the same way.

**Also found:** the `managed-by: bicep` tag had been on four resources since
July, while nothing was in Bicep. M8 is what made the tag true.

**Lesson.** "May contain noise" is a reason to check each line, not to skip
them. The test is the provider schema's `ReadOnly` flag, not how the line
looks.

### 5. "No keys": what the code does versus what the account still allows (M10)

**Symptom.** On Sep 16, before M10, the Foundry account's activity log showed
about ten `listKeys` calls under Gerard's account while the portal was open.
That's expected portal behaviour, but it confirmed key access was still
switched on. M10's goal was that no script reads a key.

**The migration.** All 12 call sites across the nine tracked scripts moved to
Entra ID sign-in. The M7 acceptance test was re-run on the keyless code and
passed (Gerard's call). One item's lower score was traced to known variance
in its model-judged scoring, not to the migration. Two things surfaced along the way.

**A script the survey missed.** The M10 survey treated `m3_analyze.py` only as
the place a key helper lived. It never looked at the script's own pipeline,
which read two keys: a subscription key, and a storage SAS signed with the
account key. Gerard chose to name it as a stated exception in M10's
definition of done rather than leave the milestone quietly open. It was
closed on Sep 23. The REST calls now use bearer tokens, and the SAS is signed
with a user delegation key, which is decision (A), Gerard's.

**A test that couldn't have failed the right way.** One planned M10 test said
a 401 or 403 from AI Search would mean "the free tier doesn't support keyless
sign-in". But the RBAC model deliberately gave no role on Search, so the test
would have returned 403 for a missing role. That would have been read as a
tier limit, pointing toward recreating Search on a paid tier: a one-way
change with a monthly bill. The role was assigned first, and keyless Search
then worked on the free tier.

**Who was still reading the keys.** After the migration, `listKeys` calls
kept arriving. The activity log showed why:
- every call carried the client app ID that Microsoft's first-party app list
  names as **Visual Studio Code**;
- the calls came in pairs on a fixed 14 minute 42 second timer, so not a
  person;
- they stopped when VS Code was closed.

Which extension makes them isn't determined. The hypothesis was Claude's;
Gerard ran every query.

**Root cause, the important part.** The Function's role, Foundry User,
includes the `listkeys` action. Keyless code stops the app *using* keys. It
doesn't stop an identity *fetching* one. The step that makes a fetched key
useless is switching local (key) authentication off on the account
(`disableLocalAuth`). There's a second effect: with VS Code fetching keys
about eight times an hour under Gerard's identity, the `listKeys` record
can't show a genuine retrieval. Turning keys off would also make "who
fetched a key?" worth asking again.

**Status.** `disableLocalAuth` hasn't been done yet. It's in the backlog, with
both known breakages listed (the VS Code poll, and the now-closed M3
pipeline). See "Known limits".

**Lesson.** "The code is keyless" and "the account is keyless" are different
claims. Check the role's permissions, not just the code's behaviour.

### 6. The SDK that doesn't trace its own tools (M14)

**Symptom.** The goal for tracing was to see, inside one upload, each step of
the agent's run and each of its three tools: `get_fact_sheet`,
`evaluate_draft` and `audit_thumbnail`. Microsoft's docs for this SDK version
(`azure-ai-agents` 1.1.0, the "classic" Agents API) show a few lines to turn
tracing on.

**Evidence.** Before writing anything, the exact package set was installed
offline, and the SDK's tracing code was read. It has a helper that creates an
`execute_tool` span, **and nothing in the SDK calls it.** With message content
recording off (it stays off, because the prompts carry the store's fact
sheet), the tool names weren't recorded anywhere else either. Following the
docs would have produced a trace with every agent step and no named tools.

**Fix.** The M7 orchestrator already wraps each tool in a helper, `logged()`,
that records its inputs and outputs. It refuses to run if the wrapper changes
the tool definitions the model sees. **Gerard decided (D-M14-7)** to add one
span around that helper at startup, rather than accept unnamed tools. No
certified file changed, and the orchestrator's own check proves the agent's
tools didn't move. An offline negative control confirmed the check is live:
a wrapper that hides the tool's signature is refused.

**Result.** One traced upload on Oct 13 gave the correct item4 result, and 61
spans under a single operation ID. That's the host's request, the agent's
steps, and `execute_tool get_fact_sheet` (0 ms), `evaluate_draft` (7.1 s) and
`audit_thumbnail` (3.1 s), in that order. The trace answered a question the
logs couldn't: about 10 of the 22.5 seconds the agent spent working were our
own tools. Inside the 3.1-second image audit, the Vision call itself took 0.2
seconds. One upload costs about 200 KB of log ingestion, 76 KB of it the new
spans.

**What it still can't see.** The judge inside `evaluate_draft` reaches its
model through the `openai` package, which this lean package set doesn't trace.
Its 7.1 seconds show up as one block. That also means tracing doesn't fix a
known gap from M7: token counts read from the agent leave out the judge's
tokens (and the image audit's own vision calls).

**Lesson.** When the docs and the installed code might disagree, read the
code. It took minutes, and it changed what got built.

## Smaller findings worth recording

- **Global Administrators bypass "assignment required."** An app set so
  only assigned users can sign in still lets a Global Admin through
  (Microsoft's AADSTS50105 page). The sign-in gate was tested with a
  non-admin test user for that reason.
- **Basic publishing credentials were on by default.** While checking which
  identity performed the first GitHub deploy, Gerard checked the Function's
  publishing settings. Basic authentication was enabled for the deploy
  endpoints (ARM's default), so the publish profile held a working password,
  which undercut the secretless deploy. It was switched off in Bicep, and the
  OIDC deploy still works.
- **Conditional Access and security defaults can't both be on.** Testing one
  app policy meant turning off the tenant-wide defaults first. Four baseline
  policies replaced them for the trial, and a break-glass Global Admin
  account was created first. That account is excluded from every policy, and
  its password is kept on paper.
- **Private endpoints needed no NAT gateway.** With the Function inside the
  VNet, outbound calls kept working. That was measured, and the mechanism
  wasn't established.
- **A queue metric couldn't drive the poison alert.** `QueueMessageCount` has
  no per-queue breakdown and refreshes daily (Microsoft Learn). So the alert
  is a log search on the host's own "moving message to the poison queue" line,
  checked every 15 minutes for $0.50 a month.

## Known limits, stated plainly

- **The private networking isn't running.** M12's private endpoints and
  storage firewall were built, tested and torn down on Oct 12 to save cost
  ($15.60 a month running, from Azure's retail price list). The VNet and its
  security groups stay, at $0. One Bicep parameter rebuilds the rest for a
  demo. Today the storage firewall is open again.
- **Conditional Access is temporary.** The Entra ID P2 trial ends on Nov 6.
  The policies are deleted and security defaults turned back on before then
  (C9, the week of Oct 26), and the exported policy files become the record.
  *[Add the C9 result here.]*
- **Key access is still on for the Foundry account** (case study 5).
  `disableLocalAuth` is in the backlog.
- **The Function's Foundry role is broader than it needs.** Foundry User
  grants everything on the account (`Microsoft.CognitiveServices/*`). One
  shared AI Services account serves both the chat models and Vision, so
  "narrowest role at narrowest scope" can't be met for that row. It's
  recorded as an accepted trade-off.
- **AI Search is on the free tier.** It can't take a private endpoint, and its
  tier can't be changed after creation.
- **The agent uses the classic Agents API, which retires on 2027-03-31.** The
  migration is planned and will rebuild the agent-level tracing and the
  agent's network isolation. The isolation design is costed (about $98 a
  month as a full private setup) and written up, not built.
- **Two open questions are recorded, not answered:** why the alert email
  started working (case study 1), and why the first custom-role assignment
  took more than 65 minutes (case study 2).
- **Dev and the public portfolio site share one subscription and one
  credit,** with a spending limit as the brake.

## Lessons worth keeping

- **Test the path that only runs when something breaks.** The release,
  retry, poison and alert paths all looked fine until a failure was caused on
  purpose (case studies 1 and 2).
- **A test has to be able to fail for the reason it's looking for.** The
  Search test would have read a missing role as a tier limit. The `.txt`
  re-fire couldn't fail at all.
- **Saved isn't applied.** A setting confirmed in a list proves it was saved,
  not that the running service obeys it. Check the effect (case study 1).
- **Present isn't sufficient.** The right role at the wrong scope fails
  exactly like no role (case study 3).
- **Treat "noise" as a list to check** (case study 4).
- **Check what the identity can do, not just what the code does** (case study
  5).
- **Read the code when the docs might be wrong** (case study 6).
- **Price it before building it.** Every build in this phase was costed from
  Azure's retail price list first, and the cost of tearing down and
  rebuilding was part of the networking decision.

## How this was built

Built with Claude (Anthropic) as a coding and analysis partner, with work
divided on purpose, as in Phase 1.

**Gerard** made the design decisions, often choosing among options Claude laid
out, and did all of the Azure, CLI, portal and git work: every what-if,
deploy, test, upload and query. Recorded decisions include:
- amending M8's definition of done to the register standard (Sep 21);
- naming M3's key use as a stated exception rather than leaving M10 open
  (Sep 22), then decision (A), a user delegation SAS (Sep 23);
- the queue design (Sep 23), and the M11 build choices: remote build, Python
  3.14, the topic as blob metadata, one agent per upload (Sep 24);
- widening the Event Grid grant to the account (Sep 24);
- a custom queue role reached in two stages, rather than the broader built-in
  role (Sep 25);
- 7-day soft delete for blobs and containers (Sep 29);
- the group-based sign-in gate, and starting the P2 trial (Oct 7);
- which private endpoints to build, and to tear them down after the evidence
  window (Oct 9);
- building the agent's network isolation inside the API migration rather than
  now (Oct 10);
- the order of M14's parts, trusting only the `main` branch for deploys, the
  alert frequency, the lean tracing packages, and naming each tool call
  (Oct 12-13).

He also caught problems himself:
- unregistered what-if diffs and an empty queue check (Sep 25);
- a deprecated role that Claude had wrong (Sep 22);
- a session handoff that never reached the repo (Sep 23);
- the reason the weekly scheduled task had stopped running (Oct 12).

He also pushed back on certifying data whose history was in question (Sep
22), which surfaced two provenance gaps.

**Claude** wrote the Bicep, the Function code, the tracing setup, the probe
and test scripts, the commands Gerard ran, and the documentation drafts,
including this page. Claude also made these errors, among others:
- the queue-scoped Event Grid grant (case study 3);
- the first alert proof upload, which left out the topic and so couldn't fail;
- the `.txt` re-fire (case study 1);
- several wrong "expected output" lines in commands on Sep 25.

Where the project log doesn't record who did something, this page doesn't
say.

## Evidence

| What | Where |
|---|---|
| The what-if register (M8 onward) | `infrastructure/iip/README.md` |
| All Bicep | `infrastructure/iip/` |
| RBAC model, rows 1-18 | `phase2-rbac-model-draft.md` |
| Keyless migration | `aa96bea` (12 call sites); `fcc55b6` (M3) |
| The Function's code | `function/` (first built in `b713df9`) |
| Private networking, built state | `evidence/m12-networking/`; `m12-prep.md` |
| Conditional Access policies, exported | `evidence/m13-conditional-access/`; `phase2-conditional-access-spec-draft.md` |
| First GitHub deploy over OIDC | `fd02de9`; `.github/workflows/iip-function-deploy.yml` |
| Tracing | `8b4dce6`; `function/tracing.py`; `evidence/m14-tracing/` |
| Regression uploads (item4) | `scripts/results/*_function_item4_*.json` (CA001 On; M12 stages 2 and 3; teardown; OIDC; tracing) |
| Case study 1 (alerts) | `m14-prep.md`, Part 2 and "the delivery fault" |
| Case study 6 (tracing) | `m14-prep.md`, Part 3, "the build and the run" |
| Full session log | `STATUS.md` (Sep 21 - Oct 13) |
