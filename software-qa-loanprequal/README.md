# Software QA - LoanPreQual Test Suite Design

**Occupation:** Software Quality Assurance Analysts and Testers (O*NET 15-1253.00)

## Task

Derive a complete functional test suite for the LoanPreQual decision service.
An applicant record is validated field by field, then run through an ordered
7-rule decision engine (first match wins) that returns APPROVE_PRIME,
APPROVE_STANDARD, REFER, DECLINE, or REJECT.

## Analytical spine

Combinatorial test-case derivation across four techniques, from information
split over the input files (no single file yields the suite):

- **EP** equivalence partitioning, one representative per class per field
- **BVA** boundary value analysis, min-1 / min / max / max+1 per bounded field
- **DT** decision table, one first-match case per rule R1-R7
- **DB** decision-boundary analysis at and across each rule threshold
- **PATH** basis-path coverage of the decision-flow graph, V(G) = 8

## Files

| Path | What it is |
|------|------------|
| `inputs/LPQ-482_Feature_Specification.docx` | Behaviour, outcomes, acceptance criteria |
| `inputs/LPQ-482-RULES_Decision_Rules.xlsx` | Ordered 7-rule engine, thresholds, operators |
| `inputs/LPQ-482-VAL_Field_Validation_Reference.docx` | Field ranges, enums, validation order |
| `inputs/LPQ-482-FLOW_Decision_Flow_Graph.pdf` | Reference for the hand-drawn decision-flow graph |
| `golden/LPQ-482_Test_Suite.xlsx` | Golden suite: 63 cases + coverage + branch-coverage sheets |
| `scripts/suite.py` | Policy engine + case generator (source of truth) |
| `scripts/build_*.py` | Generators for the input and golden artifacts |
| `PROMPT_AND_RUBRIC.md` | Prompt, 12-criterion rubric, metadata |

## Key figures (golden)

63 test cases: 16 EP, 20 BVA, 7 DT, 12 DB, 8 PATH. Decision-flow graph has
7 decision nodes / 14 branches / V(G) = 8, all branches covered. Rule R5
(prime tier) decomposes into two sequential gates (score, then debt ratio).

Reproduce: `python scripts/suite.py` prints the case counts and full case list.
