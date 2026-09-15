# M7 — An Azure AI Foundry agent that checks its own work

<!--
DRAFT, NOT FOR PUBLICATION. Written 2026-09-15.
Held until Phase 2 is ready to go up with it (Gerard's call, Sep 14).
/ai-103/* returns 404 on ostebovik.net (staticwebapp.config.json), so pushing
this file does not publish it.

WHO WROTE THIS DRAFT: Claude drafted all of the prose on Sep 15 from
m7-orientation.md, STATUS.md (Sep 2–14 entries), the commit log, and the
results JSON. Gerard chose the format, scope, audience and authorship
arrangement, and is the editor. Record his edits and decisions inline as he
makes them.

FIGURE RULES (from STATUS.md "Current next action"):
- brand_consistent is 0.600 -> 0.244: an improvement, NOT a fix.
- Never quote 1/15.
- Never combine judged and deterministic counts into one figure.

OPEN BEFORE PUBLISHING: the 120-run certification is at 8c57001. The
condition-A wording that shipped Sep 14 changed m7_cv_audit_tool.py after
that commit. Update "Where the certification stands" once a full
orchestrator pass has run at current HEAD, or keep that section as written.

VERIFIED Sep 15 against the results JSON: 120 rows, 0 errors, 0 unmeasured;
text 118/120 (both item6); audit 118/120 (item2 run 8 and item3 run 1, both
info_accurate). 148/150 is the five-fixture subset. Items 6-8 reuse item1's
thumbnail, and all 8 items together are 238/240 model-judged and 120/120
deterministic. p-values and Wilson intervals recomputed and match.

[CHECK] marks a claim Gerard should confirm before publishing.

GERARD'S REVIEW, Sep 15: he read "In short" and kept it as written. He
judged it longer than ideal, but found that each point says something
significant and leads into the next section. He plans to ask a few people
for an outside read before publishing.
-->

## In short

- **What it is:** a single Azure AI Foundry agent that drafts marketing copy
  for a fictional hardware store. It checks each draft against the store's
  fact sheet, then audits the thumbnail image for legibility, brand colours
  and factual accuracy. It is the seventh and final milestone of the IIP lab
  build for AI-103.
- **What it proves:** the agent does what it was designed to do, measured
  against a written answer key. In the certified pass it
  completed **120 of 120 runs with zero crashes**, and **118 of 120 audit
  rows** matched the key.
- **What it does not do yet:** about **a quarter** of runs on one test image
  still name a colour that isn't in the image, and the agent repeats that
  mistake in its output. The rate fell from 60% to 24%. That is an
  improvement, not a fix, and this page says so.
- **What it's really about:** deciding what to trust. Most of the work on
  this milestone went into finding out when a result could be believed,
  including twice when a good-looking number turned out to be wrong.

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

**Two operator notes from the build:**

- **Azure AI region support is per feature, not per service.** Image
  Analysis 4.0 is available in West US, but its captioning feature is not.
  "The service is in my region" and "the feature I need is in my region" are
  different claims, so check the one you actually depend on.
- **The agent needs the project endpoint, not the account endpoint.** The
  CLI's `properties.endpoints` only lists account-level endpoints. The
  project endpoint comes from the portal's project Overview.

## Six decisions worth showing

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

### 6. Ship the lower-scoring fix, because the better score broke another check

The last visible defect: on the flawed "tool rental" thumbnail, which is
entirely orange, the audit often described the colours using the brand
colour "cream." The model sees the image correctly and picks the wrong word:
the image's colours are pale, and "cream" is the only light colour named in
the brand guide.

Two wordings were tested, with one change between them, 45 runs each, and
pass/fail bands written into the commit messages before any results
existed:

<!-- The last column's "1/15" is item2's info_accurate baseline, NOT the banned
condition-A colour figure. Same digits, different measurement. -->

| Wording | Runs naming "cream" | Model-judged cells | item2 `info_accurate` misses |
|---|---|---|---|
| Baseline (Sep 11, 15 runs) | 9/15 = 0.60 | 149/150 | 1/15 |
| **A: name colours by hue (shipped)** | **11/45 = 0.24** | **448/450** | 1/45 |
| B: A plus "say 'peach', not 'cream'" | 2/45 = 0.04 | 440/450 | **10/45** |

**B won on the target measure and was rejected.** Its ten extra failures all
landed in a different check on a different image, which nobody was
watching, and pushed it below the floor set in advance. Compared with A,
B removed nine wrong colour words and added nine wrong pass/fail results.
That's a bad trade: a wrong verdict matters more than a wrong adjective.
**A shipped (Sep 14).** Against the
baseline, the drop is statistically significant (p = 0.024), and no other
check regressed.

## Where the certification stands

The full certification pass ran on Sep 11 at commit `8c57001`, 15 runs of
each of the 8 items, with a clean working tree:

| Measure | Result |
|---|---|
| Runs completed | **120/120**, zero crashes, zero unmeasured |
| Text rows matching the key | **118/120**. Both misses are item6, where the agent correctly caught an unsupported claim and fixed it. The behaviour was right; the key expected a different path. |
| Audit rows matching the key | **118/120**. Both misses are one known, rare failure in `info_accurate` |
| Image checks on the five fixtures, model-judged | **148/150** |
| Image checks on the five fixtures, deterministic | 75/75 (arithmetic; cannot vary) |

**The Sep 14 colour fix came after that commit.** It was measured on its
own (the table in decision 6), but not yet in a full agent pass. The agent
repeats the audit's notes word for word, so the fix changes what the agent
reads. This project's own rule is that a change like that reopens
certification. [UPDATE once the pass at current HEAD has run.]

## Known limits, stated plainly

- **About one run in four on item3 still names a colour that isn't in the
  image,** and the agent repeats it in its summary. The likely range is
  14–39% (95% interval). This is an improvement, not a fix.
- **`info_accurate` has two rare failure modes, and they are opposites.**
  In one, the model's explanation reasons wrongly to a fail. In the other,
  the explanation reasons correctly to a pass and the true/false field says
  fail anyway. One wording change can't fix both.
- **The crash-handling path has never run against a real crash.** A clean
  pass doesn't test it.
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
cost, and that re-test is how the Sep 11 certification came to be run.

**Claude** wrote the Python, including the orchestrator, the tool wrappers,
the probe scripts and the provenance module. Claude drafted the agent
instructions, whose second version regressed on Claude's bugs, and did the
results analysis and statistics. Claude made the two Sep 14 analysis errors
described above.

Where the project log doesn't record who did something, this page doesn't
say. [CHECK: Gerard to confirm this framing before publishing]

## Evidence

| What | Where |
|---|---|
| Certification pass | `results/20260911-142437_orchestrator_stability.json` · `8c57001` |
| Condition A (shipped) | `results/20260914-134557_fixture_stability.json` · `9a3c605` |
| Condition B (rejected) | `results/20260914-150649_fixture_stability.json` · `dc66d5d` |
| Sep 11 baseline | `results/20260911-113242_fixture_stability.json` · `59f4ba3` |
| Answer key | `content-items-plan.md` |
| Full session log | `STATUS.md` (Sep 2–14) |

Each results file listed here records its commit, whether the working tree
was clean, and the model deployments. The files from Sep 11 onward also
record the prompt text that actually ran. All of them are committed under
`ai-103/scripts/results/`.
[CHECK: the repo is public, so a reader can open these]
