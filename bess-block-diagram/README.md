# BESS Block Diagram Synthesis

**Occupation:** Electrical and Electronics Drafters (O*NET 17-3012.00), Professional Scientific and Technical Services sector

## Task

Draft a battery energy storage system (BESS) site block diagram in Excel from verbal specifications plus a one-block wiring reference. Two build scales: standard (3 power blocks) and extended (5 power blocks). No input file contains the full diagram. The solver instantiates the harness connection rules across every block and generalizes the one-block reference to the whole system at both scales.

## Analytical spine

Visual synthesis. The solver must recover the one-block wiring grammar from a hand-drawn field sketch, build a full block/edge inventory from that plus prose rules, then render it as a tagged, colored block diagram at two scales. Distinct from a numeric solve, a combinatorial enumeration, or a statistical aggregation. The wiring reference is a scanned pen-and-paper sketch, not a clean drawing, so the internal grammar has to be read off a hand image before anything can be instantiated.

## Files

| Path | What it is |
|------|------------|
| `inputs/BX-SE-TAX-014_Block_Taxonomy.docx` | Block types, tag convention, per-block and per-site quantities |
| `inputs/BX-SE-ICD-021_Interconnect_Harness_Schedule.docx` | Four harness families and all connection rules |
| `inputs/BX-SE-SK-104_Power_Block_Wiring.pdf` | Hand-drawn one-block wiring sketch (scanned; the only picture of the wiring) |
| `golden/bess_block_diagram.xlsx` | Golden: standard (3-block) and extended (5-block) diagrams, two sheets |
| `scripts/topology.py` | Deterministic block + edge generator (source of truth) |
| `scripts/render_bess.py` | Grid-art renderer (PNG preview + xlsx emitter) |
| `scripts/build_doc1.py`, `build_doc2.py` | Spec-document generators |
| `scripts/render_sketch.py` | Hand-drawn one-block wiring sketch generator (emits the PDF input + a preview) |
| `previews/refsketch_preview.png` | Reference render of the hand-drawn sketch |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomized rubric, metadata |

## Key figures (golden)

Standard build: 35 blocks, 43 harness edges (DC-PWR 15, AC-PWR 5, COMMS 16, AUX-24V 7).
Extended build: 56 blocks (adds an AC Combiner Panel), 70 edges (DC-PWR 25, AC-PWR 8, COMMS 26, AUX-24V 11).

Three hard points, all verifiable. First, the one-block wiring grammar has to be read off a hand-drawn sketch (no clean drawing is provided), and a misread there repeats across every block. Second, COMMS is an intra-block daisy chain (not a star to the controller), with only the head BMS reaching the PCS. Third, AC power does not scale linearly: blocks 1-3 feed the AC bus directly and blocks 4-5 aggregate through the combiner panel, so AC-PWR is 8 not 10 on the extended build.

Reproduce: `python scripts/topology.py` prints the full block and edge inventory for both builds. `python scripts/render_sketch.py` regenerates the hand-drawn reference PDF and its preview.

## Note on the hand-drawn input

`inputs/BX-SE-SK-104_Power_Block_Wiring.pdf` and `previews/refsketch_preview.png` are a clean reference render of the hand-drawn one-block sketch. The final submission uses a photographed pen-and-paper redraw of the same wiring in its place.
