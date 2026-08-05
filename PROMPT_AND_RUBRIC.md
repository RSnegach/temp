# HTS-1 Delta-V and Propellant Budget

## Occupation

Aerospace Engineers (O*NET 17-2011.00), Professional Scientific and Technical Services.

**Tasks:** Formulate mathematical models or other methods of computer analysis to develop, evaluate, or modify design, according to customer engineering requirements. Direct or coordinate activities of engineering or technical personnel involved in designing, fabricating, modifying, or testing of aerospace products. Plan or conduct experimental, environmental, operational, or stress tests on models or prototypes of aircraft or aerospace systems or equipment. Evaluate product data or design from inspections or reports for conformance to engineering principles, customer requirements, or quality standards. Write technical reports or other documentation, such as handbooks or bulletins, for use by engineering staff, management, or customers.

**Skills:** Mathematics, Science, Critical Thinking, Complex Problem Solving, Reading Comprehension.

**Multimodal:** yes (the tanking record is a photograph of a signed paper form).
**Web search required:** no.
**Estimated time for a practitioner with no LLM:** 5 to 7 hours.

## Prompt

> Need the pre-ship delta-V and propellant budget for HTS-1 put together before the review board on Friday. I have the maneuver plan workbook, the propulsion ground rules, Priya's notes from GN&C, and a photo of the tanking record from the pad.
>
> The maneuver sheet leaves the apogee insertion and the disposal burn as DERIVE, so those have to be sized off the orbit parameters tab per the ground rules. Everything else on that sheet is either given or wrong in some way that Priya's notes call out, so read her notes before you trust the sheet.
>
> What I need out of it: the derived delta-V for each maneuver with the loss factors applied, the rocket-equation propellant burn per maneuver with the mass bookkeeping right through payload separation, usable versus required main propellant, and where our margin lands against the 5% gate. If we are short, tell me the top-off quantity. Show the RCS hydrazine separately.
>
> Put your reconciliation and a short findings and recommendation overview in their own tabs in the same workbook. Every derived number needs to be a working spreadsheet formula that traces back to the raw inputs, not a typed-in result. The board will click cells.
>
> Deliverable is one Excel workbook, `deltav_propellant_budget.xlsx`. Make it clean enough to drop straight into the pre-ship package.

## Input files

| Path | What it is |
|------|------------|
| `inputs/maneuver_plan.xlsx` | Maneuver plan (M2 and M4 left as DERIVE, M3 booked in ft/s), orbit parameters, telemetry channel list, ground station contact schedule |
| `inputs/propulsion_groundrules.docx` | HTS-PROP-007 Rev B: derivation methods, fixed masses, Isp policy, losses and residuals, propellant accounting, margin policy |
| `inputs/engineering_notes.docx` | GN&C note from Priya: combined burn not split, acceptance Isp not nameplate, M1 descoped, M3 unit error, payload sep timing, as-loaded not planned, GHe excluded |
| `inputs/prop_load_record.jpg` | Photograph of tanking record TNK-2026-114: MMH, NTO, N2H4, GHe as loaded, with signatures |

Distractors carried on purpose: the telemetry channel list and the 49 pass ground contact schedule are irrelevant to the budget, the 322.0 s nameplate Isp is superseded, the 800 kg planning load is not what was loaded, the M1 phasing burn is descoped but still printed on the maneuver sheet, and the GHe on the tanking record is not flight propellant.

## Analytical spine

Multi-source numeric derivation with adversarial inputs. No single document contains the answer, and three of the four documents contain at least one figure that must be rejected in favour of another document. The solver derives two delta-V values from orbital mechanics, propagates a sequential rocket-equation mass chain across a mid-sequence payload separation, and lands a margin verdict against a policy gate. Every conflict has a documented resolution and a traceable numeric effect.

## Golden solution

`golden/deltav_propellant_budget.xlsx`, seven sheets:

| Sheet | Contents |
|-------|----------|
| Inputs | All raw scalars from the four source documents, shaded, nothing derived |
| Delta-V Derivation | Geometry, vis-viva, law of cosines M2, split-burn comparison, two-burn Hohmann M4, M3 conversion |
| Maneuver Budget | Per-maneuver ideal dV, loss, effective dV, mass before, propellant used, payload separation, mass after; excluded M1 called out below the table |
| Margin Summary | Usable vs required, margin against the gate, top-off, and the nameplate-Isp sensitivity chain |
| RCS Budget | Hydrazine loaded vs budget, plus the as-loaded mixture ratio check |
| Reconciliation | Eleven numbered discrepancies with the treatment taken, the source of record, and the linked numeric effect |
| Findings | Headline block plus six prose sections including the recommendation |

All 92 derived cells are live Excel formulas chained back to the Inputs sheet. Verified by independent recalculation: `python scripts/verify_golden.py` reloads the workbook, recomputes every formula from scratch, and compares against the stored value.

### Key figures

| Quantity | Value |
|---|---|
| Va at GTO apogee | 1597.39 m/s |
| Vc circular GEO | 3074.66 m/s |
| M2 ideal (combined) | 1803.60 m/s |
| M2 if split (rejected) | 2912.80 m/s, a 1109.21 m/s penalty |
| M2 effective (1.5% loss) | 1830.65 m/s |
| M3 (115 ft/s converted) | 35.05 m/s |
| M4 (two-burn Hohmann) | 10.88 m/s |
| Total effective delta-V | 1876.58 m/s |
| Ve at acceptance Isp 318.5 s | 3123.42 m/s |
| Start wet mass m0 | 1569.20 kg |
| M2 propellant | 695.95 kg |
| Mass after M2 and separation | 373.25 kg |
| M3 propellant | 4.17 kg |
| M4 propellant | 1.28 kg |
| Main propellant required | 701.40 kg |
| Main propellant loaded | 740.00 kg |
| Usable (less 2% residual) | 725.20 kg |
| Margin | 23.80 kg, 3.39% |
| Verdict | under the 5% gate |
| Top-off required | 11.50 kg, to a 751.50 kg load |
| Cost of the Isp shortfall | 5.56 kg |
| Usable lost by underloading | 58.80 kg |
| RCS margin | 1.70 kg, 22.67% |

## Rubric

Weights run +5 to -5. Tolerances are stated where a rounding path could legitimately shift the last digit.

| # | Criterion | Weight |
|---|---|---|
| 1 | Derives the M2 combined apogee insertion ideal delta-V as 1803.60 m/s (accept 1800 to 1807 m/s) using the law of cosines on the GTO apogee velocity and the circular GEO velocity with the full 27 degree plane change. | +5 |
| 2 | States or applies the GTO apogee velocity as 1597.39 m/s (accept 1596 to 1599 m/s) and the circular GEO velocity as 3074.66 m/s (accept 3073 to 3076 m/s). | +3 |
| 3 | Applies the 1.5% finite-burn and steering loss to the M2 ideal delta-V only, giving an effective M2 of 1830.65 m/s (accept 1827 to 1834 m/s), and applies no loss factor to M3 or M4. | +4 |
| 4 | Derives the M4 disposal delta-V as 10.88 m/s (accept 10.5 to 11.3 m/s) by summing both impulses of a two-burn Hohmann transfer from GEO to a circular orbit 300 km above GEO. | +4 |
| 5 | Converts the M3 GEO trim from the 115 ft/s booked on the maneuver sheet to 35.05 m/s (accept 35.0 to 35.1 m/s) before using it. | +3 |
| 6 | Excludes the M1 phasing burn from the propellant budget entirely, and states that it was descoped. | +4 |
| 7 | Uses the 318.5 s acceptance hot-fire Isp rather than the 322.0 s nameplate value, giving an exhaust velocity of 3123.42 m/s (accept 3122 to 3125 m/s). | +5 |
| 8 | Sets the start wet mass to 1569.20 kg (accept 1569 to 1570 kg) from 320.0 kg dry plus 500.0 kg payload plus 740.00 kg main propellant plus 9.20 kg hydrazine. | +4 |
| 9 | Takes main propellant loaded as 740.00 kg from the tanking record (MMH 279.2 plus NTO 460.8) rather than the 800 kg planning target. | +5 |
| 10 | Excludes the GHe pressurant from flight propellant mass, and states that it is loaded through ground support equipment. | +3 |
| 11 | Removes the 500 kg payload from the stage mass immediately after the M2 apogee insertion, so that M3 and M4 are sized on a stage of 373.25 kg (accept 372 to 375 kg) rather than on the payload-inclusive mass. | +5 |
| 12 | Computes per-maneuver propellant from the rocket equation as a sequential chain, giving 695.95 kg for M2 (accept 694 to 698 kg), 4.17 kg for M3 (accept 4.0 to 4.3 kg), and 1.28 kg for M4 (accept 1.2 to 1.4 kg). | +5 |
| 13 | Reports total main propellant required as 701.40 kg (accept 699 to 704 kg). | +5 |
| 14 | Deducts the 2.0% residual from loaded main propellant to give 725.20 kg usable (accept 724.5 to 726 kg). | +4 |
| 15 | Reports the main propellant margin as 3.39% (accept 3.2% to 3.6%) computed as (usable minus required) divided by required. | +5 |
| 16 | States explicitly that the margin does not meet the 5% pre-ship gate. | +5 |
| 17 | Quantifies the top-off needed to reach the 5% gate as 11.50 kg (accept 10.5 to 12.5 kg), or equivalently a total main propellant load of 751.50 kg. | +5 |
| 18 | Reports the RCS hydrazine budget separately from the main propellant, showing 9.20 kg loaded against the 7.50 kg mission budget for a margin of 1.70 kg, and does not offset main propellant margin with it. | +4 |
| 19 | Includes a reconciliation tab or section documenting the key changes and corrections made to the input data (Isp used, units converted, maneuvers included or excluded, mass bookkeeping). | +5 |
| 20 | Includes a findings and recommendations tab or section with an overview of the margin status, the contributing factors, and a recommendation (top-off quantity or waiver path). | +5 |
| 21 | Presents the delta-V derivation as an organized element (a labeled tab, table, or block) showing the intermediate quantities, not only the final delta-V numbers. | +3 |
| 22 | Presents the reconciled maneuver list and the per-maneuver propellant burn as a table with one row per maneuver carrying delta-V, mass before, propellant used, and mass after. | +4 |
| 23 | Every derived quantity in the delivered workbook is a working spreadsheet formula that references the raw input values, not a hard-coded constant. | +4 |
| 24 | Attributes the tight margin to identified causes, quantifying at least one: the Isp shortfall costing 5.56 kg (accept 5.0 to 6.2 kg) or the underload costing 58.80 kg of usable propellant (accept 57 to 60 kg). | +3 |
| 25 | Delivers a single Excel workbook named `deltav_propellant_budget.xlsx`. | +2 |
| 26 | Splits the apogee insertion into a separate circularization and a separate plane change and sums them, producing an M2 near 2912.80 m/s instead of the combined 1803.60 m/s. | -5 |
| 27 | Uses the 322.0 s nameplate Isp for the budget instead of the 318.5 s acceptance value. | -5 |
| 28 | Includes the descoped M1 phasing burn in the propellant budget. | -4 |
| 29 | Uses 800 kg as the main propellant loaded, or includes the GHe pressurant in propellant mass. | -4 |
| 30 | Carries the 500 kg payload through the M3 and M4 burns instead of separating it after M2. | -4 |
| 31 | Uses the M3 trim as 115 m/s without converting from ft/s. | -3 |
| 32 | Reports a margin that meets or exceeds the 5% gate, or omits the margin verdict entirely. | -5 |
| 33 | Compares required propellant against loaded propellant without deducting the 2.0% residual. | -3 |

Golden solution scores the full positive set and none of the negatives.

## Reproduce

```
python scripts/engine.py          # prints every figure in the table above
python scripts/gc_data.py         # ground contact variation guards
python scripts/build_input.py     # rebuilds inputs/maneuver_plan.xlsx
python scripts/fix_docx.py        # stages the two docx inputs, black headings, ASCII only
python scripts/build_golden.py    # rebuilds golden/deltav_propellant_budget.xlsx
python scripts/verify_input.py    # input audit
python scripts/verify_golden.py   # independent recalculation of all 92 formula cells
```
