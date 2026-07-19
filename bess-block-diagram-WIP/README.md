# BESS Block Diagram Synthesis (WORK IN PROGRESS - INCOMPLETE)

> This project was abandoned mid-build when the assigned occupation changed. It
> is kept for the topology engine and render work, not as a finished task. There
> is no golden solution, no rubric, and no prompt. Do not treat it as complete.

## Intended task

Synthesize a two-configuration block diagram of a battery energy storage system
(BESS) in Excel, purely from verbal specifications plus a partial hand sketch of
one repeating unit. Version A = standard build (3 power blocks), Version B =
extended build (5 power blocks). No input file was to contain the full diagram;
the solver instantiates the harness connection rules across every block and
generalizes the one-block sketch to the whole system at both scales.

## What exists here

| Path | What it is | State |
|------|------------|-------|
| `inputs/BX-SE-TAX-014_Block_Taxonomy.docx` | Block-type taxonomy: functions, tags, ports, quantities | Drafted |
| `inputs/BX-SE-ICD-021_Interconnect_Harness_Schedule.docx` | Harness families and connection rules | Drafted |
| `scripts/topology.py` | Deterministic block+edge generator for both configs | Working |
| `scripts/render_bess.py` | Grid-art diagram renderer (PIL + xlsx model) | Partial |
| `scripts/build_doc1.py`, `build_doc2.py` | Generators for the two input docs | Working |
| `previews/preview_standard.png`, `preview_extended.png` | Rendered draft diagrams (3- and 5-block) | Draft |

## What is missing

- No hand-drawn one-block sketch input
- No golden `bess_block_diagram.xlsx` deliverable
- No prompt or rubric
- Render engine not finalized (label collisions, xlsx emitter incomplete)

## Locked topology (from `scripts/topology.py`)

Standard (3 blocks): 35 blocks, 43 harness edges.
Extended (5 blocks): 56 blocks, 70 edges, adds an AC combiner panel. AC power
does not scale linearly: blocks 1-3 feed the bus directly, blocks 4-5 aggregate
through the combiner.

Run `python scripts/topology.py` to print the block and edge inventory.
