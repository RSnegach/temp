# Month-End Close and Reconciliation (double-entry over volume)

**Occupation:** Accountants and Auditors (O*NET 13-2011.00), Professional/Scientific/Technical Services

## Task

Close the month for a services firm from a raw general ledger. Foot the ledger to an unadjusted trial balance, diagnose why it does not balance, correct the transposition, post the month-end adjusting entries, reconcile the bank, and produce an adjusted trial balance, a bank reconciliation, and adjusted net income.

## Analytical spine

Double-entry constraint over transaction volume: footing, error diagnosis (transposition vs unrelated variance), the distinction between a restatement, a journal entry, and a bank-reconciliation item, and the balancing identity. Distinct from the other portfolio spines. The golden uses live formulas throughout.

## Files

| Path | What it is |
|------|------------|
| `inputs/General_Ledger_June.xlsx` | Raw GL detail (opening + month lines to foot), subledgers, bank statement |
| `golden/Adjusted_Trial_Balance.xlsx` | Golden close: adjusting entries, adjusted TB, bank rec, net income (live formulas) |
| `scripts/accounting.py` | Chart of accounts, unadjusted balances, adjustments engine (source of truth) |
| `scripts/accounting_hard.py` | Raw-GL construction that foots to the unadjusted TB; trap definitions |
| `scripts/build_gl.py`, `build_golden.py` | Input and golden generators |
| `scripts/xlsx_live.py` | Live-formula cache injection, normalization, fingerprint scrub |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomic rubric, metadata |

## Key figures (golden)

Unadjusted out of balance by 2,700 (AR transposition, divisible by 9). Seven adjusting entries. Adjusted trial balance 934,000 debits equal credits. Bank rec ties at 85,800. Net income 55,000.

## Why it is hard (a human 6 hour task)

Volume plus three discrimination traps: the 2,700 imbalance is a transposition fixed by restatement, not a journal entry (a balancing entry cannot cure a one-sided imbalance); the inventory count variance of 1,250 is a distractor (not divisible by 9, under review) that must be left alone; and June rent is already posted, so re-accruing it double-counts. The deposit in transit and outstanding checks are reconciling items, not entries.

Reproduce: `python scripts/accounting.py` prints the entries and the adjusted trial balance; `python scripts/accounting_hard.py` shows the raw GL footing to the unadjusted TB.
