# Month-End Close and Reconciliation (Meridian) - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

I need June closed for Meridian Technical Services. The raw ledger is in `General_Ledger_June.xlsx`: the "General Ledger" tab has the opening balances and every journal line for the month, so foot it to get the unadjusted trial balance yourself. The supporting schedules and the bank statement are on the other two tabs.

It does not tie out as it sits, so first find why. Compare the ledger to the supporting records: a difference between the ledger and a schedule that is divisible by 9 is a transposition and gets fixed by restating the ledger figure to the schedule, not by a journal entry. Watch for a couple of traps. There is an inventory count that differs from the ledger, but that difference is not the out-of-balance and is not a transposition, so leave it alone unless it is authorized; note it and move on. And June rent is already posted in the ledger, so do not accrue it again; the only rent adjustment is the reclass of a supplies purchase that was miscoded to rent.

Then post the normal month-end adjustments the schedules call for (prepaid insurance, depreciation, accrued wages, unearned revenue earned), plus the book-side bank items that are not yet recorded (the service fee and the returned NSF check), and remember the deposit in transit and outstanding checks are reconciling items only, not entries. Every journal entry has to balance.

Hand it back as `Adjusted_Trial_Balance.xlsx`: the adjusting entries, the adjusted trial balance with debits equal to credits, a bank reconciliation showing adjusted bank equals adjusted book cash, and adjusted net income. Compute the adjusted balances, totals, the balance check, and net income as live formulas off the unadjusted figures and the adjustments so it recomputes if a number changes.

---

## RUBRIC (weights in the numeric field only)

Each criterion is one atomic check. Derived values state their basis.

Find the imbalance and correct it the right way:
**+4** The unadjusted trial balance is out of balance by 2,700, identified as the Accounts Receivable transposition (ledger 148,500 vs aging 145,800; 2,700 is divisible by 9).
**+3** The transposition is fixed by restating AR to the 145,800 aging total, NOT by a balancing journal entry.
**-4** A journal entry is written to "correct" the transposition (which cannot fix a one-sided out-of-balance), or the books are forced to balance by plugging an unrelated account.

Do not act on the distractors:
**+4** The inventory count variance (ledger 96,500 vs count 95,250 = 1,250) is left unbooked; it is noted as not divisible by 9 and under review, and is not the cause of the imbalance.
**+3** June rent is not accrued again; the only rent adjustment is the reclass of the 6,000 supplies purchase miscoded to Rent Expense.
**-4** The inventory variance is written down (moving inventory to 95,250), or June rent is accrued a second time, either of which mis-states the adjusted balances.

Adjusting journal entries (each balances):
**+2** Prepaid insurance expense of 6,000 (18,000 times 4 of 12 months) is debited to Insurance Expense and credited to Prepaid Insurance.
**+2** Depreciation of 2,000 (24,000 / 12) is debited to Depreciation Expense and credited to Accumulated Depreciation.
**+2** Accrued wages of 7,600 are debited to Wages Expense and credited to Wages Payable.
**+2** Unearned revenue of 12,000 now earned is debited to Unearned Revenue and credited to Service Revenue.
**+2** The bank service fee of 400 and the NSF check of 1,900 are each booked as entries reducing Cash; the deposit in transit and outstanding checks are not booked.
**-2** A deposit in transit or an outstanding check is booked as a journal entry.

Adjusted trial balance, bank rec, net income:
**+4** The adjusted trial balance balances with total debits equal to total credits at 934,000.
**+3** The bank reconciliation ties: adjusted bank balance (90,100 + 8,000 - 12,300 = 85,800) equals adjusted book cash (88,100 - 400 - 1,900 = 85,800), and equals the Cash line on the adjusted trial balance.
**+2** Adjusted net income is 55,000 (revenue 407,000 less expenses 352,000).
**+2** The adjusted balances, totals, balance check, and net income are live formulas off the unadjusted figures and adjustments, not typed-in values.

---

## Golden scores 100 against this rubric
The golden `Adjusted_Trial_Balance.xlsx` foots the ledger, identifies the 2,700 AR transposition and restates AR to the aging total without a journal entry, leaves the 1,250 inventory variance and the already-posted June rent alone, posts the four accruals plus the bank fee and NSF check, ties the adjusted trial balance at 934,000 debits equal credits, reconciles cash to 85,800 both sides, and reports net income of 55,000, all as live formulas.

## Metadata
- O*NET occupation: Accountants and Auditors (13-2011.00)
- O*NET tasks (verbatim from O*NET):
  - Prepare adjusting journal entries.
  - Analyze business operations, trends, costs, revenues, financial commitments, and obligations to project future revenues and expenses or to provide advice.
  - Report to management regarding the finances of establishments.
  - Inspect account books and accounting systems for efficiency, effectiveness, and use of accepted accounting procedures to record transactions.
- O*NET skills (Skills section): Mathematics, Critical Thinking, Reading Comprehension, Active Learning.
- Web search allowed: No (self-contained in the ledger workbook).
- Multimodal: No (spreadsheet inputs).
- Time estimate: 6 hours by hand (foot the ledger, diagnose the transposition, separate the distractors from the real adjustments, post seven entries, build the adjusted trial balance and bank reconciliation, and wire the workbook with live formulas).
