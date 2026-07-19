# LPQ-482 Test Design Package

Test-suite-design task for the LoanPreQual decision service: derive a full
functional test suite from a feature specification, a decision-rules workbook,
a field-validation reference, and a hand-drawn decision-flow graph.

## Contents

| Path | What it is |
|------|------------|
| `inputs/LPQ-482_Feature_Specification.docx` | Feature spec: behaviour, outcomes, acceptance criteria |
| `inputs/LPQ-482-RULES_Decision_Rules.xlsx` | Ordered 7-rule decision engine, thresholds, operators |
| `inputs/LPQ-482-VAL_Field_Validation_Reference.docx` | Field ranges, enums, validation order |
| `inputs/LPQ-482-FLOW_Decision_Flow_Graph.pdf` | Reference for the hand-drawn decision-flow graph |
| `golden/LPQ-482_Test_Suite.xlsx` | Golden test suite: 63 cases across EP, BVA, DT, DB, PATH |
| `PROMPT_AND_RUBRIC.md` | Prompt, scoring rubric, metadata |
| `flow_preview.png` | Rendered preview of the decision-flow graph |
| `*.py` | Deterministic generators for the suite and input artifacts |
| `LPQ-482_TestDesign_Inputs.zip` | Packaged input files |
| `LPQ-482_Test_Suite_golden.zip` | Packaged golden deliverable |

## Regenerating

The policy engine and case generator live in `suite.py`; the input and golden
artifacts are built by the `build_*.py` scripts. Run `python suite.py` to print
the deterministic case counts and full case list.
