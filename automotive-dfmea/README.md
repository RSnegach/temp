# Automotive DFMEA - Fuel Delivery (AIAG-VDA Action Priority)

**Occupation:** Automotive Engineers (O*NET 17-2141.02), Manufacturing sector

## Task

Complete and rank a Design FMEA for a gasoline fuel delivery subsystem using the AIAG-VDA (2019) Action Priority method. Reconcile a working failure-mode register, derive each Detection rating from the current control, look up Action Priority from the AP table, apply the action rule, and rank.

## Analytical spine

Matrix scoring + threshold logic. Distinct from the numeric-solve, combinatorial, statistical-aggregation, and visual-synthesis tasks. The golden is fully tabular with live formulas, so it grades without visual-parsing variance.

## Files

| Path | What it is |
|------|------------|
| `inputs/FDS-DFMEA-SCOPE_Subsystem_and_Functions.docx` | Subsystem items and functions (context) |
| `inputs/FDS-DFMEA-RATE_Ratings_and_Action_Priority.docx` | Detection map, AP table, action rule |
| `inputs/FDS-DFMEA-MODES_Failure_Mode_Register.xlsx` | Working mode list: S and O given, controls, duplicate/superseded rows |
| `golden/FDS-DFMEA_Fuel_Delivery.xlsx` | Golden DFMEA: live-formula D and AP, ranked, plus Detection map and AP table tabs |
| `scripts/dfmea.py` | AP table + ratings + failure modes engine (source of truth) |
| `scripts/build_inputs.py`, `build_golden.py` | Input and golden generators |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomic rubric, metadata |

## Key figures (golden)

14 active failure modes (3 dropped as duplicate/superseded). Action Priority: 7 High, 5 Medium, 2 Low. FM-01 (external rail leak, S9) ranks first.

## Why it is hard (fails a model on at least one run)

Three compounding traps, all verified against the engine:
- **AP is a table lookup, not S x O x D.** A model that multiplies gets 7 of 14 rows wrong, under-prioritizing high-severity low-product leak modes (FM-09, FM-12, FM-13 are High but score Low/Medium as a product).
- **Detection is derived from the control**, not given. Guessing a constant D is wrong on 12 of 14 rows.
- **Reconcile the register first.** Scoring the duplicate/superseded rows inflates the count; FM-13's superseded row (O=1) flips its AP from High to Medium versus the active row (O=2).

Reproduce: `python scripts/dfmea.py` prints the full AP grid and the scored DFMEA.
