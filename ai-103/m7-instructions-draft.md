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
> Gerard's substitute-don't-only-subtract fix to the redraft clause. **V4**
> (2026-09-09) closes the meta-commentary defect — see below.
>
> **A version is never edited in place.** On 2026-09-09 the V4 clauses were
> first applied to the V3 string itself, with `ACTIVE_INSTRUCTIONS_LABEL` still
> reading V3. Caught by an mtime check before any commit. Every result on record
> is labelled with the version it ran under, so editing a version relabels
> history: the Sep 7 and Sep 8 runs would have pointed at wording that did not
> exist when they ran, and the next run would have recorded `V3` while executing
> V4. V4 is therefore built as `INSTRUCTIONS_V3.replace(...)` with three asserts
> that fail at import if either substitution stops matching — a retyped 40-line
> string is an unverifiable diff.

---

## Decisions this draft makes for you — change any of them

1. **Redraft cap: twice** (Gerard's call, 2026-09-07). `enable_auto_function_calls`
   defaults to `max_retry=10`, so an uncapped loop is a real cost risk. Set on
   judgement, not evidence. ~~A multi-run pass can replace the judgement with a
   number.~~ — **that plan is void as of 2026-09-09, and the correct direction
   inverted.** The redraft loop re-rolls: a fixed failing draft passes 7 of 10
   re-reads unchanged, so the cap is a dice count. At 70% per read, one read
   passes 70%, a cap of 1 gives 91%, a cap of 2 gives 97.3% — **a higher cap
   raises the false-pass rate**, and a multi-run pass would have measured the cap
   rather than justified it. Whatever the cap should be, it is not a number the
   certification run can hand you.
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

## V4 (2026-09-09) — two clauses, one defect

**Gerard's wording, both clauses.** Claude specified what each had to accomplish,
critiqued two drafts of clause 7, and built the version block; Gerard wrote the
sentences and made the placement call.

**The defect.** Every redraft on record put the grounding document into
customer-facing copy — *"sticks to the details confirmed in the fact sheet"*,
*"as presented in the store fact sheet"*, *"questions about store policies not
listed there"*. Marketing copy talking to a customer about an internal document.
`check_meta_commentary.py`, run retroactively over both Sep 8 results files,
measured it at **5 of 5 redrafts and 2 of 21 first drafts** — the first-draft
number had never been checked, and both of those PASSED with zero redrafts and
would have shipped.

**Clause 4 — the prohibition, and why it is in the DRAFT section.**

> Do not ever mention the fact sheet, the instructions or the drafting process.
> The reader is the customer and has no need to know about the internal process.

It carries both a prohibition and the principle behind it, so a novel evasion
("as documented internally") still falls under "the drafting process". **It sits
in clause 4 rather than clause 7 because of those 2 first drafts:** a fix confined
to the redraft clause would have left them uncaught while appearing to work.
*Known risk, not yet needed:* clause 4's subject is factual claims and this
sentence is about audience, so it may be competing for salience inside a clause
about something else. If the detector ever shows hits again, promoting it to its
own numbered clause is the next lever — one variable, and testable.

**Clause 7 — the legal move, and why a prohibition alone would have failed.**

> If the fact sheet does not support a claim, leave it out. Do not compensate by
> writing vaguely or making unsupported claims. Instead, use the valid details
> available to draft the best-supportable copy possible and allow the check to
> fail.

V3's clause 7 offered exactly two moves: *remove* unsupported claims, *replace*
them with supported ones. On a topic the fact sheet cannot support, remove empties
the copy — V2 measured where that lands, relevance 4.0 → 2.0 for being
uninformative — and replace has no material. **The meta-commentary was the agent
inventing a third move because the instructions gave it none.** Claude rejected
Gerard's first clause-7 draft on exactly this: it added three more prohibitions
and no legal move, which would have rebuilt V2's trap with one more wall. The
final sentence names the right path instead of blocking one more wrong one —
this project's own standing lesson ("define the condition that produces the
verdict, rather than enumerating what shouldn't cause it") applied to instructions
rather than to a judge prompt. Clause 12's `FLAGGED FOR REVIEW` already existed to
carry a failure; the agent needed permission to use it, not another way to win.

**Pre-registered risk, recorded in the source before the run.** "Allow the check
to fail" sits before "call evaluate_draft on each new draft", so it could be read
as permission to stop after draft 1 — which would show as `redrafts` dropping to 0
on item7, where V3 recorded 2. Predicted not to happen. **It did not:** item7
recorded `redrafts=2` on 26 of 30 runs, and the four zeros are runs whose first
draft passed.

**Result, 30 runs of item6 and item7, 113 drafts.**

| | V3 baseline | V4 | Fisher two-sided |
|---|---|---|---|
| redrafts referencing the fact sheet | 5/5 | **0/53** | p = 2.2e-07 |
| first drafts referencing the fact sheet | 2/21 | **0/60** | p = 0.065 |

The redraft channel is settled. The first-draft channel is suggestive and not
significant — the baseline is only two events, and reaching p<0.05 needs about 50
runs, deliberately not spent. And the detector is a phrase matcher: a future clean
run should still be sampled by eye.

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
