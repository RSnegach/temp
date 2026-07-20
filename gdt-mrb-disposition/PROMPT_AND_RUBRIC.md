# GD&T Inspection Disposition (BRKT-4471) - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

I need the final dimensional disposition on the BRKT-4471 mounting bracket, serial 4471-0007, before it can ship to the customer. First articles came off the CMM and I need every controlled feature called ACCEPT, MRB, or rejected, with the math shown so I can defend it in the material review.

Everything is in four files. The drawing (`drawing_bracket.pdf`) has the feature control frames and the datum scheme, read the callouts straight off it. The disposition procedure (`GDT-DISP_Interpretation_and_Disposition_Procedure.docx`) is our standard method: order of operations, how bonus and datum shift work, how to turn the measured offsets into a position deviation, and the accept/MRB/reject rule. The CMM results are in `CMM_inspection_report.xlsx`, measured local sizes and the center offsets from true position, plus the datum feature sizes on the second tab. There's also my marked-up bring-up sketch (`inspection_sketch_reference.png`) flagging the holes that looked marginal, use it as a pointer, the numbers of record are in the CMM report.

The things that bite people on this part: the four mounting holes are called at MMC with datum B also at MMC, so they get bonus from their own size departure and a datum shift from B, but the precision bore R1 is called RFS with no modifier, so it gets nothing no matter how its size departs. The dowel pin P1 is an external feature, so its bonus runs the other way, it earns tolerance as it gets smaller, not larger. Check size before position: if a feature is out of size, it rejects on size and position is moot. And profile and flatness are not features of size, no bonus, compare straight to the tolerance.

Give it back as `BRKT-4471_Inspection_Disposition.xlsx`, one row per feature with the extracted callout, the stated tolerance, the bonus, the datum shift, the total allowed position tolerance, the actual position deviation, the virtual condition, the size check, and the disposition. Add a short summary count of how many features landed in each category. Write the bonus, shift, total, deviation, size check, and disposition as live formulas off the measured cells and a datum tab, not typed-in numbers, so it recalculates if a measurement gets corrected. I want to trace every value.

---

## RUBRIC (weights in the numeric field only)

Each criterion is one atomic check. Derived values state their derivation from the callout and the measured inputs, not bare golden-only numbers.

Callout extraction (read the feature control frames off the drawing):
**+3** The four mounting holes H1 to H4 are read as position, diameter 0.20 at MMC, to datums A, B at MMC, C. The MMC modifier on both the tolerance and datum B is captured.
**+2** R1 is read as position, diameter 0.10, RFS (no material condition modifier on the tolerance).
**+2** P1 is identified as an external feature (dowel pin), position diameter 0.15 at MMC to datum A.
**+1** S1 is read as profile of a surface (tolerance 0.30) and F1 as flatness (tolerance 0.05), neither a feature of size.
**-3** Any feature control frame is misread in a way that changes the disposition (for example R1 treated as if it carried an MMC modifier, or a hole tolerance value transcribed wrong).

Bonus tolerance (departure from MMC, correct direction per feature type):
**+3** H3 bonus is 0.100, from its measured size 8.10 at LMC minus MMC 8.00 (full bonus).
**+2** P1 bonus is 0.070, computed as external: MMC 12.00 minus measured 11.93 (bonus increases as the pin shrinks), not measured minus MMC.
**+2** H2 bonus is 0.000 because it is measured at MMC (8.00), even though a datum shift still applies.
**+2** R1 bonus is 0.000 because it is RFS, despite its size departing from MMC by 0.07.
**-4** Bonus for the external pin P1 is computed in the internal direction (measured minus MMC, giving a negative or wrong value), or any RFS feature is given a nonzero bonus.

Datum shift (only when a datum of size is referenced at MMC):
**+3** Datum B departure is 0.040 (measured 10.04 minus MMC 10.00), and this 0.040 shift is added to each of H1 to H4.
**+2** No datum shift is applied to P1, R1, or H5, because none references a datum feature of size at MMC (R1 references B without a modifier, so B contributes no shift there).
**-3** A datum shift is applied to a feature whose frame does not carry the modifier on that datum (for example adding shift to R1), or datum B's departure is computed against the wrong limit.

Position deviation and total allowed:
**+3** Actual position deviation is computed as a diameter, 2 times the square root of (devX squared plus devY squared). H4 is 0.372 from (0.150, 0.110).
**+2** Total allowed for H3 is 0.340 (stated 0.20 plus bonus 0.100 plus shift 0.040), and H3 is ACCEPT because 0.320 is within 0.340.
**+2** Total allowed for H2 is 0.240 (stated 0.20 plus 0 bonus plus 0.040 shift), and H2 is ACCEPT because 0.216 is within 0.240.
**-3** Deviation is compared as a radius against a diameter tolerance (or the factor of 2 is dropped), changing any disposition.

Size-first and dispositions:
**+3** H5 is REJECT on size: measured 5.09 exceeds the 5.06 upper limit, so position is not evaluated.
**+3** H4 is MRB: deviation 0.372 exceeds total allowed 0.260 even with bonus 0.020 and shift 0.040.
**+2** R1 is MRB: deviation 0.135 exceeds the 0.100 allowed, with no bonus and no shift available under RFS.
**+2** S1 is ACCEPT (profile 0.240 within 0.30) and F1 is ACCEPT (flatness 0.038 within 0.05), each compared directly with no bonus.
**+2** The disposition counts are exactly 6 ACCEPT, 2 MRB, 1 REJECT (size), across 9 features.
**-4** H5 is dispositioned on position (ACCEPT or MRB) instead of rejected on size.

Virtual condition and live formulas:
**+2** Virtual condition is reported per feature: internal features use MMC minus stated tolerance (H1 to H4 give 7.80), the external pin uses MMC plus stated tolerance (P1 gives 12.15).
**+2** Bonus, datum shift, total allowed, deviation, size check, and disposition are live formulas referencing the measured cells and a datum tab, not static typed values, so the workbook recalculates when a measurement changes.
**-2** The derived columns are static numbers rather than formulas, so a changed measurement does not propagate.

---

## Golden scores 100 against this rubric
The golden `BRKT-4471_Inspection_Disposition.xlsx` extracts the six feature control frames, applies bonus in the correct direction per feature type (zero for the RFS bore and the at-MMC hole), adds datum B's 0.040 shift only to the four holes called to B at MMC, computes each position deviation as a diameter, checks size before position, and reaches 6 ACCEPT (H1, H2, H3, P1, S1, F1), 2 MRB (H4, R1), 1 REJECT on size (H5). Every derived value is a live formula off the measured inputs and the datum tab.

## Metadata
- O*NET occupation: Automotive Engineers (17-2141.02)
- O*NET tasks (verbatim from O*NET):
  - Establish production or quality control standards.
  - Conduct automotive design reviews.
  - Write, review, or maintain engineering documentation.
  - Read and interpret blueprints, technical drawings, schematics, or computer-generated reports.
- O*NET skills (Skills section): Critical Thinking, Reading Comprehension, Mathematics, Active Learning.
- Web search allowed: No (self-contained in the four files).
- Multimodal: Yes (an engineering drawing and a marked-up hand sketch must be read).
- Time estimate: 6 hours by hand (read every feature control frame off the drawing, transcribe the CMM results, compute bonus in the correct direction per feature, derive datum shift, convert offsets to position deviation, apply the size-first disposition rule to nine features, and build the workbook with live lookups).
