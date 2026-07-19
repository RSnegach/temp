"""
Single source of truth for the test-suite-design task.

System under test: LoanPreQual decision service. An applicant record is first
VALIDATED field-by-field; if any field is invalid the request is rejected with a
validation error. If all fields are valid, an ORDERED rules engine (first match
wins) returns a decision.

This module implements the exact policy the input files describe, plus the four
case-generation procedures the referenced Test Design Standard pins down:
  EP  - equivalence partitioning (one representative per class)
  BVA - boundary value analysis (min-1, min, max, max+1 per bounded numeric field)
  DT  - decision-table (one first-match representative per business rule)
  DB  - decision-boundary analysis (each numeric rule threshold, on and across)

Every single-variable case holds the other fields at the pinned BASELINE
applicant, so the expected result is deterministic. Running this file prints the
exact case counts and the full case list used by the golden suite and rubric.
"""

# ---------------- field constraints (validation) ----------------
# bounded numeric fields: (min, max, nominal_interior, kind)
NUM_FIELDS = {
    "applicant_age":       (18, 75, 35, "int"),
    "annual_income":       (0, 1_000_000, 120_000, "int"),
    "credit_score":        (300, 850, 680, "int"),
    "loan_amount":         (1_000, 500_000, 150_000, "int"),
    "existing_debt_ratio": (0.0, 60.0, 25.0, "dec1"),   # one decimal place
}
ENUM_FIELDS = {
    "employment_status": ["Employed", "Self-Employed", "Retired", "Unemployed"],
    "loan_term_months":  [12, 24, 36, 48, 60],
}
ENUM_INVALID = {"employment_status": "Contractor", "loan_term_months": 18}

FIELD_ORDER = ["applicant_age", "annual_income", "credit_score", "loan_amount",
               "existing_debt_ratio", "employment_status", "loan_term_months"]

# pinned baseline valid applicant (lands APPROVE_STANDARD); every isolation
# case starts from this and changes exactly one field.
BASELINE = {
    "applicant_age": 40,
    "annual_income": 90_000,
    "credit_score": 700,
    "loan_amount": 200_000,
    "existing_debt_ratio": 30.0,
    "employment_status": "Employed",
    "loan_term_months": 36,
}

# ---------------- validation ----------------
def validate(app):
    """Return list of (field, message). Empty => all fields valid."""
    errs = []
    for f, (lo, hi, _nom, kind) in NUM_FIELDS.items():
        v = app[f]
        if kind == "int" and not isinstance(v, int):
            errs.append((f, "must be a whole number")); continue
        if kind == "dec1":
            # must be a number with at most one decimal place
            if round(v, 1) != v:
                errs.append((f, "must have at most one decimal place")); continue
        if v < lo or v > hi:
            errs.append((f, f"must be between {lo} and {hi}"))
    for f, allowed in ENUM_FIELDS.items():
        if app[f] not in allowed:
            errs.append((f, "not a permitted value"))
    return errs

# ---------------- ordered rules engine (first match wins) ----------------
# thresholds are business values distinct from validation ranges.
T_MIN_SCORE = 620          # R2: below this -> decline
T_DTI_MAX   = 43.0         # R3: above this -> decline
T_LTI_MULT  = 5            # R4: loan > mult * income -> decline
T_PRIME_SCORE = 720        # R5
T_PRIME_DTI   = 36.0       # R5
T_STD_SCORE   = 660        # R6

def decide(app):
    """Assumes app already passed validation. Returns (code, reason)."""
    if app["employment_status"] == "Unemployed":
        return ("DECLINE", "no qualifying income source")            # R1
    if app["credit_score"] < T_MIN_SCORE:
        return ("DECLINE", "credit score below minimum")             # R2
    if app["existing_debt_ratio"] > T_DTI_MAX:
        return ("DECLINE", "debt-to-income above maximum")           # R3
    if app["loan_amount"] > T_LTI_MULT * app["annual_income"]:
        return ("DECLINE", "loan exceeds income multiple")           # R4
    if app["credit_score"] >= T_PRIME_SCORE and app["existing_debt_ratio"] <= T_PRIME_DTI:
        return ("APPROVE_PRIME", "prime tier")                       # R5
    if app["credit_score"] >= T_STD_SCORE:
        return ("APPROVE_STANDARD", "standard tier")                 # R6
    return ("REFER", "manual underwriting review")                   # R7 default

RULES = ["R1","R2","R3","R4","R5","R6","R7"]

def evaluate(app):
    errs = validate(app)
    if errs:
        f, m = errs[0]
        return f"REJECT: {f} {m}"
    code, reason = decide(app)
    return f"{code}: {reason}"

# ---------------- helpers ----------------
def base(**over):
    a = dict(BASELINE); a.update(over); return a

def vec(app):
    return {f: app[f] for f in FIELD_ORDER}

CASES = []  # list of dict(id, technique, target, vector, expected)
def add(tid, technique, target, app):
    CASES.append(dict(id=tid, technique=technique, target=target,
                      vector=vec(app), expected=evaluate(app)))

# ---------------- EP: equivalence partitioning ----------------
def gen_ep():
    i = 1
    # numeric valid-class representative (nominal interior), one per field
    for f, (lo, hi, nom, kind) in NUM_FIELDS.items():
        add(f"EP-{i:03d}", "EP", f"{f}: valid class (nominal)", base(**{f: nom})); i += 1
    # enum: one representative per permitted member + one invalid member
    for f, members in ENUM_FIELDS.items():
        for m in members:
            add(f"EP-{i:03d}", "EP", f"{f}: class '{m}'", base(**{f: m})); i += 1
        add(f"EP-{i:03d}", "EP", f"{f}: invalid class", base(**{f: ENUM_INVALID[f]})); i += 1

# ---------------- BVA: validation boundary value analysis ----------------
def step(kind): return 0.1 if kind == "dec1" else 1
def gen_bva():
    i = 1
    for f, (lo, hi, nom, kind) in NUM_FIELDS.items():
        s = step(kind)
        pts = [(round(lo - s, 1), "min-1 (invalid low)"),
               (lo, "min (valid low)"),
               (hi, "max (valid high)"),
               (round(hi + s, 1), "max+1 (invalid high)")]
        for val, tag in pts:
            v = int(val) if kind == "int" else round(float(val), 1)
            add(f"BVA-{i:03d}", "BVA", f"{f}: {tag}", base(**{f: v})); i += 1

# ---------------- DT: decision-table, one first-match rep per rule ----------------
def gen_dt():
    # each case is a valid applicant crafted to trigger exactly one rule first.
    reps = [
        ("R1", base(employment_status="Unemployed")),
        ("R2", base(credit_score=600)),                       # <620, not unemployed
        ("R3", base(existing_debt_ratio=50.0)),               # >43, score ok
        ("R4", base(loan_amount=500_000, annual_income=90_000)),  # 500k > 5*90k=450k
        ("R5", base(credit_score=740, existing_debt_ratio=30.0)), # >=720 & <=36
        ("R6", base(credit_score=680, existing_debt_ratio=40.0)), # >=660, not prime (DTI>36)
        ("R7", base(credit_score=640, existing_debt_ratio=40.0)), # 620-659 -> refer
    ]
    for i, (rule, app) in enumerate(reps, 1):
        add(f"DT-{i:03d}", "DT", f"decision rule {rule}", app)

# ---------------- DB: decision-boundary analysis on rule thresholds ----------------
def gen_db():
    i = 1
    # R2 min score 620: 619 declines, 620 passes R2
    add(f"DB-{i:03d}", "DB", "R2 score threshold: 619 (below)", base(credit_score=619)); i += 1
    add(f"DB-{i:03d}", "DB", "R2 score threshold: 620 (at)", base(credit_score=620)); i += 1
    # R6 standard score 660: 659 vs 660
    add(f"DB-{i:03d}", "DB", "R6 score threshold: 659 (below)", base(credit_score=659)); i += 1
    add(f"DB-{i:03d}", "DB", "R6 score threshold: 660 (at)", base(credit_score=660)); i += 1
    # R5 prime score 720: 719 vs 720 (DTI held <=36 so R5 can trigger)
    add(f"DB-{i:03d}", "DB", "R5 score threshold: 719 (below)", base(credit_score=719, existing_debt_ratio=30.0)); i += 1
    add(f"DB-{i:03d}", "DB", "R5 score threshold: 720 (at)", base(credit_score=720, existing_debt_ratio=30.0)); i += 1
    # R5 prime DTI 36.0: 36.0 vs 36.1 (score held >=720)
    add(f"DB-{i:03d}", "DB", "R5 DTI threshold: 36.0 (at)", base(credit_score=740, existing_debt_ratio=36.0)); i += 1
    add(f"DB-{i:03d}", "DB", "R5 DTI threshold: 36.1 (above)", base(credit_score=740, existing_debt_ratio=36.1)); i += 1
    # R3 DTI max 43.0: 43.0 vs 43.1
    add(f"DB-{i:03d}", "DB", "R3 DTI threshold: 43.0 (at)", base(existing_debt_ratio=43.0)); i += 1
    add(f"DB-{i:03d}", "DB", "R3 DTI threshold: 43.1 (above)", base(existing_debt_ratio=43.1)); i += 1
    # R4 loan-to-income 5x: income 100k -> 500k (at) vs 500001 (above). keep loan<=max 500000.
    add(f"DB-{i:03d}", "DB", "R4 LTI threshold: loan=5x income (at)", base(annual_income=100_000, loan_amount=500_000)); i += 1
    add(f"DB-{i:03d}", "DB", "R4 LTI threshold: loan just over 5x income", base(annual_income=99_000, loan_amount=496_000)); i += 1  # 496000 > 495000

# ---------------- control-flow graph of the decision engine ----------------
# The rule engine is a chain of binary decisions. R5 (score>=720 AND dti<=36)
# decomposes into TWO sequential gates the rules TABLE hides as one row. The
# decision-flow graph (input file 4) exposes them, which is what unlocks branch
# and basis-path coverage.
#
# Decision (predicate) nodes, in order:
#   D1 employment_status == Unemployed        (R1)
#   D2 credit_score < 620                      (R2)
#   D3 existing_debt_ratio > 43.0              (R3)
#   D4 loan_amount > 5 * annual_income         (R4)
#   D5 credit_score >= 720                      (R5 score gate)
#   D6 existing_debt_ratio <= 36.0             (R5 dti gate)
#   D7 credit_score >= 660                      (R6)
# 7 predicates -> 14 branches -> V(G) = 7 + 1 = 8 basis paths.
DECISION_NODES = ["D1","D2","D3","D4","D5","D6","D7"]
CYCLOMATIC = len(DECISION_NODES) + 1   # V(G) = 8

def cfg_edge_node_check():
    """Cross-check V(G) via E - N + 2 with a single merged exit node.
    Nodes: entry + 7 decisions + 1 exit = 9. Edges: entry->D1 (1) + 2 per
    decision (14) = 15.  V = 15 - 9 + 2 = 8."""
    N = 1 + len(DECISION_NODES) + 1
    E = 1 + 2*len(DECISION_NODES)
    return E - N + 2, N, E

def trace(app):
    """Ordered list of (decision_node, branch_taken_bool) for a VALID record.
    Returns None for a record that fails validation (rejected before the engine,
    so it exercises no decision branch)."""
    if validate(app):
        return None
    p=[]
    if app["employment_status"]=="Unemployed": p.append(("D1",True)); return p
    p.append(("D1",False))
    if app["credit_score"]<T_MIN_SCORE: p.append(("D2",True)); return p
    p.append(("D2",False))
    if app["existing_debt_ratio"]>T_DTI_MAX: p.append(("D3",True)); return p
    p.append(("D3",False))
    if app["loan_amount"]>T_LTI_MULT*app["annual_income"]: p.append(("D4",True)); return p
    p.append(("D4",False))
    if app["credit_score"]>=T_PRIME_SCORE:
        p.append(("D5",True))
        if app["existing_debt_ratio"]<=T_PRIME_DTI: p.append(("D6",True)); return p
        p.append(("D6",False))
    else:
        p.append(("D5",False))
    if app["credit_score"]>=T_STD_SCORE: p.append(("D7",True)); return p
    p.append(("D7",False)); return p

# ---------------- PATH: basis-path coverage (8 independent paths) ----------------
def gen_path():
    reps=[
        ("P1: D1-T", base(employment_status="Unemployed")),
        ("P2: D1-F D2-T", base(credit_score=600)),
        ("P3: D1-F D2-F D3-T", base(existing_debt_ratio=50.0)),
        ("P4: ...D4-T", base(loan_amount=500_000, annual_income=90_000)),
        ("P5: ...D5-T D6-T", base(credit_score=740, existing_debt_ratio=30.0)),
        ("P6: ...D5-T D6-F D7-T", base(credit_score=740, existing_debt_ratio=40.0)),
        ("P7: ...D5-F D7-T", base(credit_score=700, existing_debt_ratio=30.0)),
        ("P8: ...D5-F D7-F", base(credit_score=640, existing_debt_ratio=30.0)),
    ]
    for i,(lbl,app) in enumerate(reps,1):
        add(f"PATH-{i:03d}","PATH",lbl,app)

def branch_coverage():
    """Map each of the 14 branches to the case ids that exercise it (valid cases)."""
    cov={}
    for c in CASES:
        # rebuild the app dict from the vector to trace
        app={f:c["vector"][f] for f in FIELD_ORDER}
        tr=trace(app)
        if tr is None: continue
        for node,b in tr:
            cov.setdefault((node,b),[]).append(c["id"])
    return cov

def build_all():
    CASES.clear()
    gen_ep(); gen_bva(); gen_dt(); gen_db(); gen_path()
    return CASES

if __name__ == "__main__":
    cases = build_all()
    from collections import Counter
    by_tech = Counter(c["technique"] for c in cases)
    by_exp = Counter(c["expected"].split(":")[0] for c in cases)
    print("case counts by technique:")
    for t in ["EP","BVA","DT","DB","PATH"]:
        print(f"  {t}: {by_tech[t]}")
    print(f"  TOTAL: {len(cases)}")

    vg, N, E = cfg_edge_node_check()
    print(f"\nCFG: {len(DECISION_NODES)} decision nodes, {2*len(DECISION_NODES)} branches, "
          f"nodes(incl entry+exit)={N}, edges={E}")
    print(f"  V(G) = decisions+1 = {CYCLOMATIC}   cross-check E-N+2 = {vg}   match={CYCLOMATIC==vg}")

    cov = branch_coverage()
    all_branches = [(d,b) for d in DECISION_NODES for b in (True,False)]
    uncovered = [br for br in all_branches if br not in cov]
    print(f"\nbranch coverage: {len(cov)}/{len(all_branches)} branches hit; uncovered={uncovered}")
    print("basis paths (PATH cases):")
    for c in cases:
        if c["technique"]=="PATH":
            app={f:c['vector'][f] for f in FIELD_ORDER}
            tr="->".join(f"{n}{'T' if b else 'F'}" for n,b in trace(app))
            print(f"  {c['id']}: {tr}  => {c['expected'].split(':')[0]}")
    print("\nexpected-result distribution (by code):")
    for k, v in sorted(by_exp.items()):
        print(f"  {k}: {v}")
    print("\nfull case list:")
    for c in cases:
        vshort = f"age{c['vector']['applicant_age']} inc{c['vector']['annual_income']} sc{c['vector']['credit_score']} loan{c['vector']['loan_amount']} dti{c['vector']['existing_debt_ratio']} {c['vector']['employment_status']} t{c['vector']['loan_term_months']}"
        print(f"  {c['id']:8s} {c['technique']:4s} | {c['target']:42s} | {c['expected']}")
