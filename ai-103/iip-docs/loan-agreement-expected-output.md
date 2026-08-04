# Expected Output — Loan Agreement (Promissory Note)

**Sample document set:** `Loan_Agreement_Promissory_Note.pdf` (clean) /
`scan_Loan_Agreement_Promissory_Note.pdf` (flatbed scan) / angled phone photo (pending)

**Scope note:** This record covers **Page 1**, since that's the only page common to
all three image-quality conditions (the angled photo is single-page by design — see
session notes). Page 2 is boilerplate (waivers, severability, notices, signature
blocks) and contributes no distinct entities — covered briefly at the bottom for
completeness, but only the clean/scanned conditions will exercise it.

All content below is synthetic — fictional parties, fictional figures — for IIP
Phase 1 testing purposes.

---

## Document Type / Topic

A two-party personal loan agreement (promissory note) — unsecured, fixed-rate,
fixed-term — between an individual Borrower and an individual Lender. Governed by
Arizona law.

## Expected OCR Accuracy

Clean PDF and flatbed scan: should both extract at or near 100% character accuracy —
this is typed, well-formatted text with no handwriting, watermarks, or unusual fonts.
Any discrepancy here is a real finding, not an artifact of document quality.

Angled photo: expect minor degradation — possible character substitution errors,
especially in dollar figures or section numbering, due to perspective skew and
lighting. This is the actual point of including this condition.

## Expected Key Phrases

- Loan Agreement
- Borrower / Lender
- $50,000.00 (Borrowed Money / principal)
- 11.25 percent per annum (interest rate)
- Due Date
- monthly installments
- late payment fee
- unsecured loan
- acceleration
- attorneys' fees and costs

## Expected Entities

| Type | Value |
|---|---|
| Person | Harry Sample (Borrower) |
| Person | Scrooge McDuck (Lender) |
| Location | 321 Central Ave, Phoenix, Arizona, 85012 |
| Location | 982 W Treasure Trl, Apache Junction, Arizona, 85120 |
| Date | July 1, 2026 (agreement date / first payment date) |
| Date | June 30, 2031 (Due Date — full balance) |
| Quantity | $50,000.00 (principal) |
| Quantity | 11.25% (annual interest rate) |
| Quantity | $958.12 (monthly payment) |
| Quantity | $50.00 (late fee) |
| Quantity | 72 (loan term, months) |

No organization entities expected — both parties are named as individuals, no
companies or institutions appear on page 1.

## Expected Sentiment

**Neutral.** This is procedural/legal financial language with no emotionally
charged content. If Language returns anything other than neutral (or a low-confidence
mixed/neutral split), that's worth investigating as a possible false positive —
this is a useful sentiment-analysis calibration check precisely because the
correct answer is so unambiguous.

## Expected Summary (written before running anything)

> This is a $50,000 unsecured personal loan agreement between Harry Sample
> (Borrower) and Scrooge McDuck (Lender), dated July 1, 2026, governed by Arizona
> law. The loan carries an 11.25% annual interest rate, repaid in 72 monthly
> installments of $958.12 beginning July 1, 2026, with the full balance due by
> June 30, 2031. Standard provisions cover late fees, default acceleration, and
> attorney's fee recovery for the prevailing party in a dispute.

## Sample Q&A Pairs

| Question | Correct Answer |
|---|---|
| Who is the borrower? | Harry Sample |
| Who is the lender? | Scrooge McDuck |
| What is the loan amount? | $50,000.00 |
| What is the interest rate? | 11.25% per annum |
| What is the monthly payment amount? | $958.12 |
| Is the loan secured or unsecured? | Unsecured |
| What is the late fee for a missed payment? | $50.00 |
| What state's law governs this agreement? | Arizona |
| When is the full balance due? | June 30, 2031 |
| How many monthly payments are there? | 72 |

---

## Page 2 (Clean / Scanned conditions only — bonus coverage)

No new named entities, aside from a repeated reference to **Arizona** as the
governing law jurisdiction (Section XV) — this is the correct page for that
clause. Key phrases worth checking for: waiver of presentment, non-waiver,
severability, integration, conflicting terms, notice, execution, co-signer,
governing law. Expected sentiment: neutral. No summary/Q&A rubric needed —
page 2 is pure boilerplate and not a meaningful test of extraction quality on
its own.
