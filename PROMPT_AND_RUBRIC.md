# LoanPreQual Test Suite - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

We're picking up test design for the LoanPreQual decision service ahead of the Release 2.4 hardening sprint, and I need a full functional test suite built out before the dev drop lands Thursday. This is the pre-qual call that the online app and the branch tool both hit, so it has to be solid.

Everything you need is in the four files: the feature spec (`LPQ-482_Feature_Specification.docx`), the decision rules workbook (`LPQ-482-RULES_Decision_Rules.xlsx`), the field validation reference (`LPQ-482-VAL_Field_Validation_Reference.docx`), and my decision-flow sketch of the rule engine (`LPQ-482-FLOW_Decision_Flow.png` -- the path map I drew on the whiteboard). The spec tells you how the service behaves and the order it does things in; the validation reference has the field limits; the rules workbook has the decision logic and, importantly, the evaluation order and the exact operators at each threshold. Read the operator notes carefully, a couple of them are strict and a couple are inclusive and it changes the answer at the boundary. The flow sketch lays the engine out as branch points, and note the prime rule splits into two gates on it (a score gate then a debt gate) even though the rules table shows it as one line, so treat those as separate branches to cover.

I want proper coverage, not just happy path. Exercise the equivalence classes for every field, the boundaries on every field that has a range, and the decision rules including the ordering, so a record that could trip more than one rule lands on the right one. Boundaries on the decision thresholds matter as much as the field-validation boundaries. Work the flow sketch too: cover both the true and false exit of every branch point, and give me a set of cases that walks the independent paths through the graph. Keep each case focused on one thing by holding the rest of the record steady, and make sure the expected result is what the service would actually return, remembering a bad field is a rejection and not a decline.

Give it back to me as `LPQ-482_Test_Suite.xlsx` with one row per test case: an ID, which technique it's from, what it's targeting, the full applicant record for that case, and the expected result. Add a coverage summary so I can see at a glance that every field and every rule is covered when I walk the leads through it.

---

## RUBRIC (weights in the numeric field only)

**+5 (critical)** — The suite includes a decision-table case for every one of the seven rules R1-R7, each with the correct first-match outcome: R1 DECLINE (unemployed), R2 DECLINE (score below 620), R3 DECLINE (DTI above 43.0), R4 DECLINE (loan over 5x income), R5 APPROVE_PRIME, R6 APPROVE_STANDARD, R7 REFER. Correct check: 7 rule cases, each outcome as listed.

**+5 (critical)** — Rule-ordering / first-match is respected: any case that satisfies more than one rule condition shows the earlier rule's outcome (e.g. an unemployed applicant with a low score returns DECLINE "no qualifying income source" from R1, not the score reason). Correct check: no case reports a later rule when an earlier condition is also true.

**+4 (critical)** — Decision-threshold boundary cases are present and correct for the strict-vs-inclusive operators: score 619 DECLINE vs 620 REFER (R2 strict <); DTI 43.0 allowed vs 43.1 DECLINE (R3 strict >); loan exactly 5x income allowed vs just over 5x DECLINE (R4 strict >); score 719 vs 720 for prime (R5 inclusive >=); DTI 36.0 allowed vs 36.1 not prime (R5 inclusive <=); score 659 REFER vs 660 APPROVE_STANDARD (R6 inclusive >=). Correct check: each threshold tested at and across the boundary with the right outcome.

**+4 (critical)** — Boundary value analysis covers all five bounded numeric fields at min-1, min, max, max+1: applicant_age (17/18/75/76), annual_income (-1/0/1000000/1000001), credit_score (299/300/850/851), loan_amount (999/1000/500000/500001), existing_debt_ratio (-0.1/0.0/60.0/60.1). Correct check: 20 BVA cases, invalid limits return REJECT naming that field.

**+3 (important)** — Equivalence partitioning covers each field's valid class and each enumerated field's members plus an invalid member: employment_status (4 members + 1 invalid), loan_term_months (5 members + 1 invalid), and a valid representative for each numeric field. Correct check: 16 EP cases.

**+3 (important)** — Validation-versus-decision distinction is correct throughout: an out-of-range field returns REJECT (naming the first failing field), never DECLINE; a DECLINE only appears on a fully valid record. Correct check: every REJECT row has an out-of-range or invalid-enum field; no REJECT row is a valid record.

**+3 (important)** — Interaction cases where a valid boundary input still triggers a business decline are correct: annual_income = 0 (valid) with the baseline 200000 loan returns DECLINE (loan over 5x income, since 5x0=0), and loan_amount = 500000 (valid max) with baseline 90000 income returns DECLINE (over 5x). Correct check: these two rows are DECLINE via R4, not APPROVE or REJECT.

**+2 (important)** — Each case holds non-target fields constant at a single baseline applicant so the variable under test is isolated, and the baseline applicant itself resolves to APPROVE_STANDARD. Correct check: non-target fields equal the baseline in every isolation case.

**+4 (critical)** — Branch coverage of the decision-flow graph is complete: both the true and false exit of all seven decision points (D1-D7) is exercised by at least one case, including the R5 decomposition into a score gate (D5) and a debt-ratio gate (D6). Correct check: all 14 branches covered; specifically D5-true-then-D6-false leads onward to D7 (not to APPROVE_PRIME), and D5-false bypasses D6 to D7.

**+3 (important)** — A basis-path set walks the independent paths through the graph: 8 paths matching cyclomatic complexity V(G) = 7 decisions + 1 = 8. The eight paths and outcomes are: D1T→DECLINE; D2T→DECLINE; D3T→DECLINE; D4T→DECLINE; D5T,D6T→APPROVE_PRIME; D5T,D6F,D7T→APPROVE_STANDARD; D5F,D7T→APPROVE_STANDARD; D5F,D7F→REFER. Correct check: 8 path cases, each tracing the stated branch sequence to the stated outcome.

**+2 (minor)** — Every case row carries a unique ID, a technique tag (EP / BVA / DT / DB / PATH or equivalent), the complete applicant record (all seven fields), and an expected result. A coverage summary maps techniques and rules to cases, and a branch-coverage view maps each graph branch to a covering case. Correct check: no row missing a field or expected result.

**-5 (negative)** — Under-generation of boundaries: any bounded numeric field missing its min-1/min/max/max+1 set, or any decision threshold missing its at/across-boundary pair. Correct check: flag each missing boundary; a suite with only nominal values fails this.

**-5 (negative)** — Misclassifying an invalid-field case as DECLINE (or a business decline as REJECT), or reporting a threshold outcome on the wrong side of a strict-vs-inclusive operator (e.g. 620 shown as DECLINE, or DTI 43.0 shown as DECLINE). Correct check: flag each such row.

**-3 (negative)** — Missing the ordered-rule interactions: treating the rules as independent so a multi-condition record shows the wrong rule, or omitting the income=0 / max-loan decline interactions. Correct check: flag each.

**-3 (negative)** — Failing to decompose R5 on the flow graph: treating the prime rule as a single branch so the D5-true / D6-false path (strong score, debt ratio just over 36) is not covered or is wrongly sent to APPROVE_PRIME. Correct check: flag if no case exercises D5-true with D6-false landing at APPROVE_STANDARD.

---

## Golden scores 100 against this rubric
The golden suite (63 cases) contains: 7 DT rule cases with the listed outcomes (+5), correct first-match ordering (+5), all 12 decision-boundary cases at/across each operator (+4), 20 BVA cases across all five fields (+4), complete 14-branch coverage of the flow graph with R5 decomposed (+4), 16 EP cases (+3), correct REJECT-vs-DECLINE throughout (+3), the income=0 and max-loan R4 interaction declines (+3), the 8 basis-path cases matching V(G)=8 (+3), baseline isolation with baseline = APPROVE_STANDARD (+2), full row structure + coverage + branch-coverage sheets (+2). It commits none of the negative failure modes. Sum of positives attained = all; negatives not triggered => ~100.

## Metadata
- O*NET: Software Quality Assurance Analysts and Testers (15-1253.00). Tasks: design test plans/cases; document/verify defects; develop/execute test scripts. Skills: Critical Thinking, Quality Control Analysis, Complex Problem Solving, Judgment and Decision Making.
- Web search allowed: No (self-contained in the four files).
- Multimodal: Yes (the four inputs include a hand-drawn decision-flow graph, `LPQ-482-FLOW_Decision_Flow.png`, alongside text/spreadsheet files).
- Time estimate: 7 hours by hand (derive validation EP/BVA for 7 fields, decision-table for 7 ordered rules, boundary analysis on 6 thresholds, branch and basis-path coverage of the flow graph with the R5 gate decomposition, resolve interactions, build and format the workbook).
