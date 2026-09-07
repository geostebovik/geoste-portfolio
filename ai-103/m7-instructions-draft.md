# M7 orchestrator instructions — rationale

> **The wording itself is no longer here.** It lives in
> `scripts/m7_orchestrator.py` as `INSTRUCTIONS_V3` and that file is the only
> source of truth. A copy used to sit in this doc; on 2026-09-07 Gerard edited
> that copy twice, once with no effect at all, because it was not what runs.
> Two homes for one fact, which is the failure the Sep 6 `STATUS.md`
> restructure exists to prevent. Removed rather than re-synced.
>
> Version history: **V1** the deliberate throwaway (15/15 audit, no redraft
> path exercised). **V2** regressed to 12/15 — two bugs, both Claude's, both
> diagnosed in one read from the persisted run and both fixed in V3. **V3**
> adds the `get_fact_sheet` tool, corrects the `query` clause, and carries
> Gerard's substitute-don't-only-subtract fix to the redraft clause.

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
