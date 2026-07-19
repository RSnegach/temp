# BESS Block Diagram - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

We're putting the block diagram package together for the containerized BESS platform and I need you to draft the site single-line as a block diagram in Excel. We quote this platform in two build sizes and I need both drawn: the standard 3 power-block build and the extended 5 power-block build.

I can't hand you a marked-up drawing because that's exactly what I need produced. What I can give you is the block taxonomy (`BX-SE-TAX-014_Block_Taxonomy.docx`), which lists every block type, its tag convention, and how many of each go per power block and per site, and the interconnect schedule (`BX-SE-ICD-021_Interconnect_Harness_Schedule.docx`), which defines the four harness families and the rules for how everything wires together. There's also a one-block wiring reference (`BX-SE-SK-104_Power_Block_Wiring.pdf`) so you can see how a single power block is wired internally and where it ties up to the site section. That reference shows one block only. You need to replicate that pattern for every power block in each build and wire the shared site section per the schedule.

Watch the interconnect schedule carefully on two things. The comms inside a block is a daisy chain, not a home run to the controller. And the AC collection on the larger build does not just scale up one for one, there's a rule about the bus feeder count that changes how the upper blocks reach the bus. Read it and apply it.

Give it back as `bess_block_diagram.xlsx` with the standard build on one sheet and the extended build on another. Draw each block as a labeled box, each connection as a line tagged and colored by its harness family, and add the harness color key. I want to be able to count blocks and trace every harness from this drawing.

---

## RUBRIC (weights in the numeric field only)

**+5 (critical)** — Standard build has the correct block inventory: 35 blocks total (1 each of Site Controller, Aux Transformer, MV Step-up Transformer, Revenue Metering, AC Collection Bus, plus 3 PCS, 3 DC Combiner, 12 Battery Rack, 12 Rack BMS), no AC Combiner Panel. Correct check: 35 blocks with that type breakdown.

**+5 (critical)** — Extended build applies the AC bus-feeder exception: 56 blocks including 1 AC Combiner Panel (AC-CMB); power blocks 1-3 feed the AC bus directly and blocks 4-5 feed the AC-CMB, which makes one feeder to the bus. Correct check: AC-CMB present, PCS-04 and PCS-05 connect to AC-CMB not the bus, AC-CMB connects to AC-BUS. A linear 5/3 scale-up (no AC-CMB, all 5 PCS on the bus) is wrong.

**+4 (critical)** — COMMS is a daisy chain within each power block: the K Rack BMS units chain BMS-n-1 to BMS-n-2 to ... to BMS-n-4, the head BMS-n-1 connects to that block's PCS, and each PCS home-runs to the Site Controller. Correct check: BMS units are chained, not each wired to the controller. A star of all BMS to the controller is wrong.

**+4 (critical)** — Harness edge counts are correct per build. Standard: DC-PWR 15, AC-PWR 5, COMMS 16, AUX-24V 7 (43 total). Extended: DC-PWR 25, AC-PWR 8, COMMS 26, AUX-24V 11 (70 total). Correct check: these eight counts.

**+3 (important)** — DC-PWR is wired within each block only: each Battery Rack home-runs to its block's DC Combiner (star of 4), and each DC Combiner feeds its block's PCS. Per block that is 5 DC links. Correct check: rack-to-DCC star plus DCC-to-PCS, no DC crossing between blocks or to the site.

**+3 (important)** — AUX-24V feeds only the active equipment: the Aux Transformer feeds each PCS and each DC Combiner (2 per block) and the Site Controller (1 site-level). Correct check: racks and BMS are NOT aux-fed, AC bus/metering/MV transformer/AC-CMB are NOT aux-fed.

**+3 (important)** — Site-level blocks and links exist once, not per power block: one AC-BUS, one Metering, one MV-XFMR, with AC-BUS to Metering to MV-XFMR, Metering home-runs COMMS to the Site Controller, and Aux Transformer feeds the Site Controller. Correct check: these are single site-level items, not duplicated per block.

**+3 (important)** — Naming and indexing are consistent across both builds: PCS-0n and DCC-0n by block, RK-n-k and BMS-n-k by block then position (e.g. RK-3-2, BMS-5-4). Correct check: tags follow this scheme with no off-by-one.

**+2 (minor)** — Both builds are on separate sheets, each block is a labeled box, each connection is a line colored and tagged by harness family (DC-PWR red, AC-PWR black, COMMS blue, AUX-24V green), and a harness color key is present. Correct check: two sheets, colored tagged lines, legend.

**-5 (negative)** — Extended build drawn as a linear scale-up: no AC Combiner Panel and all 5 PCS landed on the AC bus directly, giving AC-PWR 10 instead of 8. Correct check: flag if AC-CMB missing or PCS-04/05 wired to the bus.

**-4 (negative)** — COMMS drawn as a star (every BMS wired to the Site Controller or to the PCS) instead of an intra-block daisy chain. Correct check: flag if BMS units are not chained.

**-3 (negative)** — Aux over-fed (racks or BMS given an AUX-24V connection) or site-level items duplicated per power block. Correct check: flag either.

---

## Golden scores 100 against this rubric
The golden `bess_block_diagram.xlsx` reproduces both inventories (35 / 56 blocks) and all eight edge counts (15/5/16/7 and 25/8/26/11), applies the AC-CMB exception, draws the comms daisy chain, restricts aux feeds, keeps site items singular, and names everything consistently. It commits none of the three negative failure modes.

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
