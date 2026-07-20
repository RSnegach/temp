"""
Single source of truth for the contract obligation register task (legal services).

A master services agreement plus one amendment contains dated obligations whose
DUE DATES must be computed. The paralegal/contracts analyst must:

  1. Extract every obligation and its trigger (a fixed calendar date, or an event
     such as "within N days after the Effective Date", "N business days before
     each quarter end", "on the Nth of each month").
  2. Compute each due date using the correct day count:
       - "days" = calendar days
       - "business days" = skip weekends AND the holiday calendar
       - month/quarter anchors resolved to real calendar dates
  3. Apply the rolling convention: if a calendar-day deadline lands on a weekend
     or holiday, it rolls FORWARD to the next business day (per the contract's
     "next business day" clause). Business-day counts already skip non-business
     days so they never need rolling.
  4. Apply supersession: the amendment changes some periods and dates; the
     superseded original obligation must NOT appear with its old date.
  5. Apply conditionals: some obligations only exist if a condition is met
     (e.g. "if total fees exceed $250,000"); include or drop based on given facts.

Why this resists a one-shot answer: the deadlines chain off a mix of calendar
and business-day arithmetic across a real holiday calendar, one amendment silently
supersedes several original clauses, and two obligations are conditional on facts
stated elsewhere. A model that treats every "days" as calendar days, ignores the
holiday roll, or scores a superseded clause gets multiple due dates wrong.

All dates computed here so the golden ties out. Pure standard library.
"""
import datetime as _dt

# ---------------- calendar facts ----------------
EFFECTIVE_DATE = _dt.date(2025, 1, 15)          # MSA effective date
AMENDMENT_DATE = _dt.date(2025, 3, 3)           # Amendment No. 1 effective
CONTRACT_YEAR = 2025

# US federal-style holiday calendar the contract points to (observed dates 2025)
HOLIDAYS = {
    _dt.date(2025, 1, 1):  "New Year's Day",
    _dt.date(2025, 1, 20): "MLK Day",
    _dt.date(2025, 2, 17): "Presidents Day",
    _dt.date(2025, 5, 26): "Memorial Day",
    _dt.date(2025, 6, 19): "Juneteenth",
    _dt.date(2025, 7, 4):  "Independence Day",
    _dt.date(2025, 9, 1):  "Labor Day",
    _dt.date(2025, 11, 27):"Thanksgiving",
    _dt.date(2025, 11, 28):"Day after Thanksgiving",
    _dt.date(2025, 12, 25):"Christmas Day",
}

# facts referenced by conditional obligations
FACTS = {
    "total_annual_fees": 312000,     # > 250000 -> triggers the audit-support obligation
    "processes_personal_data": False, # False -> the DPA breach-drill obligation does NOT apply
    "data_classification": "High",   # buried in Exhibit B -> triggers the security review (O12)
}

# ---------------- day-count helpers ----------------
def is_business_day(d):
    return d.weekday() < 5 and d not in HOLIDAYS

def roll_forward(d):
    while not is_business_day(d):
        d += _dt.timedelta(days=1)
    return d

def add_calendar_days(start, n):
    return start + _dt.timedelta(days=n)

def add_business_days(start, n):
    """n business days AFTER start (start itself not counted)."""
    d = start; count = 0
    step = 1 if n >= 0 else -1
    while count < abs(n):
        d += _dt.timedelta(days=step)
        if is_business_day(d):
            count += 1
    return d

def business_days_before(anchor, n):
    return add_business_days(anchor, -n)

def quarter_ends(year):
    return [_dt.date(year,3,31), _dt.date(year,6,30),
            _dt.date(year,9,30), _dt.date(year,12,31)]

# ---------------- obligations ----------------
# Each: id, title, party, trigger dict, rolling(bool), conditional(key or None),
#       superseded_by (id or None). The 'compute' function returns due date(s).
# rolling only matters for calendar-day / fixed-date items.

def _kickoff():        return roll_forward(add_calendar_days(EFFECTIVE_DATE, 10))
def _first_invoice():  return add_business_days(EFFECTIVE_DATE, 5)
def _sow_signoff():    return roll_forward(add_calendar_days(EFFECTIVE_DATE, 30))
def _qbr_dates():      return [business_days_before(q, 3) for q in quarter_ends(CONTRACT_YEAR)]
def _annual_audit():   return roll_forward(_dt.date(CONTRACT_YEAR, 7, 31))     # only if fees>250k
def _insurance_cert(): return roll_forward(add_calendar_days(EFFECTIVE_DATE, 15))
def _renewal_notice(): return business_days_before(_dt.date(CONTRACT_YEAR,12,31), 60)  # amended below
def _renewal_notice_amended(): return business_days_before(_dt.date(CONTRACT_YEAR,12,31), 90)
def _monthly_report(month):
    # "by the 5th of each month"; if 5th non-business, roll forward
    return roll_forward(_dt.date(CONTRACT_YEAR, month, 5))
def _termination_true_up(): return add_calendar_days(AMENDMENT_DATE, 45)  # new in amendment
def _dpa_drill():      return roll_forward(add_calendar_days(EFFECTIVE_DATE, 60))  # conditional, off
def _integration_report():  return add_business_days(_sow_signoff(), 20)  # CHAINED off O3's due date
def _security_review():     return roll_forward(add_calendar_days(EFFECTIVE_DATE, 75))  # conditional on data class High

OBLIGATIONS = [
    dict(id="O1", title="Project kickoff meeting", party="Provider",
         basis="Within 10 calendar days after the Effective Date; roll to next business day",
         fn=_kickoff, kind="single", conditional=None, superseded=False),
    dict(id="O2", title="First monthly invoice issued", party="Provider",
         basis="Within 5 business days after the Effective Date",
         fn=_first_invoice, kind="single", conditional=None, superseded=False),
    dict(id="O3", title="Statement of Work sign-off", party="Client",
         basis="Within 30 calendar days after the Effective Date; roll to next business day",
         fn=_sow_signoff, kind="single", conditional=None, superseded=False),
    dict(id="O4", title="Quarterly business review", party="Both",
         basis="3 business days before each calendar quarter-end",
         fn=_qbr_dates, kind="multi", conditional=None, superseded=False),
    dict(id="O5", title="Annual audit support package", party="Provider",
         basis="By July 31; required only if total annual fees exceed $250,000",
         fn=_annual_audit, kind="single", conditional="fees_gt_250k", superseded=False),
    dict(id="O6", title="Certificate of insurance delivered", party="Provider",
         basis="Within 15 calendar days after the Effective Date; roll to next business day",
         fn=_insurance_cert, kind="single", conditional=None, superseded=False),
    dict(id="O7", title="Non-renewal notice (ORIGINAL, superseded)", party="Either",
         basis="At least 60 business days before Dec 31 (SUPERSEDED by Amendment No.1)",
         fn=_renewal_notice, kind="single", conditional=None, superseded=True),
    dict(id="O7A", title="Non-renewal notice (as amended)", party="Either",
         basis="At least 90 business days before Dec 31 (Amendment No.1)",
         fn=_renewal_notice_amended, kind="single", conditional=None, superseded=False),
    dict(id="O8", title="Monthly status report", party="Provider",
         basis="By the 5th of each month; roll to next business day",
         fn=lambda: [_monthly_report(m) for m in range(2, 13)], kind="multi",
         conditional=None, superseded=False),
    dict(id="O9", title="Termination true-up statement", party="Provider",
         basis="Within 45 calendar days after Amendment No.1 effective date (new)",
         fn=_termination_true_up, kind="single", conditional=None, superseded=False),
    dict(id="O10", title="Data-protection breach drill", party="Provider",
         basis="Within 60 calendar days after Effective Date; only if Provider processes personal data",
         fn=_dpa_drill, kind="single", conditional="processes_pii", superseded=False),
    dict(id="O11", title="Integration report", party="Provider",
         basis="Within 20 business days after the Statement of Work sign-off (chained to O3's due date)",
         fn=_integration_report, kind="single", conditional=None, superseded=False),
    dict(id="O12", title="Independent security review", party="Provider",
         basis="Within 75 calendar days after Effective Date; only if data classification is High (Exhibit B)",
         fn=_security_review, kind="single", conditional="data_high", superseded=False),
]

def conditional_active(key):
    if key is None: return True
    if key == "fees_gt_250k":  return FACTS["total_annual_fees"] > 250000
    if key == "processes_pii": return FACTS["processes_personal_data"]
    if key == "data_high":     return FACTS["data_classification"] == "High"
    raise ValueError(key)

def register():
    rows = []
    for o in OBLIGATIONS:
        if o["superseded"]:
            continue
        if not conditional_active(o["conditional"]):
            continue
        due = o["fn"]()
        if o["kind"] == "multi":
            for i, d in enumerate(due, 1):
                rows.append(dict(id=f'{o["id"]}.{i}', title=o["title"], party=o["party"],
                                 basis=o["basis"], due=d))
        else:
            rows.append(dict(id=o["id"], title=o["title"], party=o["party"],
                             basis=o["basis"], due=due))
    rows.sort(key=lambda r: (r["due"], r["id"]))
    return rows

if __name__ == "__main__":
    print(f"Effective {EFFECTIVE_DATE}  Amendment {AMENDMENT_DATE}")
    print(f"facts: {FACTS}")
    rows = register()
    print(f"\n{len(rows)} active dated obligations (superseded/inactive dropped):\n")
    print(f"{'id':>5}  {'due date':>12} {'day':>4}  title")
    for r in rows:
        print(f'{r["id"]:>5}  {r["due"].isoformat():>12} {r["due"].strftime("%a"):>4}  {r["title"]}')
    # show which were dropped
    dropped = [o["id"] for o in OBLIGATIONS if o["superseded"] or not conditional_active(o["conditional"])]
    print("\ndropped:", dropped, "(O7 superseded, O10 conditional-off)")
