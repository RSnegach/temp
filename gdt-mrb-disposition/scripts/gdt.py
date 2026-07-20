"""
Single source of truth for the GD&T inspection-disposition (MRB) task.

An automotive machined bracket is inspected on a CMM. For every feature the
engineer must:
  1. Size check: is the actual local size within the size limits? (size governs
     first: an out-of-size feature is dispositioned on size, position is moot.)
  2. Bonus tolerance: when the position tolerance carries an MMC modifier, extra
     positional tolerance equal to the feature's departure from MMC is allowed.
        internal feature (hole): departs as it gets LARGER  -> bonus = actual - MMC
        external feature (pin):  departs as it gets SMALLER -> bonus = MMC - actual
     RFS (no modifier) grants NO bonus even though size departs.
  3. Datum shift: when a datum feature of size is referenced at MMC in the frame,
     the datum feature's own departure from its MMC adds an additional shift
     allowance to features controlled to that datum.
  4. Total allowed positional tolerance = stated tol + bonus + datum shift.
  5. Actual positional deviation (diameter) = 2 * sqrt(dx^2 + dy^2).
  6. Virtual condition (mating boundary):
        internal: VC = MMC - stated_geo_tol
        external: VC = MMC + stated_geo_tol
  7. Disposition:
        size out of limits            -> REJECT (size)
        position <= total allowed      -> ACCEPT
        position > total allowed       -> MRB (submit for material review)
     Non-size geometric callouts (profile, flatness) get NO bonus; a profile
     value is compared directly to its tol.

The register mixes conventions and includes red-herring/ trap features. This is
computed here so the golden ties out exactly.
"""
import math

# ------------------------------------------------------------------ datum sizes
# Datum features of size and their measured actual local size. MMC given.
# Datum B is an internal datum hole; departure = actual - MMC.
DATUMS = {
    "B": dict(type="internal", mmc=10.00, lmc=10.06, actual=10.04),  # departs 0.04
    "C": dict(type="internal", mmc=6.00,  lmc=6.05,  actual=6.00),   # at MMC, no shift
}
def datum_shift(name):
    d = DATUMS[name]
    if d["type"] == "internal":
        return round(d["actual"] - d["mmc"], 4)
    return round(d["mmc"] - d["actual"], 4)

# ------------------------------------------------------------------ features
# Each feature:
#   id, kind: 'hole'(internal FOS) | 'pin'(external FOS) | 'profile' | 'flatness'
#   size_mmc, size_lmc : material limits (for FOS)
#   char : 'position' | 'profile' | 'flatness'
#   geo_tol : stated tolerance value (diameter zone for position)
#   modifier : 'MMC' | 'RFS' | None   (position modifier)
#   datum_at_mmc : name of a datum-of-size referenced at MMC in the frame, or None
#   meas_size, dx, dy : CMM results (dx,dy = center offset from true position)
#   prof_dev : measured profile/flatness deviation (for non-FOS callouts)
FEATURES = [
    # ---- 4-hole mounting pattern, position at MMC to A|B(M)|C ----
    # H1: mid-size, comfortable pass with bonus.
    dict(id="H1", kind="hole", size_mmc=8.00, size_lmc=8.10, char="position",
         geo_tol=0.20, modifier="MMC", datum_at_mmc="B",
         meas_size=8.05, dx=0.060, dy=0.050),
    # H2: exactly at MMC (no bonus); datum shift from B still applies; borderline.
    dict(id="H2", kind="hole", size_mmc=8.00, size_lmc=8.10, char="position",
         geo_tol=0.20, modifier="MMC", datum_at_mmc="B",
         meas_size=8.00, dx=0.090, dy=0.060),
    # H3: at LMC (full 0.10 bonus) + datum shift 0.04; actual 0.320 exceeds the
    #     stated 0.20 AND the bonus-only 0.30, but bonus+shift total 0.34 rescues
    #     it -> ACCEPT. Discriminator: naive or bonus-only handling wrongly MRBs.
    dict(id="H3", kind="hole", size_mmc=8.00, size_lmc=8.10, char="position",
         geo_tol=0.20, modifier="MMC", datum_at_mmc="B",
         meas_size=8.10, dx=0.130, dy=0.093),
    # H4: small bonus only; deviation beats even bonus+shift -> MRB.
    dict(id="H4", kind="hole", size_mmc=8.00, size_lmc=8.10, char="position",
         geo_tol=0.20, modifier="MMC", datum_at_mmc="B",
         meas_size=8.02, dx=0.150, dy=0.110),
    # ---- dowel pin, EXTERNAL, position at MMC (bonus direction flips) ----
    # P1: pin under MMC gives bonus = MMC - actual; rescues a >stated deviation.
    dict(id="P1", kind="pin", size_mmc=12.00, size_lmc=11.90, char="position",
         geo_tol=0.15, modifier="MMC", datum_at_mmc=None,
         meas_size=11.93, dx=0.080, dy=0.070),
    # ---- precision bore, position RFS: NO bonus even though size departs ----
    # R1: size departs a lot but RFS grants nothing; deviation > stated -> MRB.
    dict(id="R1", kind="hole", size_mmc=20.00, size_lmc=20.08, char="position",
         geo_tol=0.10, modifier="RFS", datum_at_mmc=None,
         meas_size=20.07, dx=0.050, dy=0.045),
    # ---- size-reject trap: hole over the LMC limit; position is moot ----
    dict(id="H5", kind="hole", size_mmc=5.00, size_lmc=5.06, char="position",
         geo_tol=0.25, modifier="MMC", datum_at_mmc=None,
         meas_size=5.09, dx=0.020, dy=0.020),
    # ---- profile red herring: NOT a feature of size, no bonus, direct compare ----
    dict(id="S1", kind="profile", char="profile", geo_tol=0.30, modifier=None,
         prof_dev=0.24),
    # ---- flatness red herring: passes, no bonus concept ----
    dict(id="F1", kind="flatness", char="flatness", geo_tol=0.05, modifier=None,
         prof_dev=0.038),
]

def actual_dia_dev(dx, dy):
    return round(2.0 * math.sqrt(dx * dx + dy * dy), 4)

def bonus(f):
    if f["char"] != "position" or f["modifier"] != "MMC":
        return 0.0
    if f["kind"] == "hole":          # internal: bonus as it enlarges
        return round(f["meas_size"] - f["size_mmc"], 4)
    if f["kind"] == "pin":           # external: bonus as it shrinks
        return round(f["size_mmc"] - f["meas_size"], 4)
    return 0.0

def virtual_condition(f):
    if f["char"] != "position":
        return None
    if f["kind"] == "hole":
        return round(f["size_mmc"] - f["geo_tol"], 4)
    if f["kind"] == "pin":
        return round(f["size_mmc"] + f["geo_tol"], 4)
    return None

def size_ok(f):
    if f["char"] not in ("position",) or f["kind"] not in ("hole", "pin"):
        return True
    lo, hi = sorted((f["size_mmc"], f["size_lmc"]))
    return lo <= f["meas_size"] <= hi

def evaluate():
    rows = []
    for f in FEATURES:
        rec = dict(id=f["id"], kind=f["kind"], char=f["char"])
        if f["char"] != "position":
            # profile / flatness: direct comparison, no bonus, no VC
            dev = f["prof_dev"]
            rec.update(stated=f["geo_tol"], bonus=0.0, shift=0.0,
                       total=f["geo_tol"], actual=dev, vc=None, size_ok=True,
                       disp="ACCEPT" if dev <= f["geo_tol"] else "MRB")
            rows.append(rec); continue

        b = bonus(f)
        sh = datum_shift(f["datum_at_mmc"]) if f["datum_at_mmc"] else 0.0
        total = round(f["geo_tol"] + b + sh, 4)
        act = actual_dia_dev(f["dx"], f["dy"])
        vc = virtual_condition(f)
        sok = size_ok(f)
        if not sok:
            disp = "REJECT (size)"
        elif act <= total:
            disp = "ACCEPT"
        else:
            disp = "MRB"
        rec.update(size=f["meas_size"], stated=f["geo_tol"], modifier=f["modifier"],
                   bonus=b, shift=sh, total=total, actual=act, vc=vc,
                   size_ok=sok, disp=disp)
        rows.append(rec)
    return rows

if __name__ == "__main__":
    from collections import Counter
    rows = evaluate()
    print("datum shifts:", {k: datum_shift(k) for k in DATUMS})
    hdr = f"{'id':>3} {'kind':>8} {'char':>9} {'size':>7} {'mod':>4} {'stated':>7} {'bonus':>6} {'shift':>6} {'total':>7} {'actual':>7} {'VC':>7} {'disp':>14}"
    print(hdr)
    for r in rows:
        print(f"{r['id']:>3} {r['kind']:>8} {r['char']:>9} "
              f"{r.get('size',''):>7} {r.get('modifier',''):>4} "
              f"{r['stated']:>7.3f} {r['bonus']:>6.3f} {r['shift']:>6.3f} "
              f"{r['total']:>7.3f} {r['actual']:>7.3f} "
              f"{(r['vc'] if r['vc'] is not None else ''):>7} {r['disp']:>14}")
    print("\ndisposition counts:", dict(Counter(r['disp'] for r in rows)))
