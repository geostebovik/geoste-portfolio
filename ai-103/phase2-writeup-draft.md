# Taking the agent from a developer's machine to an app running in Azure

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
  silent.
- Wrong turns (Gerard, 2026-10-13): kept only where Gerard took part in
  catching or resolving them; cut where they were Claude's alone.
- Dates and times (Gerard, 2026-10-13): no clock times or day-level dates
  in the body. Durations stay where they are the finding (10 minutes vs 1,
  65+ minutes, 14 minutes 42 seconds). Month-level dates in the milestone
  table. The session log has the exact times.

GERARD'S EDITS, 2026-10-13 (Claude applied them):
- "In short", bullet 1: "a developer's laptop" became "a developer's machine";
  "You upload a thumbnail…" became "Upload a thumbnail… An Azure Function
  then runs…" (Gerard's wording; Claude fixed one typo).
- Accepted Claude's critique items: "In short" 1-4 (unmeasured "most of the
  time"; the case-study order wording; "every change" became "each major
  change"; the Bicep sentence cut from bullet 1). "What was built" 1-3 (the
  diagram's Bicep line; "each major change"; the exam-weight error, since
  "Plan and manage" is not the largest area).
- Cut from the AI-103 table (Gerard): the CI/CD row (the pipeline deploys the
  Function, not the Foundry project) and the quotas/cost row (pricing infra
  isn't managing model workloads).
- Added to Terms (Gerard): OIDC; federated credential.
- Edit pass completed the same day, section by section (Gerard approved each
  change; Claude applied and re-checked them). Gerard's rules for the page:
  no Claude-only wrong turns, no clock times or day-level dates, and no
  operational details about the live tenant (where the break-glass password
  is kept, the storage firewall's state, how the subscription is funded).
- Added (Gerard's idea): "After Phase 2", undated intent only.
- Title (Gerard): no "M7"; "laptop" became "a developer's machine" to
  match bullet 1. M7's title dropped "M7" the same day.

CLAUDE'S EDITS, 2026-10-14 (for Gerard to review): key authentication was
switched off on the Foundry account the same day, so case study 5's "Status"
became "Fix" (the test in both directions, plus the 403-not-401 detail). The
"Known limits" bullet and the "After Phase 2" bullet for it were removed. "One
rule held" and the evidence table gained the keys-off upload. "How this was
built" gained the decision. "In short" was NOT touched (held for the outside
readers). Not added to "Known limits": storage-account and AI Search key
access, under Gerard's rule against operational details about the live tenant.
Gerard's call whether to add them.

GERARD'S DECISION, 2026-10-15: case study 5 gains the "Then storage and AI
Search" paragraph (Claude drafted both sentences; Gerard approved both). It
states the security posture only, not the live tenant's settings.

STILL OPEN BEFORE PUBLISHING:
- ~~M13's rollback (C9, the week of 2026-10-26): add one closing line to the
  M13 row and to "Known limits". Nothing else depends on it.~~ DONE
  2026-10-26: Gerard ran C9; Claude added both lines.
- ~~Gerard's edit pass~~ (done 2026-10-13), then ~~outside readers for "In
  short" (requests out; see OUTSIDE READERS below)~~. Readers dropped
  2026-10-24 (Gerard). His own "In short" went in 2026-10-26 (next entry).

GERARD'S "IN SHORT", 2026-10-26. Gerard rewrote "In short" in his own voice
(Option A, his decision of 2026-10-20) in the Claude Doc "In short — offline
edit", then revised it through three rounds of line-by-line critique by
Claude. Gerard decided every change. The final wording is mixed. Treat these
as Claude's, adopted by Gerard: most of "What it shows" ("so a break showed
up right away" replaced Claude's own first suggestion, "never quietly broke",
which overclaimed: M12's firewall did break M3's `--blob` path); "no keys or
passwords in the code to leak"; and "symptom, evidence, root cause, fix",
matched to the case-study headings. The rest of the order and wording is
Gerard's. The page title is unchanged. The Oct 15 version is in git
history.
- ~~Case study 1, "Root cause": a stray drafting sentence~~ REMOVED
  2026-10-14 (found by Claude; Gerard approved). It wasn't in what the outside
  readers saw.
- At publish time: an "On this page" link list, and the evidence table's
  repo-relative paths turned into GitHub links.

OUTSIDE READERS (shared with m7-writeup-draft.md; recorded by Claude
2026-10-14). Gerard emailed five people on 2026-10-13. Each got only the two
"In short" sections (M7 and Phase 2, with the pre-Oct-14 wording) and five
questions. Readers are not named here, because this repo is public.
- Reader 1, replied 2026-10-13: a senior Azure and AI-security practitioner
  who has built agents in production.
  - Understood it only "somewhat", "based on my guesses"; found it hard to
    follow.
  - Stopped on "IIP" and "M8-M14". Neither was on the list of words the email
    asked about. They are internal labels, and neither page or glossary
    defines them (checked 2026-10-14).
  - Had to guess what "copy" meant (marketing copy).
  - Came away with "learning about building agents for automation". The
    troubleshooting and deciding-what-to-trust point of "What it's really
    about" didn't come across.
  - Read every bullet "to try to get a complete grasp"; named none as the
    one that made him read on.
  - Admitting what doesn't work yet: "Believable." Keep those bullets.
  - Suggested: first say what the project is trying to accomplish, then a
    diagram of the stages.
  - DECIDED (Gerard, 2026-10-14): no change to "In short" until the other
    four replies are in, so their answers stay comparable with this one.
    Then rewrite it goal first, with no internal labels and a diagram at the
    top, and send the rewrite back to Reader 1.
    *(Superseded 2026-10-15, Gerard: rewrite now rather than wait. Two days
    in, with one reply of four, the likelier problem was the size of the
    ask: the email was 731 words plus five written answers, under a subject
    line promising two minutes.)*
- Readers 2-5: no reply yet (2026-10-14; still none 2026-10-15).
  *(2026-10-20: Reader 2 replied; see the entry at the end of this list.)*
- 2026-10-15 (Gerard decided; Claude drafted): "In short" rewritten on both
  pages (goal first, no internal labels, the diagram
  images/in-short-stages.svg; troubleshooting moved to the first bullet;
  "How it works" cut because the diagram shows it). 260 words became 210.
  Gerard approved it as written. Follow-ups, as replies in the original
  threads: the readers who haven't answered get Part 2's "In short" only (about 210
  words) plus the diagram and ONE question ("After a 30-second skim, what do
  you think this project is?"); Reader 1 gets both rewrites and "did this fix
  what stopped you?". The previous wording is in git history.
- Reader 1, second reply, 2026-10-15 (to the rewrite): "This is awesome and
  makes absolute sense." The rewrite fixed what stopped him. Two suggestions,
  both about the agent rather than the summary: (1) a human in the loop at the
  end, to validate results and keep tuning; (2) would the agent notice if
  fonts, files or colours changed, and alert someone to take a look.
  Claude's notes: colour is the one it does catch (item4's planted flaw is a
  colour violation, and the audit fails it). The brand check judges the colour
  scheme alone, so a changed logo passes unnoticed, and so does a changed
  font unless it hurts legibility (the separate legibility check caught
  item3's 3px title) (m7-orientation.md, "brand_consistent is palette-only"; Todoist [stretch]
  item). The results page is where a person reviews a result, but nothing
  feeds that review back into tuning. **Decided (Gerard, same day):** add
  both, honestly. M7 page "Known limits" gains "The brand check judges colour
  only"; this page's "After Phase 2" gains "A person in the loop". Claude
  drafted both; Gerard approved them as written.
- Reader 2, replied 2026-10-20 (to the Oct 15 follow-up: Part 2's rewritten
  "In short" only, the diagram, one question). She passed it to a technical
  reader she knows and relayed his comments; she added one framing of her own.
  Recorded by Claude from the email, read in Gerard's Gmail with his
  knowledge.
  - The technical reader could not follow the story or quickly grasp the
    significance. He pieced it together only because he knows the field.
  - "The summary read out numbers but there was no context and no
    information to the significance to the finding."
  - Reader 2's framing: it reads like "listing tasks" rather than "telling a
    story about your impact."
  - He could tell from the start that it read as AI-written, and found that
    odd from someone studying AI. His suggestions: have an LLM proof
    everything and ask whether it sounds AI-written; record yourself reading
    the summary aloud and listen to whether you can follow it.
  - Claude's notes: both main points are fair, and both land on Claude's
    work. Claude drafted all of this page's prose, the Oct 15 rewrite
    included (see WHO WROTE THIS DRAFT), so "reads as AI-written" is
    accurate. The counts in "In short" (seven stages, six complete, six case
    studies, one test upload) are exactly the "numbers without
    significance": none says what it changes for the reader. Reader 1's
    "makes absolute sense" came after he had read the first version and
    asked for this shape; this reader saw the rewrite cold, so his reading
    is the better test of a first impression.
  - ~~NOT YET DECIDED (Gerard): whether and how to rewrite "In short" again,
    and in whose voice.~~ Decided 2026-10-20 (Option A, his own voice); done
    2026-10-26 (see GERARD'S "IN SHORT" above).
-->

## In short

**The goal:** deploy the AI agent from a development environment to a secure
app in Azure, with no keys or passwords used in the code to leak, a sign-in to
see results, and email alerts automatically sent when something breaks. This
is self-study, hands-on work for Microsoft's AI-103 exam, Developing AI Apps
and Agents on Azure.

![Two-part diagram. Part 1: an AI agent takes a topic and an image, writes a title and text, checks the text against a fact sheet, audits the image and reports pass or fail. Part 2: the same agent runs in Azure: upload, queue, an Azure Function runs the agent, the result is saved, and you sign in to view it.](images/in-short-stages.svg)

- **Why do this:** troubleshooting and root cause analysis (RCA), the way an
  engineer works a ticket. Through this work, several items looked right but
  were not: a permission that matched Microsoft's documented minimum and still
  failed, an alert that fired but never sent its email, and a deployment
  preview whose "harmless noise" would have wiped real settings. Six are
  written up as case studies below: symptom, evidence, root cause, fix.
- **What it shows:** the work was split into seven stages, each with a
  definition of done written first and shown with evidence. All seven are
  complete. After every big change, the same test upload with a known answer
  was rerun, so a break showed up right away.
- **What was torn down after use:** some parts were built, proven and then
  switched off intentionally: the private network connections to save cost,
  and the stricter sign-in rules, before the Entra ID P2 trial ends. "Known
  limits" lists everything that is no longer running and why.

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
- **OIDC:** an open sign-in standard. Here, GitHub Actions uses it to prove to
  Entra ID which repository and branch a deploy is coming from, with a
  short-lived token instead of a stored password or secret.
- **Federated credential:** an entry on an identity in Entra ID that says
  "trust tokens from this issuer, for this subject". It's what lets GitHub's
  token, or the sign-in page's managed identity, stand in for a client
  secret, so no secret is stored anywhere.
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
| **M8** (Sep 2026) | Everything that already existed, described in Bicep | A `what-if` that lists only diffs written down and justified one by one in a register |
| **M9** (Sep 2026) | Two managed identities and their roles, from a written RBAC model | The role assignments exist and match the model, row by row |
| **M10** (Sep 2026) | No keys: every tracked script moved to Entra ID sign-in | The M7 agent's acceptance test re-run on the keyless code, and no surveyed script reading a key |
| **M11** (Oct 2026) | The app: upload, Event Grid, queue, Function, agent, result, and a sign-in page | An upload produces a correct result, and a member of the viewers group can sign in and see it |
| **M12** (Oct 2026) | Private networking: private endpoints and a storage firewall | The app still worked end to end with the private paths verified. Then torn down, Bicep kept |
| **M13** (Oct 2026) | Conditional Access: phishing-resistant sign-in for the results page | Six sign-in tests passed with the policy On, and the policies are exported. Then rolled back ahead of the licence trial's end: policies deleted, security defaults back on |
| **M14** (Oct 2026) | Operate: deploys from GitHub, alerts, tracing | A push deploys the Function; a failed upload emails an alert; one upload's trace shows every step |

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

 Around it: Bicep for the Azure resources and Entra objects
            App Insights + Log Analytics (Entra-only ingestion)
            GitHub Actions deploys over OIDC (a second managed identity, no secret)
```

Mapped against Microsoft's AI-103 study guide (skills measured as of April 16,
2026), Phase 2 covers much of the exam's "Plan and manage an Azure AI
solution" area, plus its observability skills:

| Exam skill area (weight) | Skill named in the study guide | Where Phase 2 does it |
|---|---|---|
| Plan and manage an Azure AI solution (25-30%) | Design Azure infrastructure for AI apps and agent-based solutions | M8, M11 (the architecture above) |
| Plan and manage an Azure AI solution (25-30%) | Configure security, including managed identity, private networking, keyless credentials, and role policies | M9, M10, M12; case studies 2, 3 and 5 |
| Implement generative AI and agentic solutions (30-35%) | Set up observability by implementing tracing, token analytics, safety signals, and latency breakdowns | M14: case study 6 |
| Implement generative AI and agentic solutions (30-35%) | Integrate monitoring into deployed agents, evaluate agent behavior, and perform error analysis | M14: case studies 1 and 6 |

M13, Conditional Access, isn't an AI-103 skill. It's the identity work an app
with a sign-in page needs either way.

**One rule held across the phase.** After each major change to the
app, the same test image (item4 from the M7 answer key, with one planted brand
flaw) was uploaded again. The correct answer is: copy passes first time; the
audit says legible PASS, brand FAIL, accurate PASS. It came back correct with
the Function inside the private network, after the storage firewall went on,
after the teardown, with Conditional Access On, after the first GitHub deploy, after
tracing was added, and after key authentication was switched off. Each of
those result files is committed.

## Case studies

Each one follows the same order: what was seen, what was checked, what the
cause turned out to be, and what changed. Several include a wrong turn,
because that's part of the record.

### 1. The alert that fired but never emailed (M14)

**Symptom.** An alert was built to email when an upload fails every try and
lands in the poison queue. That's the one signal that means "the app is
broken". To prove it, a failure was caused on purpose: pause the Function,
upload, delete the image, un-pause. That's Gerard's method, with a pause
Claude added. The alert fired, and its history said "Action group executed"
0.2 seconds later. No email arrived. Neither did one for the alert resolving,
or for a second firing about an hour later.

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
Verified, which retired the obvious theory, an unverified address.

**Fix.** The action group was re-saved with no change to any property, which
causes no drift from the Bicep. About twelve minutes later, the Resolved
email for the second alert arrived: the first email this alert ever
delivered. The next day a deliberate re-fire produced a Fired email within two
minutes of the alert. That's 0 of 3 delivered before the re-save, and 2 of 2
after.

**What it doesn't prove.** The re-save can't be separated from the time that
passed. Background propagation would look the same. Separating them would
mean breaking a working group on purpose, and the lesson is the same either
way.

**Lesson.** A portal "Test" button proves the last step of a path, not the
path. Prove a new action group with one real alert.

### 2. The failed upload that couldn't be released (M11)

**Symptom.** A failed upload should be retried after one minute
(`visibilityTimeout`), and after two failed tries move to the poison queue.
In practice, failed tries retried after **10 minutes, not 1**. It surfaced
while testing the poison path with Gerard's method: upload, then delete the
image so the Function must fail.

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
20 minutes, which pointed at the custom role. Gerard chose to test the custom
role on its own, on his identity, with a negative control: the update was allowed
with it and refused without it. With Contributor removed, the Function then
passed cleanly (no 403, retry after about 100 seconds). Later the custom
role was verified alone, about 24 hours after the old roles were deleted:
the retry, then the poison move, with zero permission errors in the
Function's logs.

**Still open.** Why the first assignment took more than 65 minutes. It was
either a slow custom-role assignment for a managed identity, or a permission
refresh triggered by adding and removing Contributor. Both are recorded, and
neither is claimed.

**Lesson.** A documented minimum is where to start, not proof. The failure
path (release, retry, poison) only runs when something goes wrong, so it has
to be tested by making something go wrong.

### 3. The right role at the wrong scope (M11)

**Symptom.** Creating the Event Grid **event subscription**, the rule that
sends each "a blob was uploaded" event to the queue as a message, failed three times in about 20
minutes: *"Managed Identity Authorization Error."*

**Evidence.** The role was there. Gerard confirmed with `az role assignment
list` that the topic's identity held Storage Queue Data Message Sender on the
queue. Least privilege says to grant that on the one queue it writes to, and
that's what had been granted.

**Root cause.** Claude's hypothesis, which the next deploy supported: Event
Grid checks the identity's permission **when it creates the event
subscription**,
and checks it against the destination's resource ID, which is the storage
account, not the queue. Microsoft Learn's steps also say "on the storage
account".

**Fix.** Gerard approved widening the grant to the account. The redeploy
succeeded first time, and the orphaned queue-level grant was deleted. The
trade-off is written into the RBAC model: the topic can now add messages to
any queue on the account (there are two), but it can't read or delete them.

**It mattered again in M12.** Once a storage account has a firewall, Event
Grid can deliver to it only with a system-assigned identity and the "trusted
Microsoft services" exception (Microsoft Learn). The topic was given a
system-assigned identity in M11 for that reason. With the firewall on in M12,
the test upload still produced a correct result.

**Lesson.** Scope is part of the role. When the role is clearly present and
access still fails, ask *what the service checks against*, and *when* it
checks.

### 4. The deployment preview whose "noise" would have wiped real settings (M8)

**Symptom.** M8 described the existing resources in Bicep. The first
`what-if` reported 7 resources to modify, where the goal was none.
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

Another, `networkRuleSet.bypass` on Search, was missing because the module
was pinned to an old API version. Updating the API version fixed it.

**Fix.** Every writable property was declared as it was found. Every remaining
diff, a property no template can set, went into a **register** with a written
reason. Gerard then amended M8's definition of done from "what-if shows no
changes", which Azure can't produce for these resources, to "no changes
other than the registered ones". That's stricter than it sounds: any line
not in the register is treated as a real change. Every what-if since is
read against the register, and any new line is investigated before anything
deploys. Gerard caught a set of eight unregistered lines that way during
M11. M12's
build found two more dropped writable properties the same way.

**Lesson.** "May contain noise" is a reason to check each line, not to skip
them. The test is the provider schema's `ReadOnly` flag, not how the line
looks.

### 5. "No keys": what the code does versus what the account still allows (M10)

**Symptom.** Before M10, the Foundry account's activity log showed
about ten `listKeys` calls under Gerard's account while the portal was open.
That's expected portal behaviour, but it confirmed key access was still
switched on. M10's goal was that no script reads a key.

**The migration.** All 12 call sites across the nine tracked scripts moved to
Entra ID sign-in. The M7 acceptance test was re-run on the keyless code and
passed, and Gerard certified it. One item's lower score was traced to known variance
in its model-judged scoring, not to the migration. Two things surfaced along the way.

**A script that still read keys.** One script, `m3_analyze.py`, still read two
keys in its own pipeline: an API key (the service's "subscription key"), and a
storage SAS signed with the
account key. Gerard chose to name it as a stated exception in M10's
definition of done rather than leave the milestone quietly open. It was
closed the next day. The REST calls now use bearer tokens, and the SAS is signed
with a user delegation key, which is decision (A), Gerard's.

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

**Fix.** Gerard decided to switch key authentication off on the account
(`disableLocalAuth`, declared in Bicep) once nothing in the project used a
key. A search of the scripts and the Function's code found no key use, and
the account had no connections that could depend on one. The change was
tested in both directions:
- **The key path is closed.** A key fetched just before the change worked
  (HTTP 200). The same key was refused afterwards: HTTP 403,
  `AuthenticationTypeDisabled`. Fetching a key now fails too ("Failed to list
  key"), so VS Code's timed fetch stops, rather than collecting keys that no
  longer work.
- **The Entra ID path still works.** The test upload gave item4's correct
  answer, and a local smoke test of all nine keyless call paths passed.

**Then storage and AI Search.** The same change was made on the project's
storage account and its AI Search service. Each was measured first, to see
what still used a key, then tested in both directions. All three services now
refuse keys. On storage, the only key traffic in 30 days turned out to be
Azure's own deployment calls, which still succeed after the change.

One detail differed from the documentation. Microsoft Learn's page on this
setting says to expect a 401. The service returned 403. Gerard stopped the run
there, because it wasn't the predicted result, and the error text settled it:
the refusal was for the key, not the network.

**Lesson.** "The code is keyless" and "the account is keyless" are different
claims. Check the role's permissions, not just the code's behaviour.

### 6. The SDK that doesn't trace its own tools (M14)

**Symptom.** The goal for tracing was to see, inside one upload, each step of
the agent's run and each of its three tools: `get_fact_sheet`,
`evaluate_draft` and `audit_thumbnail`. Microsoft's docs for this SDK version
(`azure-ai-agents` 1.1.0, the "classic" Agents API) show a few lines to turn
tracing on.

**Evidence.** Before writing anything, the exact package set was installed
in a separate test environment, and the SDK's tracing code was read. It has a helper that creates an
`execute_tool` span, **and nothing in the SDK calls it.** With message content
recording off (it stays off, because the prompts carry the store's fact
sheet), the tool names weren't recorded anywhere else either. Following the
docs would have produced a trace with every agent step and no named tools.

**Fix.** The M7 orchestrator already wraps each tool in a helper, `logged()`,
that records its inputs and outputs. It refuses to run if the wrapper changes
the tool definitions the model sees. **Gerard decided** to add one
span around that helper at startup, rather than accept unnamed tools. No
certified file changed, and the orchestrator's own check proves the agent's
tools didn't move. An offline negative control confirmed the check is live:
a wrapper that hides the tool's signature is refused.

**Result.** One traced upload gave the correct item4 result, and 61
spans under a single operation ID. That's the host's request, the agent's
steps, and `execute_tool` spans for `get_fact_sheet`, `evaluate_draft` and
`audit_thumbnail`, in that order. The trace answered a question the logs
couldn't: about 10 of the 22.5 seconds the agent spent working were our own
tools (7.1 seconds for the judge, 3.1 for the image audit). In that run, the
Vision call itself took 0.2 seconds of the audit's 3.1. One upload costs about 200 KB of log ingestion, 76 KB of it the new
spans.

**What it still can't see.** The judge inside `evaluate_draft` reaches its
model through the `openai` package, which this lean package set doesn't trace.
Its 7.1 seconds show up as one block. That also means tracing doesn't fix a
known gap from M7: token counts read from the agent leave out the judge's
tokens (and the image audit's own vision calls).

**Lesson.** When the docs and the installed code might disagree, read the
code. Reading it changed what got built.

## Smaller findings worth recording

- **Global Administrators bypass "assignment required."** An app set so
  only assigned users can sign in still lets a Global Admin through
  (Microsoft documents this under sign-in error AADSTS50105). The sign-in gate was tested with a
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
  account was created first. That account is excluded from every policy.
- **A test that couldn't have failed the right way (M10).** One planned test
  said a 401 or 403 from AI Search would mean "the free tier doesn't support
  keyless sign-in". But the RBAC model deliberately gave no role on Search, so
  the test would have returned 403 for a missing role, and been read as a tier
  limit, pointing toward recreating Search on a paid tier: a one-way change
  with a monthly bill. The role was assigned first, and keyless Search then
  worked on the free tier.
- **A queue metric couldn't drive the poison alert.** `QueueMessageCount` has
  no per-queue breakdown and refreshes daily (Microsoft Learn). So the alert
  is a log search on the host's own "moving message to the poison queue" line,
  checked every 15 minutes for $0.50 a month.

## Known limits, stated plainly

- **The private networking isn't running.** M12's private endpoints and
  storage firewall were built, tested and torn down to save cost
  ($15.60 a month running, from Azure's retail price list). The VNet and its
  security groups stay, at $0. One Bicep parameter rebuilds the rest for a
  demo. Today the storage account is back to its pre-M12 network settings.
- **Conditional Access is temporary.** It runs on a 30-day Entra ID P2
  trial. The policies were deleted and security defaults turned back on
  ahead of the trial's end, and the exported policy files are the record.
  Afterwards both an admin sign-in and the break-glass account's sign-in were
  asked for MFA, so the rollback didn't leave the tenant unprotected.
- **The Function's Foundry role is broader than it needs.** Foundry User
  grants everything on the account (`Microsoft.CognitiveServices/*`). One
  shared AI Services account serves both the chat models and Vision, so
  "narrowest role at narrowest scope" can't be met for that row. It's
  recorded as an accepted trade-off.
- **AI Search is on the free tier.** It can't take a private endpoint, and its
  tier can't be changed after creation.
- **The agent uses the classic Agents API, which retires in March 2027.** The
  migration is planned and will rebuild the agent-level tracing and the
  agent's network isolation. The isolation design is costed (about $98 a
  month as a full private setup) and written up, not built.
- **Two open questions are recorded, not answered:** why the alert email
  started working (case study 1), and why the first custom-role assignment
  took more than 65 minutes (case study 2).

## Lessons worth keeping

- **Test the path that only runs when something breaks.** The release,
  retry, poison and alert paths all looked fine until a failure was caused on
  purpose (case studies 1 and 2).
- **A test has to be able to fail for the reason it's looking for.** The
  Search test would have read a missing role as a tier limit (Smaller
  findings).
- **Present isn't sufficient.** The right role at the wrong scope fails
  exactly like no role (case study 3).
- **Treat "noise" as a list to check** (case study 4).
- **Check what the identity can do, not just what the code does** (case study
  5).
- **Read the code when the docs might be wrong** (case study 6).
- **Price it before building it.** Every build that added cost was priced
  first, from Azure's retail price list, and the cost of tearing down and
  rebuilding was part of the networking decision.

## After Phase 2

- **The AI-103 exam.**
- **Moving the agent to Microsoft's new Agents API,** before the classic API
  retires. The agent's network isolation, designed and costed in M12, gets
  built as part of that move.
- **A person in the loop.** Today a person reads each result on the results
  page, but nothing they decide there goes back into the agent. Recording
  whether the reviewer agrees with each verdict would show where the checks
  drift from human judgement, and what to tune next.

## How this was built

Built with Claude (Anthropic) as a coding and analysis partner, with work
divided on purpose, as in Phase 1.

**Gerard** made the design decisions, often choosing among options Claude laid
out, and did all of the Azure, CLI, portal and git work: every what-if,
deploy, test, upload and query. Recorded decisions include:
- amending M8's definition of done to the register standard;
- naming M3's key use as a stated exception rather than leaving M10 open,
  then decision (A), a user delegation SAS;
- the queue design, and the M11 build choices: remote build, Python
  3.14, the topic as blob metadata, one agent per upload;
- widening the Event Grid grant to the account;
- a custom queue role reached in two stages, rather than the broader built-in
  role;
- 7-day soft delete for blobs and containers;
- the group-based sign-in gate, and starting the P2 trial;
- which private endpoints to build, and to tear them down after the evidence
  window;
- building the agent's network isolation inside the API migration rather than
  now;
- the order of M14's parts, trusting only the `main` branch for deploys, the
  alert frequency, the lean tracing packages, and naming each tool call;
- switching key authentication off on the Foundry account.

He also caught problems himself:
- unregistered what-if diffs and an empty queue check;
- a deprecated role that Claude had wrong.

He also pushed back on certifying data whose history was in question, which
surfaced two provenance gaps.

**Claude** wrote the Bicep, the Function code, the tracing setup, the probe
and test scripts, the commands Gerard ran, and the documentation drafts,
including this page.

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
| Regression uploads (item4) | `scripts/results/*_function_item4_*.json` (CA001 On; M12 stages 2 and 3; teardown; OIDC; tracing; keys off) |
| Key authentication off (case study 5) | `infrastructure/iip/modules/foundry.bicep`; `infrastructure/iip/README.md`, "Keys off" |
| Case study 1 (alerts) | `m14-prep.md`, Part 2 and "the delivery fault" |
| Case study 6 (tracing) | `m14-prep.md`, Part 3, "the build and the run" |
| Full session log | `STATUS.md` (the Phase 2 entries) |
