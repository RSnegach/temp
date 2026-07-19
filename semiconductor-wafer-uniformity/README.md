# Semiconductor - Wafer Sheet-Resistance Uniformity & Yield

**Occupation:** Semiconductor Processing Technicians (O*NET 51-9141.00)

## Task

Work up sheet resistance (Rs) uniformity and yield for lot L7734-02: a 25-wafer
RTA activation lot measured on a 49-site polar map. Resolve reprobed sites,
apply edge exclusion, compute within-wafer nonuniformity, wafer-to-wafer, and
lot yield, produce a colored wafer map, and call the lot CONTINUE or HOLD.

## Analytical spine

Multi-level statistical aggregation (site to wafer to lot) plus spatial binning,
gated by three reconciliations that must all be done correctly:

- **Edge exclusion** - the 16 outer-ring sites (radius > 72.0 mm, IDs 34-49) are
  measured but excluded from every statistic; 33 included sites per wafer
- **Retest dedup** - 5 sites were reprobed; only the latest-timestamp reading
  counts, the earlier high readings are dropped
- **Uniformity definition** - the pinned half-range formula
  `(max - min) / (2 x mean) x 100`, not sigma/mean

## Files

| Path | What it is |
|------|------------|
| `inputs/L7734-02_Rs_Measurements.xlsx` | Raw per-site Rs export (incl. retest duplicates) + site map |
| `inputs/SPEC-RS-118_Rs_Specification.docx` | Rs limits, nonuniformity formula, bins, acceptance criteria |
| `inputs/SP-RS-045_Sampling_Plan.docx` | 49-site pattern, edge exclusion, retest rule, order of ops |
| `inputs/SP-RS-045_Wafer_Map_Reference.pdf` | Reference for the hand-drawn wafer map |
| `golden/L7734-02_Wafer_Analysis.xlsx` | Lot summary, per-wafer table, colored wafer map, site detail |
| `scripts/wafer.py` | Data engine + statistics (source of truth) |
| `scripts/build_*.py` | Generators for the input and golden artifacts |
| `PROMPT_AND_RUBRIC.md` | Prompt, 12-criterion rubric, metadata |

## Key figures (golden)

Correct disposition **CONTINUE**: lot yield 96.00% (792/825 included sites),
W2W 1.69%, max within-wafer nonuniformity 4.30%. The verdict is discriminating,
not a giveaway: skipping edge exclusion drops yield to ~64.6% (HOLD), and
skipping retest dedup drops it to ~95.4% (HOLD). The wrong uniformity formula
keeps CONTINUE but corrupts every per-wafer number.

Reproduce: `python scripts/wafer.py` prints all locked statistics.
