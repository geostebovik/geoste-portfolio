# M7 — An Azure AI Foundry agent that checks its own work

<!--
DRAFT, NOT FOR PUBLICATION. Written 2026-09-15, reworked 2026-09-16.
Held until Phase 2 is ready to go up with it (Gerard's call, Sep 14).
/ai-103/* returns 404 on ostebovik.net (staticwebapp.config.json), so pushing
this file does not publish it.

WHO WROTE THIS DRAFT: Claude drafted all of the prose on Sep 15 from
m7-orientation.md, STATUS.md (Sep 2-14 entries), the commit log and the
results JSON, and reworked it on Sep 16 against the Sep 15-16 results.
Gerard chose the format, scope, audience and authorship arrangement, and is
the editor. Record his edits and decisions inline as he makes them.

FIGURE RULES (STATUS.md "Current next action", revised Sep 16):
- Never 0.244. It was condition A's figure, measured with a schema docstring
  that no longer exists.
- Never "1/15" for colour naming. Sep 14 and Sep 15 each produced a 1-of-15;
  neither is a rate.
- Never combine model-judged and deterministic counts into one figure.
- Never a colour figure for the shipped code without saying WHICH LINE of the
  audit notes it counts. [observed] and [content] differ (Sep 16 finding).

VERIFIED Sep 16 (Claude) against the results JSON:
- 20260915-184006 (a915217, clean tree): 120 rows, 0 errors, 0 unmeasured;
  text 120/120; audit 120/120; five fixtures 150/150 model-judged and 75/75
  deterministic; all eight items 240/240 and 120/120; item6 first-draft
  passes 15/15; item7 first-draft passes 0/15, 2 redrafts each, all failed.
- 20260915-111227 (d46353d): audit 82/119, text 112/119, as logged.
- 20260915-130108 (Run 1, 7c9c305) and 141917 (Run 2, 0dffc01): model-judged
  357/450 and 449/450, deterministic 225/225 both. item3 "cream" by line:
  [observed] 0/45 both; [content] 3/45 and 40/45.
- Sep 14 condition A / B by line: [observed] 11/45 and 2/45; [content] 26/45
  and 5/45. Sep 11 baseline: [observed] 9/15, [content] 15/15.
- 20260916-102211 (c5dc05e, clean tree; audit code identical to 0dffc01;
  recorded prompt, schema, field descriptions and deployment identical to
  Run 2): model-judged 449/450 (the miss is item2 run 5, info_accurate),
  deterministic 225/225. item3 "cream": [observed] 1/45, [content] 34/45
  (image-attribution 20/45). Pre-registered rule (Todoist
  6hWcvG85MfcHj38q): REPLICATED. 34/45 vs 40/45: Fisher p = 0.17. Wilson
  95% interval for 34/45: 0.61-0.86.
- Wilson intervals and Fisher p-values recomputed with scipy.

DECIDED Sep 16 (Gerard): the item3 [content] colour flaw is published as a
stated limit, not fixed. The draft stays held for outside readers and the
Phase 2 group push.

STILL OPEN BEFORE PUBLISHING:
- [CHECK] the AI-103 exam domain weighting.
- [CHECK] whether the repo is public.
- [CHECK] the "How this was built" framing.
- Gerard's edit of the Sep 16 rework, and outside readers for "In short".

GERARD'S REVIEW, Sep 15: he read "In short" and kept it as written. He
judged it longer than ideal, but found that each point says something
significant and leads into the next section. He plans to ask a few people
for an outside read before publishing. The Sep 16 rework (Claude) changes
bullets 2 to 4 because their figures changed. He has not reviewed the new
wording yet.
-->

## In short

- **What it is:** a single Azure AI Foundry agent that drafts marketing copy
  for a fictional hardware store. It checks each draft against the store's
  fact sheet, then audits the thumbnail image for legibility, brand colours
  and factual accuracy. It is the seventh and final milestone of the IIP lab
  build for AI-103.
- **What it proves:** the agent does what it was designed to do, measured
  against a written answer key. In the certifying pass, run on the code as
  shipped, it completed **120 of 120 runs with zero crashes**, and **all 120
  text rows and all 120 audit rows** matched the key. It is the first pass in
  the project with no misses.
- **What it does not do yet:** one test image is entirely orange, and the
  audit still calls its lighter orange "cream," a brand colour that isn't
  in the image. A fix removed the word from the line where the audit
  describes the image (0 of 45 runs, then 1 of 45 on a repeat). It did not
  remove it from the line where the audit explains its brand verdict (40 of
  45, then 34 of 45). The verdicts are right, the word is wrong, and the agent repeats
  it in its summary. It is an open flaw, and this page says so.
- **What it's really about:** deciding what to trust. Most of the work on
  this milestone went into finding out when a result could be believed,
  including several times when a good-looking number turned out to be wrong.

## The scenario

Riverside Hardware & Supply is fictional, and its whole world is defined in
one file, `fact-sheet.md`: hours, services, contact details and a brand
guide. The agent gets a topic and a thumbnail, writes a title and a
description, checks its own draft, and reports.

Eight test items are scored against a written answer key,
`content-items-plan.md`. Five are thumbnail fixtures: two clean controls
and three with exactly one planted flaw each. The other three reuse a clean
thumbnail and exist to exercise the draft-checking and redraft path.

M7 was chosen because it covers the largest-weighted part of AI-103 (agentic
and generative AI) and the one area M1–M6 never touched: computer vision.
[CHECK: exam domain weighting against the current AI-103 study guide]

## Architecture

```
            Orchestrator agent — Foundry Agent Service
            gpt-5-4 · temperature 0 · DefaultAzureCredential
                              |
       +----------------------+-----------------------+
       |                      |                       |
 get_fact_sheet        evaluate_draft          audit_thumbnail
 returns the fact      Groundedness +          text_legible: Vision Read + WCAG
 sheet verbatim        Relevance evaluators    contrast math (no model)
                       (Azure AI Evaluation    brand_consistent + info_accurate:
                       SDK, gpt-5-4 judge)     one gpt-5-4-mini vision call
```

**Azure footprint.** Everything runs in the existing `rg-iip-dev-wus-01`
resource group. Computer vision needed **no new resource**: the Foundry
account is `kind=AIServices`, so Vision uses the same endpoint as the chat
deployments. `m7_orchestrator.py` was also the first M7 script to sign in
as a user through `DefaultAzureCredential` instead of an account key, so any
missing RBAC role on the project would show up there first.

**Operator notes from the build:**

- **Azure AI region support is per feature, not per service.** Image
  Analysis 4.0 is available in West US, but its captioning feature is not.
  "The service is in my region" and "the feature I need is in my region" are
  different claims, so check the one you actually depend on.
- **The agent needs the project endpoint, not the account endpoint.** The
  CLI's `properties.endpoints` only lists account-level endpoints. The
  project endpoint comes from the portal's project Overview.
- **A hung run raises nothing, so watch the service, not just the
  script.** Two certification attempts stalled inside the Agent Service. One
  was stuck in the SDK's status-polling loop, which has no deadline. The
  other was stuck on a network read that never returned. The retry logic
  only catches errors, so it saw neither. The fix has two parts:
  - **Hang guards.** Bounded network timeouts plus a 10-minute deadline per
    item turn a hang into an error that the existing retry handles.
  - **A stall alarm.** Any run of an hour or more gets a check on Azure
    Monitor's `ModelRequests` metric every 30 minutes, and 25 or more
    minutes of zeros counts as a stall.

  The first hang went unnoticed for 55 minutes. With the alarm, a hang can
  go unnoticed for 30 minutes at most.

## Seven decisions worth showing

### 1. When prompt edits kept breaking other checks, split the prompt

At first, all three image checks shared one prompt. A wording fix to one
check broke a different one. Two edits in a row each scored 14 of 15 cells
correct, and each time a different cell failed.

**Diagnosis:** the instructions in a shared prompt were competing for the
model's attention. None of the sentences was wrong. **Decision (Sep 2):**
split the audit into two calls, and only two, because every recorded
interference involved the same two checks. The cost is known and bounded:
one extra image upload per audit. Wording tuning had an unknown cost and no
guarantee of converging. After the split, changing the wording of one check
can no longer disturb the other.

*Why it matters:* this is choosing a fix with a known price over open-ended
tweaking.

### 2. Keep the model for perception, and do the judgment with arithmetic

The legibility check asked a vision model whether text was "readable by a
typical human." The planted flaw was text at **1.19:1** contrast, against
the 3:1 accessibility minimum. It should have been judged "not legible"
every time. Across four 7-run passes, the model called it legible in 0, 6, 5
and 3 of the 7 runs. The 6-of-7 and 3-of-7 passes used the same prompt and
the same image.
The model recovers faint text from pixel values and can't tell that a
person would struggle to read it.

**Decision (Sep 3):** take the judgment away from the model. Azure AI Vision
Read locates each piece of text. Code then measures WCAG contrast inside
each word's outline and compares it with 3:1. The result is **5 of 5
fixtures correct, with the same answer every run**, on a check that had never
been stable.

*Why it matters:* the model was being asked to judge something that can
simply be calculated.

### 3. Give the drafting agent the same source the grader uses

The second version of the agent's instructions scored worse (12/15) than
the first. The instructions told the agent to support every claim with the
fact sheet, but only the judge and the image audit had the fact sheet. The
agent never did. Like an open-book exam where only the grader has the book,
it cut every specific claim until the copy said nothing. (Claude wrote that
version. Both of its bugs were Claude's.)

**Decision (Sep 7, Gerard's call):** add a third tool, `get_fact_sheet`,
instead of pasting the facts into the instructions. The next version scored
15/15 on two consecutive runs.

### 4. Choose the judge model on evidence

The judge model had been carried over from M6 without anyone choosing it.
Three deployments were each run 10 times on two drafts, 60 judge calls in
all. On a draft whose claims are supported but which dodges the topic,
`gpt-5-2` scored groundedness 1.0 in 8 of 10 runs. `gpt-5-4` scored 4.0 in
all 10, which is the metric's documented meaning: groundedness measures
whether claims are supported, not whether they answer the question.
**`gpt-5-4` became the judge (Sep 9).**

That model also writes the drafts, so could it be grading its own work too
kindly? The data answers that. Across those 60 calls, pass/fail was
identical for all three judges, including the two that don't write the
drafts.

### 5. Certify on pass/fail, and never count arithmetic as a model answer

Individual judge scores vary by about ±1 between identical runs, so
certification uses pass/fail against the answer key, never scores.

An earlier result was reported as "225/225." That figure is **retired**:
one of the three image checks is arithmetic and can't vary, so counting it
credited the model with 75 answers it never gave. Model-judged and
deterministic results are now always reported separately, and the probe
script prints them that way.

A related finding came from testing the redraft loop: **a failing draft
that isn't changed at all passes 7 of 10 times when it is simply judged
again.** So a pass after a redraft doesn't show that the redraft fixed
anything. That is why certification uses the first-draft verdict.

### 6. Reject the better-scoring wording when it breaks another check

The last visible defect: on the flawed "tool rental" thumbnail, which is
entirely orange, the audit often described the lighter orange using the
brand colour "cream." The model sees the image correctly and picks the wrong
word: the lighter tones are pale, and "cream" is the only light colour named
in the brand guide.

Two wordings were tested on Sep 14, 45 runs each, with pass/fail bands
written into the commit messages before any results existed. The colour
count below is taken from the audit line that describes the image:

<!-- The last column's "1/15" is item2's info_accurate baseline, NOT the banned
colour figure. Same digits, different measurement. -->

| Wording | Runs naming "cream" | Model-judged cells | item2 `info_accurate` misses |
|---|---|---|---|
| Baseline (Sep 11, 15 runs) | 9/15 | 149/150 | 1/15 |
| **A: name colours by hue (shipped)** | **11/45** | **448/450** | 1/45 |
| B: A plus "say 'peach', not 'cream'" | 2/45 | 440/450 | **10/45** |

**B won on the target measure and was rejected.** Its extra failures all
landed in a different check on a different image, which nobody was
watching, and pushed it below the floor set in advance. Compared with A, B
removed nine wrong colour words and added nine wrong pass/fail results.
That's a bad trade: a wrong verdict matters more than a wrong adjective.
**A shipped (Sep 14).**

**What this comparison turned out not to be.** It was presented as one
change apart, and checked that way: the system prompt and every field
description were compared byte for byte. But one channel was never
recorded: the output schema's class docstring. It changed between A and B
as well (decision 7). So B's rejection stands as recorded, but it was not a
clean comparison, and A's figures describe a version of the code that no
longer exists. On Sep 16 the audit's *other* line, the one that explains the
brand verdict, was recounted as well. It had named cream in 26 of 45 runs
under A and 5 under B, and no count had covered it.

### 7. Treat everything the model receives as the prompt, including the schema

**The failure.** The colour fix changed the audit tool, so under this
project's own rule M7 had to be certified again. The re-certification
failed badly: only 82 of 119 audit rows matched, and one clean image failed
its accuracy check in all 15 runs. The model's explanations repeated, almost
word for word, a sentence from this project's own notes about an earlier
failure.

**The cause.** The audit returns structured output defined by a Python
class. pydantic turns that class's docstring into the schema's description,
and the OpenAI SDK sends the schema with every call. By Sep 14 the docstring
had grown to 6,177 characters of design notes (Claude wrote them). Those
notes included the earlier failure sentence verbatim and wording B's
rejected clause. The model had been reading all of it on every audit call.
Claude traced the failure to the docstring, and Gerard confirmed the length
in his own environment.

**The test.** The test made one change: the same words were moved into code
comments, which are not sent to the model. The decision rule was written
down before either run. The clean image's accuracy check, 45 runs each:

| Run | What the model receives | Misses | Model-judged cells |
|---|---|---|---|
| Run 1 | 6,177-character schema description | **45/45** | 357/450 |
| Run 2 | no schema description | **0/45** | **449/450** |

The arithmetic legibility check was right in all 225 cells in both runs.
The difference on the primary measure has p = 1.9 × 10⁻²⁶, and Run 2's
449/450 was the best model-judged result the project had recorded. A
pre-registered repeat on Sep 16 matched it.

**Decision (Sep 15):** no docstring on any class that is sent as an output
schema. Every probe now saves the whole schema the model received, not a
hand-picked list of its parts.

*Why it matters:* notes written *about* a failure, placed where the model
could read them, *caused* that failure. And "checked byte for byte" only
covers the channels that were recorded, so the claim should name them.

## Where the certification stands

M7 is certified at commit `a915217`, the code as shipped. The pass ran on
Sep 15: 15 runs of each of the 8 items, with a clean working tree.

| Measure | Result |
|---|---|
| Runs completed | **120/120**, zero crashes, zero unmeasured |
| Text rows matching the key | **120/120** |
| Audit rows matching the key | **120/120** |
| Image checks on the five fixtures, model-judged | **150/150** |
| Image checks on the five fixtures, deterministic | 75/75 (arithmetic; cannot vary) |

**It took four attempts.** An earlier pass (Sep 11, `8c57001`) matched 118
of 120 text rows and 118 of 120 audit rows. The Sep 14 colour fix then
changed the audit tool, which reopens certification under this project's
own rule. The first re-certification failed, and decision 7 explains why.
After that fix, the next two attempts hung inside the Agent Service without
raising an error, which led to the hang guards in the operator notes. The
fourth attempt passed.

**What this pass could not show.** item6 passed its first draft in all 15
runs, so the redraft loop never had a draft to rescue. item7 went through
two redrafts in every run and ended failed each time, as its key expects. A
pass that matches every verdict also says nothing about the *wording* of the
audit's notes (see "Known limits").

## Known limits, stated plainly

- **The audit still names a colour that isn't in one image.** On item3,
  which is entirely orange, the line explaining the brand verdict says
  "cream" in 40 of 45 runs. A pre-registered repeat got 34 of 45 (95%
  interval 61–86%). The line describing the image says it in 0 and 1 of
  45. Some of those explanations only name the brand's "orange/cream
  family." Most describe the image's own tones as cream: 31 of 40 and 20
  of 34, by a rule written after the first run. The verdict is right every
  time. The wording is wrong, and the agent repeats it. Changing that
  wording would change what the model reads and would reopen
  certification, so it is logged, not done.
- **`info_accurate` has two rare failure modes, and they are opposites.**
  In one, the model's explanation reasons wrongly to a fail. In the other,
  the explanation reasons correctly to a pass and the true/false field says
  fail anyway. One wording change can't fix both. Neither appeared in the
  certifying pass.
- **The crash-handling path has run once against a real failure.** During
  the failed re-certification, an Azure `server_error` was recorded as an
  unmeasured run, and the pass carried on as designed. The hang guards have
  only been seen doing nothing: the certifying pass never triggered them,
  and their failure paths were tested only in isolation.
- **Agent runs and direct probe runs of the same audit code disagree on some
  rates.** This has happened twice, and no cause has been found. Each rate on
  this page comes from a direct probe run unless it says otherwise.
- **Runs can be made more consistent, but not repeatable.** Temperature is
  0, but the Agents SDK has no seed parameter.

## Lessons worth keeping

- **A 15-run test can't measure a rate, and its errors can flatter you.**
  At 15 runs, fix A looked nearly perfect and was reported as "essentially
  fixed." At 45 runs, the same wording on the same commit named the wrong
  colour in 11 of 45. The two results don't actually conflict: the 15-run
  result's 95% interval reached 30%. The mistake was reading the number and
  not the interval. A measurement that makes a fix look worse gets re-run.
  One that makes it look better gets written up. (This was Claude's analysis
  error, caught by the pre-registered bands.)
- **A tidy explanation makes a noisy result more convincing, not more
  true.** The same 15-run pass showed a regression, and an explanation for
  it was found at p = 0.001. At 45 runs, both disappeared.
- **Write down the pass/fail bands before you run the test, in the units
  the tool reports, and above its noise floor.** "Any regression" isn't a
  usable trigger. "The majority flips, or agreement falls below 0.8" is.
- **A branch-name URL isn't a fresh read.** A GitHub raw URL for `main`
  served a week-old file from an edge cache. Pinning the commit SHA or adding
  a cache-buster returned the current file.
- **Size runs from the smallest effect you must not miss, not from the time
  available.** Run times are now recorded, not remembered: 12–14 seconds
  per audit call, so a 45-run pass takes about 55 minutes.
- **Count every place the mistake can appear, not just the field you
  fixed.** The colour fix was scored on the line that describes the image.
  The word stayed in the line that explains the verdict, which is where the
  defect was first found. No count covered that line until Sep 16, and a
  pre-registered repeat confirmed it before this page said so.
- **Anything the model can read is part of the prompt.** Decision 7
  covers it: notes about a failure, placed in the schema, reproduced that
  failure.

## How this was built

Built with Claude (Anthropic) as a coding and analysis partner, with work
divided on purpose.

**Gerard** made the design decisions, often choosing among options Claude
laid out, and did all of the Azure and CLI work, including running every
command and every measurement. Recorded decisions and
work include: writing the image-audit prompts (Aug 28); drafting each round
of the `text_legible`, `info_accurate` and `brand_consistent` wording (Claude
critiqued each round); making `get_fact_sheet` a tool and writing the
redraft clause's key fix (Sep 7); choosing the paired design for the judge
test (Sep 9); making the audit's colour description a schema field instead
of a prompt sentence (Sep 11); overruling an overly strict abort rule
(Sep 11); running condition A before B and raising runs to 45 (Sep 14).
He also pushed back when a re-test was deferred without an estimate of its
cost, and that re-test is how the Sep 11 certification came to be run. On
Sep 15 and 16 he made these calls:
- to re-certify (about 95 minutes) rather than write this page around a
  stale result;
- to confirm each decision rule before its results existed;
- to approve the one-change docstring test and the hang guards;
- to measure the colour question again before writing about it.

**Claude** wrote the Python: the orchestrator, the tool wrappers, the probe
scripts, the provenance modules, the hang guards and the analysis scripts.
Claude drafted the agent instructions, whose second version regressed on
Claude's bugs, and did the results analysis and statistics. Claude also made
these errors:
- the two Sep 14 analysis errors described above;
- writing the schema-docstring notes that decision 7 removed, and missing
  them in a Sep 15 review;
- on Sep 15, giving a colour figure that counted only one line of the
  audit's notes.

Where the project log doesn't record who did something, this page doesn't
say. [CHECK: Gerard to confirm this framing before publishing]

## Evidence

| What | Where |
|---|---|
| Certification pass | `results/20260915-184006_orchestrator_stability.json` · `a915217` |
| Failed re-certification | `results/20260915-111227_orchestrator_stability.json` · `d46353d` |
| Docstring test, Run 1 (description sent) | `results/20260915-130108_fixture_stability.json` · `7c9c305` |
| Docstring test, Run 2 (no description) | `results/20260915-141917_fixture_stability.json` · `0dffc01` |
| Colour repeat, pre-registered | `results/20260916-102211_fixture_stability.json` · `c5dc05e` |
| Earlier certification (superseded) | `results/20260911-142437_orchestrator_stability.json` · `8c57001` |
| Condition A (wording shipped) | `results/20260914-134557_fixture_stability.json` · `9a3c605` |
| Condition B (rejected) | `results/20260914-150649_fixture_stability.json` · `dc66d5d` |
| Sep 11 baseline | `results/20260911-113242_fixture_stability.json` · `59f4ba3` |
| Colour recount, line by line | `scripts/analyze_absent_color_fragments.py` |
| Answer key | `content-items-plan.md` |
| Full session log | `STATUS.md` (Sep 2–16) |

Each results file listed here records its commit, whether the working tree
was clean, and the model deployments. The files from Sep 11 onward also
record the prompt text that actually ran. Those from the Sep 15 docstring
test onward also record the whole output schema that was sent to the model.
All of them are committed under `ai-103/scripts/results/`.
[CHECK: the repo is public, so a reader can open these]
