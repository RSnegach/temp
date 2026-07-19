# Lot L7734-02 Wafer Uniformity & Yield - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

We just pulled the Rs map on lot L7734-02 off the four-point probe and I need the uniformity and yield worked up before the shift handoff so we can call the disposition. It is the 25-wafer RTA activation lot, 49-site map per wafer. Day shift wants the call made before they start the next lot behind it, and if this one goes on hold it changes what they run, so I would rather have the numbers right than fast.

The raw export is in `L7734-02_Rs_Measurements.xlsx` (one row per site reading, coordinates in the Site_Map tab). The spec with the limits and the nonuniformity definition is `SPEC-RS-118_Rs_Specification.docx`, and the sampling and edge rules are in `SP-RS-045_Sampling_Plan.docx`. I also scanned in my site-map sketch, `Wafer_Map_Reference.png`, so you can see the ring layout and which ring sits in the edge zone. The three of them are meant to be read together; the export is just the readings, the limits and the rules live in the other two.

Couple of things to watch, because they bite every time. A few sites got reprobed when the tool flagged contact, so there are duplicate rows for some sites; the sampling plan says how to handle those. And the outer ring is in the edge-exclusion band, so those sites are measured but do not go into the stats. Follow the plan's order of operations on both before you compute anything, or the numbers come out wrong, and it is easy to do them in the wrong order and not notice. Use the nonuniformity definition the spec calls out and not whatever the tool software reports, since they are not the same thing.

I need per-wafer within-wafer nonuniformity and yield, the wafer-to-wafer number, the lot yield, and a straight CONTINUE or HOLD against the acceptance criteria in the spec. Give me a colored wafer map for a representative wafer so I can eyeball the signature and see whether it is center-to-edge or something more random. Output as `L7734-02_Wafer_Analysis.xlsx` with a lot summary, the per-wafer table, the wafer map, and the per-site detail for the mapped wafer.

---

## RUBRIC (weights in the numeric field only)

**+5 (critical)** — Edge exclusion applied correctly: the 16 outer-ring sites with radius > 72.0 mm (site IDs 34-49) are excluded from all statistics; each wafer's stats are computed over exactly 33 included sites. Correct check: n_included = 33 per wafer, 825 included site-measurements across the lot.

**+5 (critical)** — Lot disposition is CONTINUE, derived from all three criteria passing: lot yield 96.00% (>= 95%), W2W 1.69% (<= 3%), and every wafer's WIW NU <= 5.0%. Correct check: verdict CONTINUE with those three supporting values.

**+4 (critical)** — Within-wafer nonuniformity uses the pinned half-range formula (max - min)/(2 x mean) x 100, not a sigma/mean definition. Spot values: W01 = 3.68%, W07 = 4.08%, W13 = 4.25%, W24 = 3.61%. Correct check: these match; the sigma/mean method (which would give W01 ~2.48%) is not used.

**+4 (critical)** — Retest reconciliation applied: for the 5 reprobed sites (W03/site15, W07/site28, W12/site5, W19/site33, W22/site20) only the latest-timestamp reading is kept; the earlier high readings are dropped. Correct check: deduped to 1225 site-measurements total; the superseded originals (each ~6.5 ohm/sq higher) do not appear in any statistic.

**+3 (important)** — Lot mean Rs = 85.57 ohm/sq and W2W = 1.69%, both computed over included sites and per-wafer means. Correct check: these two values.

**+3 (important)** — Lot yield = 96.00% (792 of 825 included site-measurements within the 80.75 to 89.25 ohm/sq spec). Correct check: 792/825.

**+3 (important)** — Per-wafer yields for the low-yield wafers are correct: W01 81.8% (6 fails), W07 75.8% (8 fails), W13 78.8% (7 fails), W24 84.8% (5 fails). Correct check: these fail counts, driven by the edge-fast radial signature at the outer included ring.

**+2 (minor)** — A colored wafer map for a representative wafer bins each included site PASS / WARN / FAIL against target and marks edge-excluded sites distinctly; a per-site detail table lists radius, Rs, included flag, and bin. Correct check: map present, edge sites marked separate from failing sites.

**+2 (minor)** — Bin thresholds correct: PASS within 82.45 to 87.55, WARN in spec but outside that band, FAIL below 80.75 or above 89.25. Correct check: a boundary site is binned per the inclusive limits in the spec.

**-5 (negative)** — Edge-excluded sites included in the statistics. This inflates every wafer mean (~+1.9 ohm/sq on a hot wafer) and pushes max WIW to ~6.3% and lot yield down to ~64.6%, which would wrongly flip the disposition to HOLD. Correct check: flag if n_included != 33 or yield near 64%.

**-5 (negative)** — Retest duplicates not reconciled (bad original readings kept or averaged in). This raises WIW on the affected wafers past 5% and drops lot yield to ~95.4%, wrongly flipping the disposition to HOLD. Correct check: flag if the ~6.5-high originals appear or the total is 1230 not 1225.

**-3 (negative)** — Wrong within-wafer nonuniformity definition (sigma/mean or full-range/mean instead of half-range). Correct check: flag if W01 WIW is reported as ~2.48% (sigma/mean) or ~7.4% (full range/mean) rather than 3.68%.

---

## Golden scores 100 against this rubric
The golden reproduces every value: 33 included sites/wafer (825 total), 1225 deduped measurements, lot mean 85.57, W2W 1.69%, lot yield 96.00% (792/825), per-wafer WIW and yields as listed, CONTINUE disposition, colored map + site detail. It commits none of the three negative failure modes. Positives all attained; negatives not triggered => ~100.

## Metadata
- O*NET: Semiconductor Processing Technicians (51-9141.00). Tasks: operate/monitor equipment and inspect product; measure and record process data; maintain process logs and disposition material. Skills: Quality Control Analysis, Monitoring, Critical Thinking, Mathematics.
- Web search allowed: No (self-contained in the four files).
- Multimodal: Yes (a hand-drawn wafer-map reference, `Wafer_Map_Reference.png`, alongside the spreadsheet and spec documents).
- Time estimate: 6 hours by hand (dedup ~1230 rows, apply edge exclusion by radius, compute WIW/yield for 25 wafers, W2W and lot yield, build the colored map and disposition).
