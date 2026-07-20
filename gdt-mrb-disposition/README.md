# GD&T Inspection Disposition - Mounting Bracket (ASME Y14.5, MMC/MRB)

**Occupation:** Automotive Engineers (O*NET 17-2141.02), Manufacturing sector

## Task

Disposition every controlled feature on a machined bracket first article as ACCEPT, MRB, or reject, from an engineering drawing, a CMM inspection report, and a standard disposition procedure. Read the feature control frames off the drawing, compute bonus tolerance and datum shift under maximum material condition, convert measured offsets to a position deviation, check size before position, and reach a disposition for each feature.

## Analytical spine

GD&T material-condition disposition: symbol extraction from a drawing plus material-boundary arithmetic (bonus, datum shift, virtual condition) with a size-first decision rule. Distinct from the numeric-solve, combinatorial, statistical-aggregation, matrix-scoring, and visual-synthesis tasks. The golden is fully tabular with live formulas, so it grades without visual-parsing variance.

## Files

| Path | What it is |
|------|------------|
| `inputs/drawing_bracket.pdf` | Engineering drawing: feature control frames, datum scheme, size limits |
| `inputs/GDT-DISP_Interpretation_and_Disposition_Procedure.docx` | Standard method: bonus, datum shift, deviation, disposition rule |
| `inputs/CMM_inspection_report.xlsx` | Measured local sizes and center offsets; datum feature sizes on tab 2 |
| `inputs/inspection_sketch_reference.png` | Inspector bring-up sketch flagging marginal holes (pointer, not values) |
| `golden/BRKT-4471_Inspection_Disposition.xlsx` | Golden disposition: live-formula bonus/shift/total/deviation/size/disposition, plus Datums and Summary tabs |
| `scripts/gdt.py` | Feature register, bonus/shift/VC engine, disposition logic (source of truth) |
| `scripts/render_drawing.py` | Drawing PNG/PDF generator |
| `scripts/make_cmm.py`, `build_golden.py`, `build_docs.py`, `render_sketch.py` | Input and golden generators |
| `scripts/xlsx_live.py` | Live-formula cache injection, decimal normalization, fingerprint scrub |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomic rubric, metadata |

## Key figures (golden)

Nine features. Disposition: 6 ACCEPT (H1, H2, H3, P1, S1, F1), 2 MRB (H4, R1), 1 REJECT on size (H5). Datum B departs 0.040 from MMC (shift applied to the four holes). H3 survives only with full LMC bonus (0.100) plus datum shift (0.040).

## Why it is hard (a human 6-hour task; distinct trap surfaces)

Five compounding traps, all verified against the engine:
- **Bonus direction flips with feature type.** The dowel pin P1 is external: bonus = MMC minus measured, so it earns tolerance as it shrinks. Computing it in the hole direction gives the wrong sign and mis-dispositions P1.
- **RFS grants no bonus.** The precision bore R1 carries no modifier, so its 0.07 size departure buys nothing; it is MRB. A model that applies bonus by habit wrongly accepts it.
- **Datum shift applies only where the modifier is on the datum.** B at MMC adds 0.040 to the four holes; R1 references B without the modifier, so it gets no shift.
- **Size is checked first.** H5 is over its size limit, so it rejects on size and position is moot; scoring its position (which passes) is wrong.
- **Bonus rescue.** H3 exceeds both the stated tolerance and the bonus-only allowance; only bonus plus datum shift together (0.340) accept it. Dropping either sends it to MRB.

Reproduce: `python scripts/gdt.py` prints the datum shifts and the full per-feature disposition table.

## Note

The `inputs/inspection_sketch_reference.png` is a clean reference render of the hand-drawn bring-up sketch. The final submission uses a photographed redraw in its place.
