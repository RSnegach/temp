"""
Single source of truth for the fuel-delivery DFMEA task (AIAG-VDA, 2019+).

Encodes:
  - the AIAG-VDA Action Priority (AP) lookup: (Severity, Occurrence, Detection)
    each 1-10 -> High / Medium / Low, per the published band logic.
  - the failure-mode set for a fuel delivery system, with Severity and
    Occurrence pinned, Detection derived from the current detection control's
    capability, plus duplicate and superseded rows to reconcile.
  - the detection-control -> Detection-rating map.

Running this prints the full AP grid (for handbook verification) and the scored
DFMEA. Every AP and Detection value is computed here so the golden ties out.

AP band logic (AIAG-VDA FMEA Handbook 1st ed., 2019):
  Severity is the primary band, then Occurrence, then Detection.
  S 9-10 (very high):
     O 6-10: High for all D
     O 4-5 : High for all D
     O 2-3 : D 1-4 High, D 5-7 High, D 8-10 High   (S 9-10 stays High whenever
             O>=2; only O=1 relaxes)
     O 1   : D 1-5 Medium, D 6-7 Medium, D 8-10 High... (see table below)
  The exact grid is defined in AP_ROWS as (S_lo,S_hi,O_lo,O_hi,D_lo,D_hi,AP).
"""

# ---------------------------------------------------------------------------
# AIAG-VDA Action Priority table, expressed as band rows.
# Each row: (S range, O range, D range) -> AP. Ranges inclusive.
# Order does not matter; every (S,O,D) in 1..10 matches exactly one row.
# ---------------------------------------------------------------------------
AP_ROWS = [
    # ================= Severity 9-10 =================
    (9,10, 6,10, 1,10, "H"),
    (9,10, 4,5,  1,10, "H"),
    (9,10, 2,3,  1,4,  "H"),
    (9,10, 2,3,  5,7,  "H"),
    (9,10, 2,3,  8,10, "H"),
    (9,10, 1,1,  1,4,  "M"),
    (9,10, 1,1,  5,7,  "M"),
    (9,10, 1,1,  8,10, "H"),
    # ================= Severity 7-8 =================
    (7,8,  6,10, 1,4,  "H"),
    (7,8,  6,10, 5,7,  "H"),
    (7,8,  6,10, 8,10, "H"),
    (7,8,  4,5,  1,4,  "M"),
    (7,8,  4,5,  5,7,  "H"),
    (7,8,  4,5,  8,10, "H"),
    (7,8,  2,3,  1,4,  "L"),
    (7,8,  2,3,  5,7,  "M"),
    (7,8,  2,3,  8,10, "H"),
    (7,8,  1,1,  1,4,  "L"),
    (7,8,  1,1,  5,7,  "M"),
    (7,8,  1,1,  8,10, "M"),
    # ================= Severity 4-6 =================
    (4,6,  6,10, 1,4,  "M"),
    (4,6,  6,10, 5,7,  "H"),
    (4,6,  6,10, 8,10, "H"),
    (4,6,  4,5,  1,4,  "L"),
    (4,6,  4,5,  5,7,  "M"),
    (4,6,  4,5,  8,10, "H"),
    (4,6,  2,3,  1,4,  "L"),
    (4,6,  2,3,  5,7,  "L"),
    (4,6,  2,3,  8,10, "M"),
    (4,6,  1,1,  1,4,  "L"),
    (4,6,  1,1,  5,7,  "L"),
    (4,6,  1,1,  8,10, "L"),
    # ================= Severity 2-3 =================
    (2,3,  6,10, 1,4,  "L"),
    (2,3,  6,10, 5,7,  "M"),
    (2,3,  6,10, 8,10, "M"),
    (2,3,  4,5,  1,4,  "L"),
    (2,3,  4,5,  5,7,  "L"),
    (2,3,  4,5,  8,10, "M"),
    (2,3,  2,3,  1,4,  "L"),
    (2,3,  2,3,  5,7,  "L"),
    (2,3,  2,3,  8,10, "L"),
    (2,3,  1,1,  1,10, "L"),
    # ================= Severity 1 =================
    (1,1,  1,10, 1,10, "L"),
]

def action_priority(S, O, D):
    for slo,shi,olo,ohi,dlo,dhi,ap in AP_ROWS:
        if slo<=S<=shi and olo<=O<=ohi and dlo<=D<=dhi:
            return ap
    raise ValueError(f"no AP row for S={S} O={O} D={D}")

def action_required(ap):
    # AIAG-VDA: High -> action needed; Medium -> should act / justify; Low -> as-is.
    return {"H":"Yes","M":"Review","L":"No"}[ap]

# ---------------------------------------------------------------------------
# Detection control capability -> Detection rating (1-10).
# Lower D = better detection. Maps a named control class to its D rating.
# ---------------------------------------------------------------------------
DETECTION_MAP = {
    "None / not detectable":            10,
    "Visual inspection only":            8,
    "Functional end-of-line test":       6,
    "In-line automated leak test":       4,
    "100% automated with error-proofing":2,
    "Design validation + in-line PPAP":  3,
    "Bench durability test":             5,
    "Pressure decay test (in-line)":     4,
}

# ---------------------------------------------------------------------------
# Failure-mode source set for a fuel delivery system.
# S (severity) and O (occurrence) are pinned (given in the input data).
# Detection is DERIVED from the 'control' via DETECTION_MAP.
# 'status' Active vs superseded/duplicate is reconciled before scoring.
# fm_id groups duplicates/supersedes: keep the row with the highest rev.
# ---------------------------------------------------------------------------
# fields: id, rev, status, item, function, failure_mode, effect, S, O, control
MODES = [
    ("FM-01",1,"Active","Fuel Rail","Contain pressurized fuel","External fuel leak at rail joint","Fuel leak, fire risk",9,3,"In-line automated leak test"),
    ("FM-02",1,"Active","Injector","Meter fuel per command","Injector partially clogged","Lean misfire, driveability",6,5,"Functional end-of-line test"),
    ("FM-03",1,"Active","Injector","Meter fuel per command","Injector stuck open","Rich run, emissions, hydrolock",8,2,"Bench durability test"),
    ("FM-04",1,"Superseded","Fuel Pump","Deliver rated flow/pressure","Pump wear low flow","Long crank",5,4,"Functional end-of-line test"),
    ("FM-04",2,"Active","Fuel Pump","Deliver rated flow/pressure","Pump wear reduces flow below spec","Hard start, stall under load",7,4,"Functional end-of-line test"),
    ("FM-05",1,"Active","Pressure Regulator","Regulate rail pressure","Regulator drifts high","Rich mixture, emissions fail",6,3,"In-line automated leak test"),
    ("FM-06",1,"Active","Pressure Regulator","Regulate rail pressure","Regulator drifts low","Lean, power loss",6,3,"Functional end-of-line test"),
    ("FM-07",1,"Duplicate","Fuel Rail","Contain pressurized fuel","External fuel leak at rail joint","Fuel leak",9,3,"In-line automated leak test"),
    ("FM-08",1,"Active","Tank Seal","Contain fuel vapor/liquid","Seal degradation, weep","Evap leak, emissions",7,2,"Visual inspection only"),
    ("FM-09",1,"Active","Quick Connector","Join fuel lines","Connector not fully seated","Fuel leak on vibration, fire risk",9,2,"100% automated with error-proofing"),
    ("FM-10",1,"Active","Fuel Filter","Filter particulate","Filter media bypass","Injector wear over time",4,4,"Bench durability test"),
    ("FM-11",1,"Active","Fuel Pump","Deliver rated flow/pressure","Pump electrical open","No start",8,2,"Functional end-of-line test"),
    ("FM-12",1,"Active","Injector","Meter fuel per command","Injector external seal leak","Fuel leak at seat, fire risk",9,2,"Pressure decay test (in-line)"),
    ("FM-13",1,"Superseded","Fuel Rail","Contain pressurized fuel","Rail cracks from pressure cycling","Fuel leak",9,1,"Design validation + in-line PPAP"),
    ("FM-13",2,"Active","Fuel Rail","Contain pressurized fuel","Rail cracks from pressure cycling fatigue","Fuel leak, fire risk",9,2,"Design validation + in-line PPAP"),
    ("FM-14",1,"Active","Regulator Diaphragm","Seal reference chamber","Diaphragm rupture","Rich, fuel in vacuum line",7,3,"None / not detectable"),
    ("FM-15",1,"Active","Fuel Filter","Filter particulate","Filter fully clogged","Fuel starvation, stall",7,3,"Functional end-of-line test"),
]

def dedup(modes):
    """Keep only Active rows; drop Duplicate and Superseded. For a fm_id with a
    superseded + active pair, the Active (higher rev) survives."""
    return [m for m in modes if m[2]=="Active"]

def score():
    rows=[]
    for (fid,rev,status,item,func,fm,eff,S,O,control) in dedup(MODES):
        D=DETECTION_MAP[control]
        ap=action_priority(S,O,D)
        rows.append(dict(id=fid,item=item,function=func,mode=fm,effect=eff,
                         S=S,O=O,control=control,D=D,ap=ap,action=action_required(ap)))
    # rank: High first, then Medium, then Low; within, by S desc then O desc then D desc
    order={"H":0,"M":1,"L":2}
    rows.sort(key=lambda r:(order[r["ap"]], -r["S"], -r["O"], -r["D"]))
    for i,r in enumerate(rows,1): r["rank"]=i
    return rows


if __name__=="__main__":
    # 1) verify AP grid coverage: every (S,O,D) maps to exactly one AP
    seen={}
    for S in range(1,11):
        for O in range(1,11):
            for D in range(1,11):
                seen[(S,O,D)]=action_priority(S,O,D)
    from collections import Counter
    print("AP grid: 1000 combos covered, distribution:", dict(Counter(seen.values())))

    # 2) print compact AP grid by severity band for handbook check
    print("\n=== AP TABLE (rows = S band / O band, cols = D 1-4 | 5-7 | 8-10) ===")
    Sband=[(9,10),(7,8),(4,6),(2,3),(1,1)]
    Oband=[(6,10),(4,5),(2,3),(1,1)]
    Dband=[(1,4),(5,7),(8,10)]
    print(f"{'S':>5} {'O':>5} | {'D1-4':>5} {'D5-7':>5} {'D8-10':>6}")
    for slo,shi in Sband:
        for olo,ohi in Oband:
            cells=[action_priority(shi,ohi,dh) for (dl,dh) in Dband]
            print(f"{slo}-{shi:>2} {olo}-{ohi:>2} |  {cells[0]:>4}  {cells[1]:>4}   {cells[2]:>4}")

    # 3) scored DFMEA
    rows=score()
    print(f"\n=== SCORED DFMEA ({len(rows)} active modes; {len(MODES)-len(rows)} dropped as dup/superseded) ===")
    print(f"{'rk':>2} {'id':>6} {'mode':38s} {'S':>2}{'O':>2}{'D':>3}  {'AP':>2} {'action':>6}")
    for r in rows:
        print(f"{r['rank']:>2} {r['id']:>6} {r['mode'][:38]:38s} {r['S']:>2}{r['O']:>2}{r['D']:>3}  {r['ap']:>2} {r['action']:>6}")
    from collections import Counter
    print("\nAP distribution:", dict(Counter(r['ap'] for r in rows)))
