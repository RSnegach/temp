# Fuel Delivery DFMEA - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

We're closing out the Design FMEA on the fuel delivery subsystem for the FX-mid program and I need it scored and ranked before the design review Thursday. It's the AIAG-VDA method, so Action Priority, not RPN.

Everything you need is in three files. The scope doc (`FDS-DFMEA-SCOPE_Subsystem_and_Functions.docx`) defines the items and their functions. The ratings reference (`FDS-DFMEA-RATE_Ratings_and_Action_Priority.docx`) has the Detection rating map, the Action Priority table, and the action rule. And the failure-mode register (`FDS-DFMEA-MODES_Failure_Mode_Register.xlsx`) is the working list of modes with severity and occurrence already assigned.

Couple of things that trip people up on this one. The register is a Rev C working list and it still has some duplicate and superseded rows in it, so reconcile those before you score anything, take the current row, not the old one. Detection is not filled in: you get it by reading each mode's current detection control and looking that control up in the Detection map. And Action Priority comes off the AP table by severity, occurrence, and detection together, it is not severity times occurrence times detection. That catches people every time.

Give it back as `FDS-DFMEA_Fuel_Delivery.xlsx`: one row per active failure mode with severity, occurrence, the detection control, the detection rating, the Action Priority, and the action call, ranked highest priority first. Write the detection and Action Priority as live formulas off the reference tables so the sheet recalculates if a rating changes, and keep the AP table and Detection map on their own tabs. I want to be able to trace every number.

---

## RUBRIC (weights in the numeric field only)

Each criterion is one atomic check. Detection and Action Priority values state their derivation from the reference tables, not bare golden-only numbers.

Reconciliation:
**+4** The three non-current rows are dropped before scoring: FM-04 rev1 (Superseded), FM-07 (Duplicate of FM-01), FM-13 rev1 (Superseded). The scored DFMEA has 14 active failure modes, not 17.
**-4** Any duplicate or superseded row is scored (17 or 16 or 15 rows instead of 14), or FM-13 is scored from its rev1 (O=1) instead of the active rev2 (O=2).

Detection derivation (D from the control via the Detection map, not guessed):
**+3** FM-14 (control "None / not detectable") has Detection = 10.
**+2** FM-08 (control "Visual inspection only") has Detection = 8.
**+2** FM-09 (control "100% automated with error-proofing") has Detection = 2.
**+1** FM-01 (control "In-line automated leak test") has Detection = 4.
**-3** Detection is filled with a guessed or constant value instead of the control's mapped rating (e.g. any mode whose D does not match the Detection map for its named control).

Action Priority by table lookup (not S x O x D):
**+5** AP is read from the AP table by (S, O, D) band, not computed as a product. FM-09 (S9 O2 D2) is High, though S x O x D = 36 would suggest Low.
**+3** FM-13 (S9 O2 D3, active row) is High; taking the superseded O=1 row would instead give Medium.
**+2** FM-01 (S9 O3 D4) is High.
**+2** FM-02 (S6 O5 D6) is Medium, though S x O x D = 180 would suggest High under an RPN threshold.
**-5** AP is derived by multiplying S x O x D (or thresholding the product) rather than by the AP table, mis-scoring the high-severity low-product leak modes (FM-09, FM-12, FM-13 shown as Medium/Low instead of High).

Counts and action:
**+3** Exactly 7 modes are Action Priority High (FM-01, FM-12, FM-13, FM-09, FM-04, FM-14, FM-08), each with action = Yes.
**+2** 5 modes are Medium (action Review) and 2 are Low (action No): 14 total across H/M/L.
**+2** The action column follows the rule: High = Yes, Medium = Review, Low = No.

Ranking and structure:
**+3** Rows are ranked High then Medium then Low, and within priority by descending Severity, then Occurrence, then Detection. FM-01 (S9 O3 D4) ranks first.
**+2** Detection and Action Priority are live formulas referencing the Detection map and AP table tabs (not static values), so the sheet recalculates when a rating changes.
**+2** The workbook has the DFMEA sheet plus a Detection map tab and an AP table tab.

---

## Golden scores 100 against this rubric
The golden `FDS-DFMEA_Fuel_Delivery.xlsx` reconciles to 14 active modes (drops FM-04 rev1, FM-07, FM-13 rev1), derives each Detection from the named control via the Detection map, looks up Action Priority from the AP table (7 High, 5 Medium, 2 Low), applies the action rule, and ranks FM-01 first. Detection and AP are live formulas off the reference tabs. It commits none of the failure modes.

## Metadata
- O*NET occupation: Automotive Engineers (17-2141.02)
- O*NET tasks (verbatim from O*NET):
  - Perform failure, variation, or root cause analyses.
  - Establish production or quality control standards.
  - Conduct automotive design reviews.
  - Write, review, or maintain engineering documentation.
- O*NET skills (Skills section): Critical Thinking, Reading Comprehension, Mathematics, Active Learning.
- Web search allowed: No (self-contained in the three files).
- Multimodal: No (all text and spreadsheet inputs).
- Time estimate: 6 hours by hand (reconcile the register, derive Detection per mode from the controls map, look up Action Priority for each mode from the table, apply the action rule, rank, and build the workbook with live lookups).
