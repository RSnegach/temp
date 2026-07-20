# Closed-Loop Traverse Reduction (Parcel BLA-7) - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

I need the closing traverse on Parcel BLA-7 reduced and adjusted so I can set the deed area. The crew ran a closed five-station loop A-B-C-D-E back to A. Field notes are on the scanned book page (`fieldbook_reference.png`) and I also keyed the raw values into `traverse_field_data.xlsx` if that is easier to pull from.

Read the notes carefully, because the crew did not book everything in the same form. The A-to-B direction is a bearing off control monument MON-3, not an azimuth. Station C is written as a deflection angle turned right, not an interior angle, so convert it. And the C-to-D line was taped on a grade and recorded as a slope distance with its vertical angle, so reduce it to horizontal before you use it. Everything else is a normal interior angle or a horizontal distance.

Run it as a compass-rule (Bowditch) adjustment. Carry the loop clockwise using the interior angles (the deflection at C is turned to the right, consistent with a clockwise run), holding the fixed MON-3 bearing on A-to-B. Balance the angles first by distributing the angular misclosure equally, then carry adjusted azimuths around, compute latitudes and departures, get the linear misclosure and the precision ratio, apply the compass-rule corrections, and carry adjusted coordinates from A at N 1000.000, E 1000.000. Then give me the enclosed area.

Hand it back as `Traverse_BLA7_Reduction.xlsx`. Show the reduced directions and distances, the angular misclosure and per-angle correction, the per-course latitudes and departures, the linear closure and the precision ratio as 1:X, the Bowditch corrections, the adjusted coordinates of all five stations, and the area in square meters and hectares. Compute the latitudes, departures, corrections, coordinates, and area as live formulas off the field-data cells so it recomputes if a value is re-keyed.

---

## RUBRIC (weights in the numeric field only)

Each criterion is one atomic check. Derived values state their derivation from the field data.

Field reductions (recognize and convert the mixed conventions):
**+3** Station C is converted from the deflection angle 71-01-56 R to an interior angle of 108-58-04 (180 minus the deflection), not used as 71 degrees.
**+3** Course CD is reduced from the slope distance 195.37 m at a 5 degree vertical angle to a horizontal distance of 194.627 m (195.37 times cosine 5 degrees), not used as 195.37.
**+2** Course AB direction is taken as azimuth 64-07-45 from the bearing N 64-07-45 E, and held fixed.
**-3** The deflection angle at C is used directly as an interior angle, or the CD slope distance is used without reduction, either of which throws the closure and area off.

Angular closure:
**+3** The five interior angles sum to 540-00-26, giving an angular misclosure of +26 seconds against the required 540-00-00, corrected by -5.2 seconds per angle.
**+2** The adjusted interior angles sum to exactly 540-00-00.
**-2** The angular requirement is taken as something other than (n-2) times 180 = 540 degrees for the five-sided figure.

Azimuths and lat/dep:
**+3** Adjusted azimuths are carried around the loop from the fixed AB azimuth through the adjusted angles, and the carried azimuth returns to 64-07-45 on closing.
**+3** Latitudes and departures use the adjusted azimuths: lat = distance times cosine(azimuth), dep = distance times sine(azimuth); AB is +87.160 lat, +179.731 dep.
**-2** Latitudes and departures are computed from the raw (unadjusted) azimuths or with lat and dep swapped.

Linear closure and precision:
**+3** Linear misclosure is 0.159 m, from sum of latitudes +0.159 and sum of departures near zero; closure = sqrt(sumLat squared + sumDep squared).
**+2** Precision ratio is 1:5696, computed as perimeter (903.397 m) divided by the linear closure and rounded.
**-2** Precision is stated as closure over perimeter (inverted), or the perimeter is taken as something other than the sum of the five horizontal distances.

Bowditch adjustment, coordinates, area:
**+3** Compass-rule corrections are distance-weighted: correction to each latitude = -sumLat times (course distance / perimeter), same for departures; the adjusted latitudes and departures each sum to zero.
**+3** Adjusted coordinates carry from A (1000.000, 1000.000) and close back exactly on A; B is (1087.125, 1179.731).
**+3** Enclosed area is 55,593 m2 (5.5593 ha) by the coordinate (shoelace) method on the adjusted coordinates.
**+2** Latitudes, departures, corrections, coordinates, and area are live formulas off the field-data cells, not static typed numbers.
**-3** The corrections are applied equally to every course instead of weighted by distance, so the coordinates and area drift.

---

## Golden scores 100 against this rubric
The golden `Traverse_BLA7_Reduction.xlsx` reduces the deflection angle and slope distance, holds the AB bearing, balances +26 seconds of angular misclosure, carries adjusted azimuths, computes lat/dep, finds a 0.159 m linear closure (1:5696), applies distance-weighted Bowditch corrections that zero the latitude and departure sums, closes the coordinates on A, and returns an area of 55,593 m2 (5.5593 ha), all as live formulas.

## Metadata
- O*NET occupation: Surveyors (17-1022.00)
- O*NET tasks (verbatim from O*NET):
  - Direct or conduct surveys to establish legal boundaries for properties, based on legal deeds and titles.
  - Compute geodetic measurements and interpret survey data to determine positions, shapes, and elevations of geomorphic and topographic features.
  - Calculate heights, depths, relative positions, property lines, and other characteristics of terrain.
  - Prepare and maintain sketches, maps, reports, and legal descriptions of surveys to describe, certify, and assume liability for work performed.
- O*NET skills (Skills section): Mathematics, Critical Thinking, Reading Comprehension, Active Listening.
- Web search allowed: No (self-contained).
- Multimodal: Yes (a scanned field-book page must be read; a keyed data sheet is also provided).
- Time estimate: 5 to 6 hours by hand (recognize and reduce the mixed booking conventions, balance the angles, carry azimuths, compute and adjust latitudes and departures, coordinate and area, and build the workbook with live formulas).
