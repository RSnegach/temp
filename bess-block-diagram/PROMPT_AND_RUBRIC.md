# BESS Block Diagram - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

We're putting the block diagram package together for the containerized BESS platform and I need you to draft the site single-line as a block diagram in Excel. We quote this platform in two build sizes and I need both drawn: the standard 3 power-block build and the extended 5 power-block build.

I can't hand you a marked-up drawing because that's exactly what I need produced. What I can give you is the block taxonomy (`BX-SE-TAX-014_Block_Taxonomy.docx`), which lists every block type, its tag convention, and how many of each go per power block and per site, and the interconnect schedule (`BX-SE-ICD-021_Interconnect_Harness_Schedule.docx`), which defines the four harness families and the rules for how everything wires together. There's also a one-block wiring reference (`BX-SE-SK-104_Power_Block_Wiring.pdf`) so you can see how a single power block is wired internally and where it ties up to the site section. That reference shows one block only. You need to replicate that pattern for every power block in each build and wire the shared site section per the schedule.

Watch the interconnect schedule carefully on two things. The comms inside a block is a daisy chain, not a home run to the controller. And the AC collection on the larger build does not just scale up one for one, there's a rule about the bus feeder count that changes how the upper blocks reach the bus. Read it and apply it.

Give it back as `bess_block_diagram.xlsx`. Put the standard build on one sheet and the extended build on another: each block a labeled box, each connection a line tagged and colored by its harness family, plus the harness color key. Then, so the shop can check the drawing against a takeoff, add a block inventory and a connection list for each build (from block, to block, harness family, one row per connection) on their own tabs. I want to be able to count blocks and trace every harness both from the drawing and from the lists.

---

## RUBRIC (weights in the numeric field only)

**+2 (critical)** — Standard build site section (Std_Inventory sheet): exactly one each of Site Controller, Aux Transformer, MV Step-up Transformer, Revenue Metering, and AC Collection Bus, and no AC Combiner Panel row. Correct check: those 5 site counts are 1 and AC-CMB is absent.

**+3 (critical)** — Standard build per-block equipment (Std_Inventory sheet): 3 PCS, 3 DC Combiner, 12 Battery Rack, 12 Rack BMS (3 power blocks x 4 racks). Correct check: these four counts, and the inventory totals 35 blocks.

**+5 (critical)** — Extended build applies the AC bus-feeder exception (Ext_Inventory + Ext_Connections sheets): the inventory includes 1 AC Combiner Panel (AC-CMB) and totals 56 blocks; the connection list shows PCS-01/02/03 to AC-BUS, PCS-04 and PCS-05 to AC-CMB (not AC-BUS), and one AC-CMB to AC-BUS row. Correct check: those AC-PWR rows are present. A linear scale-up (no AC-CMB row, all 5 PCS to AC-BUS) is wrong.

**+4 (critical)** — COMMS is a daisy chain within each power block: in the connection list the K Rack BMS units chain BMS-n-1 to BMS-n-2 to BMS-n-3 to BMS-n-4 (3 links per block), the head BMS-n-1 connects to that block's PCS, and each PCS connects to SC-01. Correct check: COMMS rows show BMS-to-BMS chain links, not every BMS wired to SC-01 or to the PCS.

**+4 (critical)** — Harness edge counts in the connection-list summaries are correct. Standard build: DC-PWR 15, AC-PWR 5, COMMS 16, AUX-24V 7 (43 total). Extended build: DC-PWR 25, AC-PWR 8, COMMS 26, AUX-24V 11 (70 total). Correct check: these eight per-harness counts on the Std and Ext connection sheets.

**+3 (important)** — DC-PWR is wired within each block only: in the connection list each Battery Rack RK-n-k connects to its own DC Combiner DCC-0n (4 per block) and each DCC-0n connects to its PCS-0n (5 DC-PWR rows per block). Correct check: no DC-PWR row crosses blocks (e.g. RK-1-k to DCC-02) or reaches a site block.

**+3 (important)** — AUX-24V feeds only active equipment: in the connection list, AUX-XFMR connects to each PCS and each DC Combiner (2 per block) and to SC-01. Standard build shows exactly 7 AUX-24V rows (3 PCS + 3 DCC + SC-01). Correct check: no AUX-24V row targets a Rack, BMS, AC-BUS, Metering, MV-XFMR, or AC-CMB.

**+3 (important)** — Site-level blocks and links exist once, not per power block: the inventory shows count 1 for AC-BUS, Metering, and MV-XFMR; the connection list has single rows AC-BUS to MTR-01, MTR-01 to MV-XFMR (AC-PWR), MTR-01 to SC-01 (COMMS), and AUX-XFMR to SC-01 (AUX-24V). Correct check: none of these site items or links are duplicated per power block.

**+3 (important)** — Naming and indexing are consistent across both builds: PCS-0n and DCC-0n by block, RK-n-k and BMS-n-k by block then position (e.g. RK-3-2, BMS-5-4). Correct check: tags follow this scheme with no off-by-one.

**+2 (minor)** — Both builds are on separate sheets, each block is a labeled box, each connection is a line colored and tagged by harness family (DC-PWR red, AC-PWR black, COMMS blue, AUX-24V green), and a harness color key is present. Correct check: two sheets, colored tagged lines, legend.

**-5 (negative)** — Extended build treated as a linear scale-up: no AC Combiner Panel in Ext_Inventory and the connection list shows all 5 PCS to AC-BUS, giving AC-PWR 10 instead of 8. Correct check: flag if the AC-CMB row is missing or PCS-04/PCS-05 connect to AC-BUS.

**-4 (negative)** — COMMS wired as a star: the connection list shows BMS units each connecting directly to SC-01 or to the PCS with no BMS-to-BMS chain links. Correct check: flag when BMS-to-BMS links are absent (a correct build has 3 BMS-to-BMS chain links per power block).

**-3 (negative)** — Aux over-fed (racks or BMS given an AUX-24V connection) or site-level items duplicated per power block. Correct check: flag either.

---

## Golden scores 100 against this rubric
The golden `bess_block_diagram.xlsx` has two diagram sheets plus an inventory and connection list per build. The inventories give 35 / 56 blocks and the connection-list summaries give all eight edge counts (15/5/16/7 and 25/8/26/11). The connection lists make the daisy-chain, the AC-CMB exception, the aux-feed restriction, and the single site-level items directly checkable. It commits none of the three negative failure modes.

## Metadata
- O*NET occupation: Electrical and Electronics Drafters (17-3012.00)
- O*NET tasks (verbatim):
  - Draft working drawings, wiring diagrams, wiring connection specifications, or cross-sections of underground cables, as required for instructions to installation crew.
  - Draft detail and assembly drawings of design components, circuitry or printed circuit boards, using computer-assisted equipment or standard drafting techniques and devices.
  - Draw master sketches to scale showing relation of proposed installations to existing facilities and exact specifications and dimensions.
  - Consult with engineers to discuss or interpret design concepts, or determine requirements of detailed working drawings.
- O*NET skills (from the Skills section, not Technology Skills): Reading Comprehension, Critical Thinking, Mathematics, Complex Problem Solving.
- Web search allowed: No (self-contained in the three files).
- Multimodal: Yes (the one-block wiring reference PDF alongside the two spec documents).
- Time estimate: 6 hours by hand (parse the taxonomy and interconnect rules, instantiate every block and harness for both builds, apply the AC-CMB exception, draft and format the two-sheet diagram with tagged colored connections).
