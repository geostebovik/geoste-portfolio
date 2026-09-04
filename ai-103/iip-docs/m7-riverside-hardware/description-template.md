# Content Template — Riverside Hardware & Supply Video Descriptions

**Status:** template for IIP M7's orchestrator agent to draft against. Analogous
role to the `template/` library referenced in `agent-system-project-plan.md`, but
scoped down to exactly what M7 needs — one content type, not a general-purpose
library.

The agent drafts a **title** and **description** for each content item using this
structure, grounded in `fact-sheet.md`. The evaluator harness (M6 pattern) then
checks the draft against the fact sheet for groundedness before it's treated as
final.

---

## Title format

`[Benefit or topic, plain language] — Riverside Hardware & Supply`

Short, specific, no clickbait. States what the viewer will get from the video.

**Example shape:** "How to Mix Exterior Paint Colors at Home — Riverside Hardware & Supply"

## Description format

Three parts, in order:

1. **Hook (1 sentence).** States the problem or question the video answers.
2. **Body (2–3 sentences).** What's covered, in plain terms. Any factual claim
   here (hours, services, pricing, availability) must be traceable to
   `fact-sheet.md` — this is exactly what the groundedness check validates.
3. **CTA (1 line).** Store name, hours, and either the phone number or "stop by"
   — pulled directly from the fact sheet's Contact/Hours sections, never
   invented or assumed.

**Example (clean, no planted errors):**

> Ever stood in the paint aisle unsure which exterior color will actually hold up
> outside? In this quick video we show you how we custom-mix exterior paint right
> in store. We walk through the whole process, start to finish. Stop by Riverside
> Hardware & Supply, Monday–Saturday 8am–6pm.

## Tone rules (from the fact sheet's Brand Guide)

- Friendly and practical, not corporate.
- No superlatives without a concrete backing fact ("best" / "biggest" are out
  unless the fact sheet says so — it doesn't).
- No hours, contact info, or service claims that aren't in `fact-sheet.md`.
