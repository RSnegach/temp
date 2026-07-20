# Closed-Loop Traverse Reduction (ASME-free land survey, Bowditch)

**Occupation:** Surveyors (O*NET 17-1022.00), Professional/Scientific/Technical Services

## Task

Reduce and adjust a closed five-station boundary traverse from a field-book page, then set the parcel area. Recognize and convert the crew's mixed booking conventions (a bearing, a deflection angle, a slope distance), balance the angular misclosure, carry azimuths, compute and compass-rule-adjust latitudes and departures, coordinate the stations, and compute the enclosed area.

## Analytical spine

Geometric closure and coordinate geometry: direction propagation around a loop, distance-weighted (Bowditch) error distribution, and shoelace area. Distinct from the other portfolio spines. The golden is a live-formula workbook so it grades deterministically.

## Files

| Path | What it is |
|------|------------|
| `inputs/fieldbook_reference.png` | Scanned field-book page (raw booked values, mixed conventions) |
| `inputs/traverse_field_data.xlsx` | The same raw values keyed into a sheet (as-booked, not reduced) |
| `golden/Traverse_BLA7_Reduction.xlsx` | Golden reduction: live-formula closure, Bowditch, coordinates, area |
| `scripts/traverse.py` | Instance + reduction + adjustment engine (source of truth) |
| `scripts/render_fieldbook.py` | Field-book page generator |
| `scripts/make_fielddata.py`, `build_golden.py` | Input and golden generators |
| `scripts/xlsx_live.py` | Live-formula cache injection, decimal normalization, fingerprint scrub |
| `PROMPT_AND_RUBRIC.md` | Prompt, atomic rubric, metadata |

## Key figures (golden)

Angular misclosure +26 seconds (corrected -5.2 per angle). Linear closure 0.159 m, precision 1:5696. Adjusted coordinates close on A. Area 55,593 m2 (5.5593 ha).

## Why it is hard (a human 5 to 6 hour task)

The difficulty is in the reduction before the arithmetic: the crew booked the AB line as a bearing, station C as a deflection angle (interior = 180 - deflection), and course CD as a slope distance needing cosine reduction. Miss any conversion and the closure and area are wrong. The Bowditch corrections are distance-weighted, not equal, and latitudes/departures must use the adjusted azimuths.

Reproduce: `python scripts/traverse.py` prints the closure, adjusted azimuths, coordinates, and area.

## Note

`inputs/fieldbook_reference.png` is a clean reference render of the hand-drawn field-book page. The final submission uses a photographed redraw in its place.
