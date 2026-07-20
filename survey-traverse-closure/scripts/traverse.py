"""
Single source of truth for the closed-loop traverse task (land surveying).

A field crew runs a closed polygon traverse: at each station they measure an
interior angle, and along each course a bearing/azimuth and a horizontal
distance. The surveyor must:

  1. Angular closure: sum the measured interior angles, compare to the geometric
     requirement (n-2)*180, distribute the angular misclosure equally, and get
     adjusted azimuths for each course.
  2. Latitudes and departures: lat = dist*cos(az), dep = dist*sin(az) for each
     course, from the ADJUSTED azimuths.
  3. Linear misclosure: sum of latitudes and sum of departures should be zero;
     the residuals are the closure in latitude/departure. Linear closure =
     sqrt(sum_lat^2 + sum_dep^2). Precision ratio = perimeter / closure, stated
     1:round(ratio).
  4. Bowditch (compass) rule adjustment: correction to each course's latitude =
     -sum_lat * (course_dist / perimeter); same for departure. Apply to get
     adjusted lats/deps that sum to zero.
  5. Adjusted coordinates: accumulate adjusted lats/deps from a start point.
  6. Area by coordinate method (shoelace) from adjusted coordinates.

Why this resists a one-shot answer: the azimuths must be propagated from a start
azimuth THROUGH the adjusted interior angles (a running direction computation
where one angle error cascades to every later course), the Bowditch corrections
are distance-weighted (not equal), and lat/dep use the ADJUSTED azimuths, not the
raw ones. Angle bearing conventions (interior angle to the right, azimuth carry-
forward = back-azimuth + interior angle) trip people up.

All numbers computed here so the golden ties out.
"""
import math

# ---------------- instance ----------------
# Closed 5-sided traverse, stations A B C D E, courses AB BC CD DE EA.
# Measured interior angles (at each station), in DMS (deg, min, sec).
INTERIOR_ANGLES = {
    "A": (98, 0, 18),
    "B": (104, 16, 21),
    "C": (108, 58, 4),      # reduced from the field book's deflection 71-01-56 R
    "D": (108, 51, 30),
    "E": (119, 54, 13),
}
# The five interior angles of a pentagon must sum to (5-2)*180 = 540 deg.
# These whole-second measured angles sum to 540 deg 00' 26", a +26" misclosure.
# (Station C is recorded in the field book as a deflection angle 71-01-56 R;
#  interior = 180 - deflection = 108-58-04.)

# Starting azimuth of the first course AB (fixed by control monument), in DMS.
# The field book records this as the quadrant bearing N 64-07-45 E.
AZ_AB_START = (64, 7, 45)

# course order and measured horizontal distances (m)
COURSES = ["AB", "BC", "CD", "DE", "EA"]
DISTANCES = {
    "AB": 199.75,
    "BC": 176.55,
    "CD": 194.627,   # reduced from slope 195.37 m at 5-00-00 vertical: 195.37*cos(5)
    "DE": 136.50,
    "EA": 195.97,
}
# station order around the loop
STATIONS = ["A", "B", "C", "D", "E"]
# starting coordinates of A
A_COORD = (1000.000, 1000.000)   # (N, E)

# ---------------- DMS helpers ----------------
def dms_to_deg(dms):
    d, m, s = dms
    return d + m/60 + s/3600

def deg_to_dms(deg):
    deg = deg % 360
    d = int(deg)
    mfull = (deg - d) * 60
    m = int(mfull)
    s = (mfull - m) * 60
    # clean rounding to 0.1"
    s = round(s, 1)
    if s >= 60:
        s -= 60; m += 1
    if m >= 60:
        m -= 60; d += 1
    return (d, m, s)

# ---------------- 1. angular closure ----------------
def angular_closure():
    total = sum(dms_to_deg(a) for a in INTERIOR_ANGLES.values())
    required = (len(INTERIOR_ANGLES) - 2) * 180
    misclosure_deg = total - required          # + means angles too large
    n = len(INTERIOR_ANGLES)
    corr_per_angle_deg = -misclosure_deg / n    # distributed equally
    adjusted = {k: dms_to_deg(v) + corr_per_angle_deg for k, v in INTERIOR_ANGLES.items()}
    return dict(total_deg=total, required=required,
                misclosure_sec=misclosure_deg*3600,
                corr_per_angle_sec=corr_per_angle_deg*3600,
                adjusted_deg=adjusted)

# ---------------- 2. azimuth propagation ----------------
def azimuths():
    """Propagate azimuths around the loop using adjusted interior angles.
    Convention: traverse runs A->B->C->D->E->A (counter-clockwise interior
    angles measured to the interior). Azimuth of next course =
    (azimuth of current course + 180 - interior angle at the turning station),
    reduced mod 360. Start with AZ_AB fixed."""
    ac = angular_closure()
    adj = ac["adjusted_deg"]
    az = {}
    az["AB"] = dms_to_deg(AZ_AB_START)
    # turning station between course i and i+1 is the shared station
    # AB -> BC turns at B, BC->CD at C, CD->DE at D, DE->EA at E, EA->AB at A
    turn = {"BC": "B", "CD": "C", "DE": "D", "EA": "E"}
    seq = ["AB", "BC", "CD", "DE", "EA"]
    for i in range(1, len(seq)):
        prev = seq[i-1]; cur = seq[i]; st = turn[cur]
        az[cur] = (az[prev] + 180 - adj[st]) % 360
    return az

# ---------------- 3. lat/dep + linear closure ----------------
def lat_dep_raw():
    az = azimuths()
    rows = {}
    for c in COURSES:
        a = math.radians(az[c]); d = DISTANCES[c]
        rows[c] = dict(az=az[c], dist=d, lat=d*math.cos(a), dep=d*math.sin(a))
    return rows

def linear_closure():
    rows = lat_dep_raw()
    sum_lat = sum(r["lat"] for r in rows.values())
    sum_dep = sum(r["dep"] for r in rows.values())
    perim = sum(DISTANCES.values())
    closure = math.sqrt(sum_lat**2 + sum_dep**2)
    ratio = perim / closure if closure else float("inf")
    return dict(sum_lat=sum_lat, sum_dep=sum_dep, perim=perim,
                closure=closure, ratio=ratio)

# ---------------- 4. Bowditch adjustment ----------------
def bowditch():
    rows = lat_dep_raw()
    lc = linear_closure()
    perim = lc["perim"]
    out = {}
    for c in COURSES:
        clat = -lc["sum_lat"] * (DISTANCES[c] / perim)
        cdep = -lc["sum_dep"] * (DISTANCES[c] / perim)
        out[c] = dict(lat=rows[c]["lat"], dep=rows[c]["dep"],
                      clat=clat, cdep=cdep,
                      adj_lat=rows[c]["lat"] + clat,
                      adj_dep=rows[c]["dep"] + cdep)
    return out

# ---------------- 5. adjusted coordinates ----------------
def coordinates():
    adj = bowditch()
    coords = {"A": A_COORD}
    seq = ["AB", "BC", "CD", "DE", "EA"]
    to_station = {"AB": "B", "BC": "C", "CD": "D", "DE": "E", "EA": "A"}
    n, e = A_COORD
    order = ["A", "B", "C", "D", "E"]
    cur = "A"
    for c in seq:
        nxt = to_station[c]
        n = coords[cur][0] + adj[c]["adj_lat"]
        e = coords[cur][1] + adj[c]["adj_dep"]
        if nxt != "A":
            coords[nxt] = (n, e)
        else:
            coords["A_check"] = (n, e)   # should return to A
        cur = nxt
    return coords

# ---------------- 6. area by coordinates ----------------
def area():
    coords = coordinates()
    pts = [coords[s] for s in STATIONS]     # (N, E)
    n = len(pts)
    s = 0.0
    for i in range(n):
        n1, e1 = pts[i]
        n2, e2 = pts[(i+1) % n]
        s += e1 * n2 - e2 * n1
    return abs(s) / 2.0

if __name__ == "__main__":
    ac = angular_closure()
    print("=== angular closure ===")
    print(f"sum interior = {ac['total_deg']:.6f} deg, required {ac['required']}")
    print(f"misclosure = {ac['misclosure_sec']:.1f}\", correction per angle = {ac['corr_per_angle_sec']:.1f}\"")
    az = azimuths()
    print("\n=== adjusted azimuths ===")
    for c in COURSES:
        print(f"  {c}: {az[c]:.6f} deg = {deg_to_dms(az[c])}")
    lc = linear_closure()
    print("\n=== linear closure ===")
    print(f"sum_lat = {lc['sum_lat']:.4f}, sum_dep = {lc['sum_dep']:.4f}")
    print(f"perimeter = {lc['perim']:.3f}, closure = {lc['closure']:.4f}")
    print(f"precision ratio = 1:{round(lc['ratio'])}")
    bw = bowditch()
    print("\n=== Bowditch adjusted lat/dep ===")
    tot_al = tot_ad = 0.0
    for c in COURSES:
        r = bw[c]; tot_al += r['adj_lat']; tot_ad += r['adj_dep']
        print(f"  {c}: lat {r['lat']:+.4f} clat {r['clat']:+.4f} -> {r['adj_lat']:+.4f} | "
              f"dep {r['dep']:+.4f} cdep {r['cdep']:+.4f} -> {r['adj_dep']:+.4f}")
    print(f"  sum adj_lat = {tot_al:.6f}, sum adj_dep = {tot_ad:.6f} (both ~0)")
    co = coordinates()
    print("\n=== adjusted coordinates (N, E) ===")
    for s in STATIONS:
        print(f"  {s}: ({co[s][0]:.4f}, {co[s][1]:.4f})")
    print(f"  A check: ({co['A_check'][0]:.4f}, {co['A_check'][1]:.4f})")
    print(f"\n=== area = {area():.3f} m^2 = {area()/10000:.4f} ha ===")
