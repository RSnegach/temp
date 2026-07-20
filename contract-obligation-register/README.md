# Contract Obligation Register (deadline calendar from prose)

**Occupation:** Paralegals and Legal Assistants (O*NET 23-2011.00), Professional/Scientific/Technical Services

## Task

Read a Master Services Agreement, its Amendment No. 1, and Exhibit B, then build a 2025 deadline calendar: extract every dated obligation, resolve supersession and conditionals, compute each due date under the contract's own calendar-day and business-day rules, and list the dropped obligations with reasons.

## Analytical spine

Temporal reasoning over prose: date arithmetic (calendar vs business days against a holiday calendar), conditional inclusion, clause supersession, and a chained deadline measured off another obligation's due date. Distinct from the other portfolio spines. The golden uses live Excel date formulas.

## Files

| Path | What it is |
|------|------------|
| `inputs/MSA_and_Amendment.docx` | The MSA, Amendment No. 1, and Exhibit B (prose; facts embedded) |
| `golden/Obligation_Register.xlsx` | Golden register: live WORKDAY/date formulas, anchors + holidays tab, dropped-obligations tab |
| `scripts/contract.py` | Obligation set + date engine (source of truth) |
| `scripts/build_contract_doc.py` | Contract prose generator |
| `scripts/build_golden.py` | Golden register generator |
| `scripts/xlsx_live.py` | Live-formula cache injection (incl. date serials), normalization, fingerprint scrub |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomic rubric, metadata |

## Key figures (golden)

24 active dated rows. Amended non-renewal deadline 2025-08-21 (90 business days before Dec 31). Chained integration report 2025-03-17 (20 business days after the SOW sign-off due date). Security review included (data classification High); breach drill dropped (no personal data). Two dropped obligations.

## Why it is hard (a human 5 to 6 hour task)

Five traps: the amendment deletes and replaces a clause ("Section 7.2 is deleted in its entirety"); two obligations are conditional on facts buried in the exhibit (fee threshold, data classification); one obligation is dropped on a recital fact (no personal data); one deadline is chained to another obligation's due date; and the day-count rules mix calendar-day rolling with unrolled business-day counts across a holiday calendar.

Reproduce: `python scripts/contract.py` prints the register and the dropped obligations.
