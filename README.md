# Task Design Portfolio

Professional-workflow task packages, one folder per project. Each complete task
provides input files, a golden solution, a scoring rubric, and the deterministic
generator scripts that produce them.

## Projects

| Folder | Occupation | Task | Status |
|--------|------------|------|--------|
| [`software-qa-loanprequal/`](software-qa-loanprequal/) | Software QA Analysts & Testers | Derive a functional test suite for a loan pre-qualification decision service (EP, BVA, decision-table, decision-flow path coverage) | Complete |
| [`semiconductor-wafer-uniformity/`](semiconductor-wafer-uniformity/) | Semiconductor Processing Technicians | Compute wafer-map sheet-resistance uniformity, yield, and lot disposition from a 25-wafer, 49-site metrology export | Complete |
| [`bess-block-diagram/`](bess-block-diagram/) | Electrical and Electronics Drafters | Synthesize a two-configuration BESS block diagram in Excel from verbal specs and a one-block wiring reference | Complete |
| [`automotive-dfmea/`](automotive-dfmea/) | Automotive Engineers | Score and rank a fuel-delivery Design FMEA by AIAG-VDA Action Priority from a ratings reference and a working failure-mode register | Complete |
| [`gdt-mrb-disposition/`](gdt-mrb-disposition/) | Automotive Engineers | Disposition a machined bracket first article (ACCEPT / MRB / reject) from a GD&T drawing, a CMM report, and a disposition procedure, applying MMC bonus, datum shift, and a size-first rule | Complete |

## Layout of a project folder

```
<project>/
  README.md              project overview, the analytical spine, key numbers
  PROMPT_AND_RUBRIC.md    the prompt, scoring rubric, and O*NET metadata
  inputs/                 input files handed to the solver
  golden/                 the golden solution deliverable
  scripts/                deterministic generators (source of truth for all numbers)
  previews/               PNG renders of any hand-drawn or visual artifact
  *.zip                   packaged input and golden bundles
```

Each project's `scripts/` folder contains a single engine module that computes
every number in the golden; the golden is generated from it, so the two always
agree. Run the engine module directly to print the locked figures.

## Note on hand-drawn inputs

Some tasks include a hand-drawn input (a decision-flow graph, a wafer map). The
repo ships a clean reference render under `previews/`; the final submission uses
a redrawn, photographed version in place of the reference.
