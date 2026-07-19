# BESS Block Diagram Synthesis

**Occupation:** Electrical and Electronics Drafters (O*NET 17-3012.00), Professional Scientific and Technical Services sector

## Task

Draft a battery energy storage system (BESS) site block diagram in Excel from verbal specifications plus a one-block wiring reference. Two build scales: standard (3 power blocks) and extended (5 power blocks). No input file contains the full diagram. The solver instantiates the harness connection rules across every block and generalizes the one-block reference to the whole system at both scales.

## Analytical spine

Visual synthesis. The solver must build a full block/edge inventory from prose rules and one worked block, then render it as a tagged, colored block diagram. Distinct from a numeric solve, a combinatorial enumeration, or a statistical aggregation.

## Files

| Path | What it is |
|------|------------|
| `inputs/BX-SE-TAX-014_Block_Taxonomy.docx` | Block types, tag convention, per-block and per-site quantities |
| `inputs/BX-SE-ICD-021_Interconnect_Harness_Schedule.docx` | Four harness families and all connection rules |
| `inputs/BX-SE-SK-104_Power_Block_Wiring.pdf` | One-block wiring reference (used directly as an input) |
| `golden/bess_block_diagram.xlsx` | Golden: standard (3-block) and extended (5-block) diagrams, two sheets |
| `scripts/topology.py` | Deterministic block + edge generator (source of truth) |
| `scripts/render_bess.py` | Grid-art renderer (PNG preview + xlsx emitter) |
| `scripts/build_doc1.py`, `build_doc2.py`, `build_refpdf.py` | Input artifact generators |
| `PROMPT_AND_RUBRIC.md` | Prompt, 11-criterion rubric, metadata |

## Key figures (golden)

Standard build: 35 blocks, 43 harness edges (DC-PWR 15, AC-PWR 5, COMMS 16, AUX-24V 7).
Extended build: 56 blocks (adds an AC Combiner Panel), 70 edges (DC-PWR 25, AC-PWR 8, COMMS 26, AUX-24V 11).

The two hardest points, both verifiable: COMMS is an intra-block daisy chain (not a star to the controller), and AC power does not scale linearly. Blocks 1-3 feed the AC bus directly and blocks 4-5 aggregate through the combiner panel, so AC-PWR is 8 not 10 on the extended build.

Reproduce: `python scripts/topology.py` prints the full block and edge inventory for both builds.
