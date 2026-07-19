"""
Single source of truth for the wafer-map yield & uniformity task.

System: a 25-wafer lot measured for sheet resistance (Rs, ohm/sq) on a 49-site
polar map after implant/anneal. The technician must compute within-wafer
nonuniformity, wafer-to-wafer variation, and bin yield, then disposition the lot.

Deterministic by construction:
  - 49-site polar layout (center + 4 rings) with fixed X/Y coordinates.
  - Rs generated from a radial signature (edge-fast anneal) + per-wafer offset +
    seeded pseudo-noise. No unseeded randomness, so every run is identical.
  - A fixed set of retest duplicates is injected (original + later-timestamp
    retest); only the retest counts.
  - Edge exclusion: 150 mm wafer (R = 75 mm), 3 mm edge exclusion -> any site
    with radius > 72.0 mm is excluded from all statistics.
  - Pinned nonuniformity definition: WIW nonuniformity % = (max - min) /
    (2 * mean) * 100 over included sites. (The 1-sigma/mean definition is the
    plausible-wrong alternative and is NOT used.)

Running this file prints every locked number used by the golden and rubric.
"""
import math, random

# ---- wafer / sampling geometry ----
WAFER_RADIUS_MM = 75.0          # 150 mm wafer
EDGE_EXCLUSION_MM = 3.0
EXCL_RADIUS = WAFER_RADIUS_MM - EDGE_EXCLUSION_MM   # 72.0 -> r > 72.0 excluded
N_WAFERS = 25

# ---- Rs spec (process spec doc) ----
RS_TARGET = 85.0
RS_TOL_PCT = 5.0                # +/- 5 %
RS_LSL = RS_TARGET * (1 - RS_TOL_PCT/100)   # 80.75
RS_USL = RS_TARGET * (1 + RS_TOL_PCT/100)   # 89.25
# bins (warn band = within spec but outside +/-3 %)
RS_WARN_LO = RS_TARGET * (1 - 3/100)        # 82.45
RS_WARN_HI = RS_TARGET * (1 + 3/100)        # 87.55

# ---- 49-site polar layout: (ring_radius_mm, n_sites, angle_offset_deg) ----
RINGS = [
    (0.0,   1, 0.0),
    (22.0,  8, 0.0),
    (40.0, 12, 15.0),
    (58.0, 12, 0.0),
    (73.0, 16, 11.25),   # outer ring: r=73 > 72 -> edge-excluded
]

def build_sites():
    """Return list of dict(site, x, y, r, ring, excluded) with 49 fixed sites."""
    sites = []
    sid = 1
    for ring_idx, (r, n, off) in enumerate(RINGS):
        for k in range(n):
            if n == 1:
                x, y = 0.0, 0.0
            else:
                ang = math.radians(off + k * 360.0 / n)
                x = r * math.cos(ang)
                y = r * math.sin(ang)
            rr = math.sqrt(x*x + y*y)
            sites.append(dict(site=sid, x=round(x,2), y=round(y,2), r=round(rr,2),
                              ring=ring_idx, excluded=(rr > EXCL_RADIUS)))
            sid += 1
    return sites

SITES = build_sites()
N_SITES = len(SITES)                 # 49
INCLUDED = [s for s in SITES if not s["excluded"]]
EXCLUDED = [s for s in SITES if s["excluded"]]

# ---- deterministic Rs generation ----
def _rng(seed):
    r = random.Random(seed)
    return r

def rs_value(site, wafer, wafer_offset):
    """Radial signature (edge-fast) + per-wafer offset + seeded noise."""
    r = _rng(hash((site["site"], wafer)) & 0xffffffff)
    radial = 10.0 * (site["r"] / WAFER_RADIUS_MM) ** 2   # 0 at center, ~9.5 at edge
    noise = (r.random() - 0.5) * 1.6                     # +/-0.8 seeded
    base = 82.0
    return round(base + radial + wafer_offset + noise, 2)

# per-wafer mean offset (deterministic sequence, small W2W spread)
def wafer_offset(w):
    rr = _rng(1000 + w)
    return round((rr.random() - 0.4) * 3.4, 2)           # roughly -1.4 .. +2.0

# ---- retest duplicates (fixed injections): (wafer, site, original_value) ----
# original reading is off; a later-timestamp retest supersedes it.
RETESTS = [
    (3, 15),   # (wafer, site) that got remeasured; all on INCLUDED sites so
    (7, 28),   # each retest changes a computed statistic
    (12, 5),
    (19, 33),
    (22, 20),
]

def measured_rows():
    """Full measurement table incl. retest duplicates. Each row:
    dict(wafer, site, x, y, r, rs, timestamp_min, is_retest)."""
    rows = []
    site_by_id = {s["site"]: s for s in SITES}
    for w in range(1, N_WAFERS+1):
        off = wafer_offset(w)
        base_ts = w * 10000
        for s in SITES:
            rs = rs_value(s, w, off)
            ts = base_ts + s["site"]     # ascending within wafer
            rows.append(dict(wafer=w, site=s["site"], x=s["x"], y=s["y"], r=s["r"],
                             rs=rs, ts=ts, is_retest=False))
    # inject retests: original (earlier ts, perturbed value) + retest (later ts, the true value)
    # We mark the ALREADY-present row as the retest (true) and add an ORIGINAL earlier bad row.
    row_index = {(r["wafer"], r["site"]): r for r in rows}
    added = []
    for (w, sid) in RETESTS:
        true_row = row_index[(w, sid)]
        true_row["is_retest"] = True
        true_row["ts"] = w*10000 + 5000 + sid      # later timestamp
        # original: earlier ts, a clearly different (bad) reading
        bad = round(true_row["rs"] + 6.5, 2)        # original read high, then remeasured
        added.append(dict(wafer=w, site=sid, x=true_row["x"], y=true_row["y"], r=true_row["r"],
                          rs=bad, ts=w*10000 + sid, is_retest=False))
    rows.extend(added)
    return rows

def dedup(rows):
    """Keep only the latest-timestamp row per (wafer, site)."""
    best = {}
    for r in rows:
        key = (r["wafer"], r["site"])
        if key not in best or r["ts"] > best[key]["ts"]:
            best[key] = r
    return list(best.values())

# ---- statistics ----
def bin_of(rs):
    if rs < RS_LSL or rs > RS_USL: return "FAIL"
    if rs < RS_WARN_LO or rs > RS_WARN_HI: return "WARN"
    return "PASS"

def wafer_stats(w, deduped):
    """Included-site stats for one wafer."""
    vals = [r["rs"] for r in deduped if r["wafer"] == w and not _excluded(r["site"])]
    n = len(vals)
    mean = sum(vals)/n
    mn, mx = min(vals), max(vals)
    wiw = (mx - mn) / (2*mean) * 100.0
    sigma = (sum((v-mean)**2 for v in vals)/(n-1)) ** 0.5
    npass = sum(1 for v in vals if RS_LSL <= v <= RS_USL)
    return dict(wafer=w, n=n, mean=mean, min=mn, max=mx, wiw=wiw, sigma=sigma,
                yield_pct=npass/n*100.0, n_fail=n-npass)

_excl_ids = {s["site"] for s in EXCLUDED}
def _excluded(site_id): return site_id in _excl_ids

def lot_stats(deduped):
    ws = [wafer_stats(w, deduped) for w in range(1, N_WAFERS+1)]
    wmeans = [x["mean"] for x in ws]
    lot_mean = sum(wmeans)/len(wmeans)
    w2w_range = max(wmeans) - min(wmeans)
    w2w_pct = w2w_range / (2*lot_mean) * 100.0
    # lot yield = included sites within spec across all wafers
    total = sum(x["n"] for x in ws)
    total_pass = sum(x["n"] - x["n_fail"] for x in ws)
    return dict(wafers=ws, lot_mean=lot_mean, w2w_range=w2w_range, w2w_pct=w2w_pct,
                total_sites=total, total_pass=total_pass, lot_yield=total_pass/total*100.0)


if __name__ == "__main__":
    print(f"sites: {N_SITES} total, {len(INCLUDED)} included, {len(EXCLUDED)} edge-excluded (r>{EXCL_RADIUS}mm)")
    print(f"excluded site ids: {sorted(_excl_ids)}")
    print(f"Rs spec: target {RS_TARGET}, LSL {RS_LSL}, USL {RS_USL}; warn band [{RS_WARN_LO},{RS_WARN_HI}]")
    rows = measured_rows()
    print(f"raw rows (incl {len(RETESTS)} retest originals): {len(rows)}  (expect {N_WAFERS*N_SITES + len(RETESTS)})")
    dd = dedup(rows)
    print(f"deduped rows: {len(dd)}  (expect {N_WAFERS*N_SITES})")
    lot = lot_stats(dd)
    print(f"\nlot mean Rs = {lot['lot_mean']:.3f} ohm/sq")
    print(f"W2W range = {lot['w2w_range']:.3f} ohm/sq  ({lot['w2w_pct']:.3f} %)")
    print(f"lot yield (included sites in spec) = {lot['total_pass']}/{lot['total_sites']} = {lot['lot_yield']:.2f} %")
    print("\nper-wafer (included sites only):")
    print(f"  {'W':>2} {'n':>2} {'mean':>7} {'min':>6} {'max':>6} {'WIW%':>6} {'yield%':>7} {'fails':>5}")
    for x in lot["wafers"]:
        print(f"  {x['wafer']:>2} {x['n']:>2} {x['mean']:>7.2f} {x['min']:>6.2f} {x['max']:>6.2f} "
              f"{x['wiw']:>6.2f} {x['yield_pct']:>7.1f} {x['n_fail']:>5}")
    # show the impact of the traps
    print("\n-- trap impact check --")
    # if edge sites were wrongly included on wafer 1
    w=1; off=wafer_offset(w)
    allvals=[rs_value(s,w,off) for s in SITES]
    incvals=[rs_value(s,w,off) for s in INCLUDED]
    m_all=sum(allvals)/len(allvals); m_inc=sum(incvals)/len(incvals)
    print(f"  wafer 1 mean incl edge={m_all:.2f} vs correct(excl)={m_inc:.2f}  (edge inclusion error ~{m_all-m_inc:+.2f})")
    # wrong formula (sigma/mean) vs pinned (range/2mean) for wafer 1
    x1=lot["wafers"][0]
    print(f"  wafer 1 WIW pinned(range/2mean)={x1['wiw']:.2f}%  vs wrong(sigma/mean)={x1['sigma']/x1['mean']*100:.2f}%")
