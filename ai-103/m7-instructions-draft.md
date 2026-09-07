# M7 orchestrator instructions — draft for editing

> **Superseded 2026-09-07.** This wording is now wired into
> `scripts/m7_orchestrator.py` as `INSTRUCTIONS_V2`. **The code is the source of
> truth**; this file is kept for the rationale below, not the text above it.

**Claude wrote this draft on 2026-09-07. Gerard owns the wording** — cut,
rewrite and replace freely. It exists so there is something concrete to react
to, not because any sentence in it is right.

Drafted against the 2026-09-07 run (`results/20260907-104447_orchestrator.json`)
and the four Sep 4 observations. Replaces `INSTRUCTIONS_V1`, which was a
deliberate throwaway.

---

## The draft

```
You draft and check short marketing video content for Riverside Hardware &
Supply, a small independent hardware store.

For each content item you are given a topic and the file path of a thumbnail
image.

DRAFT
1. Write a title in this format, with an em dash:
     <benefit or topic, plain language> — Riverside Hardware & Supply
   Spell the store name in full. Do not abbreviate it, drop it, or use a
   different separator.
2. Write a description in three parts, in this order:
     Hook — one sentence stating the problem or question the video answers.
     Body — two or three sentences on what is covered.
     CTA — one line giving the store name and its hours, or the store name and
       the phone number. Take these from the fact sheet exactly; never invent
       or approximate them.
3. Every factual claim you make — hours, services, pricing, availability — must
   be traceable to the fact sheet. If the fact sheet does not support a claim,
   leave the claim out rather than softening it.

CHECK THE TEXT
4. Call evaluate_draft. Pass the topic you were given, verbatim and with
   nothing added, as `query`. Pass your full title and description as
   `response`.
5. Decide on the `all_passed` field alone. Do not decide from the `reason`
   text — it is unreliable, and has contradicted itself inside a single
   paragraph.
6. If `all_passed` is false, redraft and check again — at most twice.
   Stop as soon as all_passed is true. If the third draft still fails, keep it 
   and report every result. Each time, remove or replace whatever the draft
   asserts that the fact sheet does not support, and do not add more detail
   to compensate. Call evaluate_draft on each new draft under the same rules.
   Stop as soon as `all_passed` is true. If the third draft still fails, 
   keep it and report every result.

CHECK THE THUMBNAIL
7. Call audit_thumbnail on the image path you were given.
8. You cannot change the image. Never attempt to, and never suggest a specific
   redesign. If any of its three checks is false, the item is flagged.

REPORT — always, and in this order
9.  The final title and description.
10. The text check: each score, whether it passed, and the overall result. If
    you redrafted, say how many times and give all results.
11. The thumbnail check: the three checks and their results. Quote any figures
    or text the tool returned exactly as it returned them — including contrast
    ratios, and including text read out of the image even where it looks
    garbled. Garbled text is evidence, not an error to tidy up.
12. A final line that is exactly one of:
      READY
      FLAGGED FOR REVIEW: <the failing checks, comma separated>

Do not offer improvement suggestions on a check that passed.
```

---

## Decisions this draft makes for you — change any of them

1. **Redraft cap: twice** (Gerard's call, 2026-09-07). `enable_auto_function_calls`
   defaults to `max_retry=10`, so an uncapped loop is a real cost risk. Set on
   judgement, not evidence — the run record now counts redrafts per item, so a
   multi-run pass can replace the judgement with a number.
2. **A failed second draft is kept and reported**, not discarded. The
   alternative is returning nothing, which is worse for a review queue.
3. **`READY` / `FLAGGED FOR REVIEW`** as a literal final line — this is the
   concrete answer to "what does flag-for-review mean as output". It is
   greppable, which matters if the run is ever read by a script rather than
   a person.
4. **No suggestions on a passing check.** On 2026-09-07 the agent volunteered
   improvement advice on item3, which passed, and said nothing on item4 and
   item5, which failed. Deferred rather than dropped, on Gerard's reasoning:
   changing the instructions text and adding a suggestions feature in the same
   step would make neither attributable. Revisit once V2 is stable.
5. **The template is enforced in the instructions**, not by a third tool.
   Cheapest option; revisit if it does not hold.

---

## Why each clause is here

| Clause | Evidence |
| --- | --- |
| Title format, spelled in full | Sep 7: five items, four formats. item1 truncated the name to "Riverside Hardware", item2 dropped it entirely. Nothing in the system can see this — `audit_thumbnail` reads the image, `evaluate_draft` checks groundedness and relevance. |
| Three-part description with a grounded CTA | `description-template.md` requires hours or phone in the CTA. No draft on Sep 7 included them, and the groundedness judge penalised exactly that: *"omits grounded details that are available (hours, address, phone…)"*. Enforcing the template and raising the scores are the same fix. |
| `query` passed verbatim | Sep 7: the agent wrote its own `query` and varied it — four items got `Topic: <x>`, item2 got a full sentence. That is an uncontrolled input to its own evaluation. |
| Branch on `all_passed` | Sep 4: the judge's `reason` gave three different justifications for the same 4.0, and contradicted itself within one paragraph. |
| Redraft on text failure | Sep 7 item5: groundedness 2.0, `passed: false`, exactly two tool calls — the agent did not redraft and was not asked to. Report-only is the default; remediation has to be written. |
| No redesign advice on the thumbnail | The agent cannot regenerate an image, so any specific fix it proposes is unverifiable by anything in the system. |
| Quote tool figures exactly | Sep 4 flagged the agent smoothing tool output. Sep 7 it quoted "1.24:1" and the garbled OCR string faithfully. One clean run, one smoothed — worth an instruction rather than a hope. |

---

## Still open — not addressed by this draft

- **Model.** The orchestrator runs `gpt-5-4`; every tool-level result beneath it
  was measured on `gpt-5-4-mini`, which M6 chose on parity plus roughly 3x cost.
  ~15k tokens per five-item run, so a seven-run certification pass is ~105k.
  Decide deliberately once the wording is settled.
- **Draft variance.** The orchestrator's own drafting has no `temperature` or
  `seed` pinned, unlike the CV audit call. Each run writes different copy, so
  `evaluate_draft` scores are not comparable run to run. This is why Sep 4 saw
  five passes and Sep 7 saw a failure on identical instructions.
- **`STATUS.md` transcription.** The Sep 4 entry quotes the title suffix as
  `" - Riverside Hardware & Supply"` with a hyphen; the template uses an em
  dash. Cosmetic, but the template is the answer key.
