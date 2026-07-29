# Setup Notes for the YouTube Channel Project — Mined from IIP/AI-103 History

Scope note up front: this is process and collaboration patterns pulled from
an unrelated technical project (Azure/AI cert work), not YouTube expertise.
It tells you how to *set up the working relationship* for success — nothing
here is a content or growth strategy. That has to come from your other
inputs.

---

## Patterns that worked — bring these over

**One living status doc, edited in place, no dated copies.**
Google Drive had no in-place-edit tool, so every "update" created a new
file — five dated `MASTER-REFERENCE` copies piled up before it got fixed by
moving the doc to GitHub, where it could actually be edited in place. Before
this project starts producing real work, decide *once* where the canonical,
current-state doc lives (a Doc, a Notion page, this Claude Project's own
project knowledge — whatever the tool is, as long as it supports true
in-place edits) and commit to updating it there, every session, instead of
letting versions multiply. Structure that held up well: current state →
decisions made and *why* → open questions → next action.

**Record the reasoning, not just the decision.**
Every real decision in this project got a one-line "why," not just a
choice — e.g., the evaluator judge model was picked specifically because it
wasn't one of the two models being compared (avoids grading bias), not
because it was convenient. For a channel audit or strategy doc: don't just
write "post 3x/week," write the data point or reasoning behind it. Decisions
without reasons are impossible to defend later or revisit when circumstances
change.

**Isolate variables before testing anything.**
The evaluation design deliberately fed both candidate models the *same*
full context so any difference in results could only be attributed to model
quality, not to inconsistent inputs. Directly applicable to channel
experiments: if testing whether a new thumbnail style improves CTR, don't
change the title at the same time — you won't know which change caused the
effect. Any "let's try X and see if it helps" idea should specify what's
being held constant.

**Flag limitations honestly instead of overselling.**
The evaluation set for this project turned out to only test easy, clear-cut
questions — a real gap, and it got written down as a known limitation
rather than glossed over. For client-facing work, this matters more, not
less: any audit or recommendation should state its own blind spots (small
sample size, short observation window, unverified assumption) rather than
present findings with more confidence than they've earned.

**Verify before trusting, especially your own outputs.**
Multiple points in this project involved checking a claim against the
primary source instead of trusting a first answer — confirming a file
landed correctly by fetching it back rather than trusting a push
confirmation, reading actual code before renaming a shared variable,
searching current documentation instead of relying on possibly-stale
knowledge. For channel work: verify claims against actual analytics data,
not impressions or generic "best practice" claims that may not hold for
this specific channel/audience.

**Reuse what already exists before generating new work.**
A full extraction of the source document already existed from earlier work
and got reused directly instead of re-deriving it. Before generating new
strategy or content from scratch, audit what the client already has —
past analytics history, existing branding assets, prior scripts/thumbnails
— and build on it rather than starting cold.

**Cheap-to-reverse decisions don't need to be perfect, just made.**
When a choice was genuinely uncertain but low-stakes and easy to undo later
(which model should grade the outputs), the move was to decide now on the
best available reasoning and explicitly note it as revisable, rather than
stall. Good default for things like posting cadence, title formulas,
thumbnail styles — pick, measure, adjust, don't wait for certainty.

---

## Friction points — guard against these

**Don't front-load jargon before the big picture lands.**
The biggest breakdown in this project happened when technical detail (SDK
class names, API specifics) got introduced before the overall shape of
"how the pieces connect" was established — it produced a copy-paste loop
instead of real understanding, and had to be explicitly walked back. For a
new domain, the risk is the same shape even if the vocabulary is different
(platform algorithm mechanics, analytics terminology, editing jargon):
establish the end-to-end picture in plain terms first, in small concrete
steps, before naming tools or introducing terminology. If it's unclear
whether a concept is already familiar, ask before explaining it.

**Watch for fatigue quietly degrading decision quality.**
Late in a long session, after an interruption, the interaction pattern
shifted from genuine engagement to reflexive copy/edit/move-on — a real
signal, not a character flaw, that it was the wrong time for detail work.
What worked was naming it directly, stopping, and resuming fresh next time
with a concrete recap. Build natural stopping points into this project
rather than pushing through when engagement visibly drops.

**Don't let a channel (or client) grade itself.**
The reasoning behind picking an independent judge model — not one of the
two things being compared — has a direct parallel here: don't evaluate a
channel's success using only metrics the channel itself chose to highlight.
Cross-check against independent or platform-wide benchmarks where possible.

**Curated metrics/questions shape what you'll ever find.**
A related lesson from this project: an evaluation set only tests what its
author thought to ask, and everything outside that scope stays invisible.
Applied here — don't just track the easy, flattering numbers (views,
subscriber count). Make sure whatever gets tracked actually tests the
things that matter for the client's real goal (retention, click-through,
conversion), not just what's convenient to measure.

**Renaming/changing something already in use can break it silently.**
A near-miss in this project: renaming a shared config value without
checking what already depended on it would have silently broken working
code — no error, just quietly wrong behavior. The channel equivalent:
before renaming a series, changing an established posting schedule, or
altering branding elements, check what's already "wired" to it (playlists,
external links, audience habits, muscle memory) rather than assume a clean
change is free.

**Pick one source of truth early, and mean it.**
The Drive-file sprawl happened because there was no discipline yet — best
guarded against from day one here by deciding explicitly where the current,
authoritative version of any given thing (strategy doc, content calendar,
brand guidelines) lives, before work starts accumulating in multiple places.

---

## Suggested starting shape for the new Claude Project's custom instructions

Mirroring the structure that worked for this project — you may not need
every section on day one, but it's a reasonable skeleton to fill in as the
engagement takes shape:

```
WORKING STYLE:
- [How involved do you want to be in drafting vs. reviewing? e.g., "build
  strategy with me, don't hand me finished recommendations I haven't
  reasoned through" — or the opposite, if this project calls for more
  autonomy than IIP did]
- Correct me when a suggestion isn't aligned with platform best practices —
  explain why, don't just flag it
- Ask if I'm already familiar before explaining a new platform feature,
  metric, or piece of terminology
- Flag deprecated or changed platform features/policies before we waste
  time planning around them
- Ask clarifying questions when my requests aren't clear
- Help me improve my prompts/briefs for this project specifically

ENVIRONMENT:
- [Channel name / niche / current subscriber-view baseline]
- [Where the canonical strategy doc lives — pick one, per the lesson above]
- [What tools you have access to: YouTube Studio analytics, editing
  software, any existing brand guidelines]
- [Client relationship shape: are you presenting to them, or working
  directly in their channel?]

KEY LESSONS (fill in as they come up, same as IIP's running gotchas list):
- [Leave this section started but empty — it earns its content over time,
  same as this project's did]
```
