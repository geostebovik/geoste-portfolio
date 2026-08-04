# Multi-Agent Client Delivery System — Project Plan Outline

Status: **outline only, not started.** Written to hand off to a dedicated
agent-development project/session. Source: lessons from the first
real engagement (Scottsdale AZ realtor / Anne Collins), not theory.

## Problem statement

If Gerard takes on multiple clients of this type (YouTube channel
cleanup/consulting for local service businesses) at once, the manual
workflow used for the first client — audit, draft, verify, publish,
correspond, invoice, all done by hand through YouTube Studio's UI and
Gmail — won't scale linearly. The question is whether/how to automate
parts of it, and with one agent or several specialized ones.

## Connection to AI-103 certification work

Gerard is separately working toward **Microsoft Certified: Azure AI
Apps and Agents Developer Associate (AI-103)** — "Developing AI Apps
and Agents on Azure" — in a dedicated Claude project set up for agent
development, building from "hello world" to a full working agent. This
outline is written to be handed to that project; the two efforts should
converge into one build, not run as parallel disconnected exercises.

AI-103's five exam domains (confirmed against Microsoft's official
study guide, effective April 2026) map cleanly onto this project —
closer than the original "multi-modal document intelligence" framing
suggested:

- **Generative AI / agentic solutions** (largest weight, 30–35%) — the
  orchestrator/multi-agent system itself (Phases 2–3 below).
- **Computer vision** — a genuine, currently-unfilled gap: the intake
  checklist (`template/intake-audit-checklist.md`) already calls for
  reviewing every video's *thumbnail*, but the actual work done this
  engagement was text-only (descriptions, contact info, chapters).
  Thumbnail auditing — brand consistency, legibility, correct info in
  the image itself — is a real business need and a clean vision-domain
  module. See the audit/research agent description in Phase 3.
- **Text analysis** — the description audit-and-rewrite work already
  done manually on 83 videos. This is the best-understood part of the
  process precisely because it's been done by hand enough times to know
  its real shape (see Phase 1).
- **Information extraction** — parsing the analytics CSV export now;
  later, contracts/intake forms once the template library (separate
  task) exists.
- **Planning AI solutions** — cuts across all of the above; not tied to
  one component.

**Two guardrails for building this as a joint cert-and-business
project, not just a cert project:**

1. The exam's scope should not override the human-in-the-loop
   checkpoints below. Treat the AI-103 project as the sandbox where
   those checkpoints get built and tested — it should not touch a real
   paying client's channel until Phase 1 is further along, regardless
   of what's useful to demonstrate for the exam.
2. AI-103 completion has real, time-sensitive career value on its own
   (active job search, 16+ months in). Don't let "make it good enough
   to also be a business tool" delay finishing the certification itself
   — the cert has a deadline-shaped value the business tool doesn't.

## Non-goals (explicit, to prevent scope creep)

- Not trying to replace Gerard's relationship management, sales, or
  judgment calls with clients.
- Not trying to fully remove human review from anything that (a)
  publishes live to a client's public channel, (b) touches money, or
  (c) makes a compliance-adjacent judgment call (e.g., license numbers,
  legal names, contact info accuracy).
- Not aiming for production-grade robustness on day one — see "Learning
  framing" below.

## Phase 0 — prerequisites (before any agent work starts)

1. **Template library must exist first** (see template-library task) —
   agents need something correct to fill in; building automation around
   ad-hoc documents means automating inconsistency.
2. **YouTube Data API / Analytics API access**, not just Studio-UI
   browser automation. Today's session hit two concrete failures from
   UI-only automation: the Chrome extension disconnected mid-edit
   (nearly leaving an unsaved partial change), and a video-selection
   mix-up almost led to editing the wrong video based on a
   similarly-named/thumbnailed duplicate. An API-based read layer
   (video list, descriptions, metadata) would have prevented the
   mix-up entirely — Studio UI has no reliable "confirm this is the
   video you think it is" signal beyond visually checking a screenshot.
   Writes (publishing descriptions) may still require Studio UI or an
   authenticated API write path — worth researching whether the
   YouTube Data API supports description updates directly, which would
   remove UI fragility from the write path too.
3. **A defined, repeatable intake questionnaire** (extend
   `template/intake-audit-checklist.md`) — the Anne engagement's early
   sessions spent real time on ad hoc scoping (what's broken, what
   matters most, contact info, brand assets) that a standard intake
   form could front-load.

## Phased build approach

**Phase 1 — manual, templated, no automation.**
Run at least one more client engagement using the Phase 0 template
library, by hand, end to end. Goal: find out which steps are actually
repeatable/mechanical versus which ones require judgment every time
(they will differ per client — e.g., Anne's "friend rate + no formal
agreement" situation is not representative of every future client).
Do not start building agents until this phase surfaces a real, observed
pattern — not a guessed one.

**Phase 2 — single orchestrator agent, narrow scope.**
One agent, not several. Automate only the steps that Phase 1 showed to
be genuinely mechanical and low-risk: compiling an audit summary from
raw data, generating first-draft descriptions against the template,
drafting (not sending) status emails, drafting (not sending) invoices
from logged hours/scope. Every live-write action (publish to channel,
send email, mark invoice sent) stays a human-confirmed step, same
pattern used throughout the Anne engagement in this session.

**Phase 3 — evaluate splitting into specialized agents.**
Only decompose into multiple agents (e.g., intake/scoping,
audit/research, execution, QA/verification) if Phase 2's single agent
demonstrably struggles — context window strain, tool-scope conflicts,
or genuinely parallel workstreams. Splitting preemptively adds
coordination complexity (state handoff between agents, consistent
context) without a proven need. If it does happen, a plausible split:

- **Intake & scoping agent** — runs the standard questionnaire, produces
  the initial living-status-doc and project plan draft for human review.
- **Audit/research agent** — read-only: pulls channel data via API,
  finds errors/gaps against the checklist, produces itemized findings.
  Includes a vision-capable pass over thumbnails (brand consistency,
  legibility, correct info in-image) — the AI-103 computer-vision
  domain module, and a real gap in the process used on the first
  client. Never writes to the client's channel.
- **Execution agent** — drafts corrected content against approved
  findings; publishes only after explicit human confirmation per item,
  same discipline used today (verify live text, save, confirm
  Save/Undo greyed out).
- **QA/verification agent** — independently re-checks the execution
  agent's published output against the approved draft. This is the
  role that would have caught the dropped-space typos ("Annewith",
  "witheXp") before a human had to.

## Human-in-the-loop checkpoints (non-negotiable, drawn from today)

These are not hypothetical — each one actually happened in this
engagement and would need an equivalent gate in any automated version:

- Confirming scope/footer decisions that touch a still-open client
  question (the 2p1WqC5uJtY footer decision, made knowingly ahead of
  Anne's answer on the channel-wide format question).
- A direct instruction to pause all live changes pending client input.
- Catching a wrong-video mix-up before publishing to it.
- Any decision involving money (rate, invoice amount, payment terms).
- Anything compliance-adjacent (the license-number question).

An agent design that can't reproduce "notice this needs a human, stop,
and ask" is not safe to point at a live client channel or invoice.

## Risk register

- **Wrong-client / wrong-video actions** — already nearly happened
  once manually; higher-stakes if agents act faster/more autonomously.
- **Credential/access scope** across multiple clients' YouTube Studio
  and Gmail accounts — needs a real access-control design, not shared
  ambient login.
- **Over-trusting AI-drafted compliance-sensitive text** (license
  numbers, legal names, factual claims) without a human compliance
  check.
- **Tool fragility** — browser-automation disconnects (observed today)
  argue for API-first design wherever possible (see Phase 0).
- **Cost/complexity creep** — multi-agent orchestration has real
  engineering and API cost overhead; only justified once volume
  justifies it (see success criteria below).

## Success criteria — when to keep building vs. stop

Suggest setting this explicitly rather than open-ended:
- Only invest past Phase 2 if there are 3+ concurrent paying clients of
  this type, or a clear signal (waitlist, referrals) that more are
  coming soon.
- If it stalls at Phase 1 or 2, that's not a failure — the template
  library and single orchestrator agent are still directly useful on
  their own.

## Learning framing

This is explicitly being pursued partly as a personal learning project
— specifically, as the build vehicle for AI-103 certification work —
separate from pure business ROI. Worth defining three different "done"
bars up front so none gets judged by the wrong standard:
- **"Good enough to pass AI-103"** — demonstrates the five exam domains
  competently; has its own deadline-shaped value independent of the
  other two bars. Don't let this slip because the tool isn't perfect.
- **"Good enough to have learned from"** — Phase 2 working end-to-end
  on one real (or simulated) client, even with rough edges.
- **"Good enough to run the business on"** — Phase 3, with the human
  checkpoints above actually enforced, not just designed.

Climb this for the sake of each rung, not because it might turn into
something bigger. Certification, then a genuinely useful tool, then
maybe a second client's worth of value — each is worth reaching on its
own. A larger outcome (an independent business, or something worth
someone else acquiring) is a possible bonus on top of that, not the
standard this project needs to hit to have been worth doing.

---

## Merge note (added 2026-08-03, IIP session)

This plan is no longer a handoff to a separate agent-development
project — confirmed 2026-08-03 that no such separate project exists.
It's folded directly into IIP as a re-scoped **M7** (see `STATUS.md`).

What changed on merge, decided 2026-08-03:

- **M7 proceeds on synthetic/simulated Anne-engagement-style data**,
  not gated on this doc's own Phase 1 requirement (a second real client
  engagement run by hand first). That gate remains real and correct for
  the *business* — Phase 2 should not touch a second real client's
  channel until a second manual engagement has actually happened — but
  the *cert* milestone (M7) doesn't need to wait on landing a client,
  which isn't fully controllable on a timeline. Real Phase 1 evidence
  still governs when this ever touches a live second client.
- **Real client data/credentials get their own resource boundary**,
  never the IIP lab environment: `rg-ycc-dev-wus-01` / `kv-ycc-dev-wus-01`
  (placeholder naming, West US, matching IIP's own `wus`-no-numeral
  convention). Not needed yet for the synthetic-data M7 build, but
  stood up ahead of need per governance decision, not after the fact.
- **M6's evaluation harness pattern carries forward directly**:
  Groundedness/Relevance/F1-style checks apply to "is this drafted
  description grounded in the channel's real data" the same way they
  applied to loan-agreement Q&A — a real skill transfer, not a relabel.
- **The computer-vision module (thumbnail audit)** fills the one exam
  domain IIP hadn't touched through M6.

This document stays as the reference for the full phased plan,
non-goals, risk register, and human-in-the-loop checkpoints. `STATUS.md`
is the living tracker; this file isn't re-edited session-to-session the
way `STATUS.md` is, except to log a merge/scope decision like this one.

---

## Decoupling note (added 2026-08-04)

The Aug 3 merge decision assumed this plan's own business thesis would
keep being validated in real time. It wasn't: Anne Collins declined to
continue at the quoted, already-discounted, friend-rate price — she
understood the offer and still judged it not worth the cost. That's a
real, if single, data point against the underlying value proposition, not
a misunderstanding or timing problem that better packaging would have
fixed.

As of this date, IIP's **M7** (`STATUS.md`) is decoupled from this plan.
It no longer builds toward this document's Phase 2 orchestrator using
Anne-engagement-style data. M7 now targets a neutral, synthetic
small-business content-review scenario instead — same technical shape
(orchestrator agent, evaluation-harness reuse, vision module), no longer
justified by or dependent on this specific business thesis.

This document is retained as a real case study — the human-in-the-loop
checkpoints, risk register, and phased-build reasoning are still sound
regardless of whether this particular niche pans out — but it is no
longer the active target for any current build. "Is this a real business"
is an open question, gated on real evidence (a paying, non-discounted
client), not something to keep building toward on assumption.
