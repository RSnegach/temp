"""
Single source of truth for the month-end close and reconciliation task
(accounting services).

An unadjusted trial balance does not balance and contains posting errors. Backed
by subledgers and a bank statement, the accountant must:

  1. Identify each error/omission by comparing the general ledger to the
     supporting records (bank reconciliation, subledger totals, accrual schedule).
  2. Write the adjusting journal entry (AJE) for each: debit account, credit
     account, amount. Each AJE must itself balance (debits = credits).
  3. Post the AJEs to the unadjusted trial balance to produce an adjusted trial
     balance whose total debits equal total credits.
  4. Confirm the adjusted net income and the balance-sheet identity.

Why this resists a one-shot answer: the unadjusted TB is deliberately out of
balance (a transposition error), so a model that just "makes it balance" without
finding the specific transposition mis-states an account; several adjustments are
pairs (accrue expense + payable, record depreciation, reclassify a misposting)
where the wrong contra-account still balances the entry but breaks the specific
account totals the subledgers dictate; and one item is a bank timing difference
that is a reconciling item but NOT a journal entry (deposit in transit), which a
model often wrongly books.

All numbers computed here so the golden ties out. Pure standard library.
"""
from collections import defaultdict

# ---------------- chart of accounts (normal balance) ----------------
# type: A(asset,debit), L(liability,credit), Q(equity,credit),
#       R(revenue,credit), X(expense,debit)
COA = {
    "1000 Cash":                 "A",
    "1100 Accounts Receivable":  "A",
    "1200 Prepaid Insurance":    "A",
    "1300 Inventory":            "A",
    "1500 Equipment":            "A",
    "1510 Accum Depreciation":   "A",   # contra-asset (credit normal), handled by sign
    "2000 Accounts Payable":     "L",
    "2100 Accrued Liabilities":  "L",
    "2200 Wages Payable":        "L",
    "2300 Unearned Revenue":     "L",
    "3000 Common Stock":         "Q",
    "3100 Retained Earnings":    "Q",
    "4000 Service Revenue":      "R",
    "5000 Wages Expense":        "X",
    "5100 Rent Expense":         "X",
    "5200 Insurance Expense":    "X",
    "5300 Depreciation Expense": "X",
    "5400 Supplies Expense":     "X",
    "5500 Bank Charges":         "X",
}
CONTRA_ASSET = {"1510 Accum Depreciation"}   # asset section but credit-normal

def normal_side(acct):
    t = COA[acct]
    if acct in CONTRA_ASSET:
        return "C"
    return "D" if t in ("A", "X") else "C"

# ---------------- unadjusted trial balance ----------------
# Stored as signed (debit positive, credit negative) so we can detect imbalance.
# This TB is INTENTIONALLY out of balance due to a transposition in AR
# (posted 148,500 but should be 145,800 per the AR subledger -> 2,700 too high).
UNADJUSTED = {
    "1000 Cash":                 88100,
    "1100 Accounts Receivable":  148500,   # transposed; subledger says 145,800
    "1200 Prepaid Insurance":    18000,
    "1300 Inventory":            96500,
    "1500 Equipment":            240000,
    "1510 Accum Depreciation":  -60000,    # credit balance
    "2000 Accounts Payable":    -73200,
    "2100 Accrued Liabilities":  0,
    "2200 Wages Payable":        0,
    "2300 Unearned Revenue":    -30000,
    "3000 Common Stock":        -150000,
    "3100 Retained Earnings":   -216200,
    "4000 Service Revenue":     -395000,
    "5000 Wages Expense":        228000,
    "5100 Rent Expense":         66000,
    "5200 Insurance Expense":    0,
    "5300 Depreciation Expense": 0,
    "5400 Supplies Expense":     42000,
    "5500 Bank Charges":         0,
    # With correct AR (145,800) this TB balances exactly; the transposition to
    # 148,500 leaves it out of balance by 2,700 (debits exceed credits).
}

# ---------------- supporting records / facts ----------------
SUBLEDGER_AR = 145800          # AR aging total (true AR)
BANK = dict(
    balance_per_bank = 90100,
    deposit_in_transit = 8000,     # reconciling item, NOT a JE
    outstanding_checks = 12300,    # reconciling item, NOT a JE
    bank_service_fee = 400,        # JE: debit bank fee (misc), credit cash
    nsf_check = 1900,              # JE: reinstate AR, credit cash (customer check bounced)
)
INSURANCE = dict(annual_premium=18000, months_expired=4)  # 12-month policy, 4 mo used
DEP_ANNUAL = 24000; DEP_MONTHS = 1                        # monthly depreciation
WAGES_ACCRUED = 7600                                     # earned, unpaid at month end
UNEARNED_RECOGNIZED = 12000                              # portion now earned
RENT_MISPOST = 6000     # 6,000 of "Rent Expense" was actually a supplies purchase

# ---------------- adjusting journal entries ----------------
# Each entry: list of (account, debit, credit). Must balance internally.
def transposition_correction():
    """The 2,700 out-of-balance is a trial-balance TRANSCRIPTION error: AR was
    carried to the TB as 148,500 but the aging subledger totals 145,800. The
    difference 2,700 is divisible by 9, the classic transposition signature. This
    is corrected by restating the AR balance to the subledger. It is NOT a journal
    entry (no ledger transaction occurred); booking a JE for it double-corrects."""
    diff = UNADJUSTED["1100 Accounts Receivable"] - SUBLEDGER_AR   # 2,700
    return dict(account="1100 Accounts Receivable",
                from_bal=UNADJUSTED["1100 Accounts Receivable"],
                to_bal=SUBLEDGER_AR, diff=diff, div9=(diff % 9 == 0))

def build_ajes():
    ajes = []

    # AJE-1: expired insurance (4 of 12 months): 18,000*4/12 = 6,000
    exp_ins = INSURANCE["annual_premium"] * INSURANCE["months_expired"] // 12
    ajes.append(("AJE-1 Record expired prepaid insurance",
                 [("5200 Insurance Expense", exp_ins, 0),
                  ("1200 Prepaid Insurance", 0, exp_ins)]))

    # AJE-2: monthly depreciation 24,000/12 = 2,000
    dep = DEP_ANNUAL // 12 * DEP_MONTHS
    ajes.append(("AJE-2 Record depreciation",
                 [("5300 Depreciation Expense", dep, 0),
                  ("1510 Accum Depreciation", 0, dep)]))

    # AJE-3: accrue unpaid wages
    ajes.append(("AJE-3 Accrue wages earned, unpaid",
                 [("5000 Wages Expense", WAGES_ACCRUED, 0),
                  ("2200 Wages Payable", 0, WAGES_ACCRUED)]))

    # AJE-4: recognize earned portion of unearned revenue
    ajes.append(("AJE-4 Recognize earned unearned revenue",
                 [("2300 Unearned Revenue", UNEARNED_RECOGNIZED, 0),
                  ("4000 Service Revenue", 0, UNEARNED_RECOGNIZED)]))

    # AJE-5: reclassify misposted rent to supplies (both are expenses; the
    # contra-account matters: crediting Rent and debiting Supplies keeps total
    # expense flat but corrects each line to what the subledger supports).
    ajes.append(("AJE-5 Reclassify misposted rent to supplies",
                 [("5400 Supplies Expense", RENT_MISPOST, 0),
                  ("5100 Rent Expense", 0, RENT_MISPOST)]))

    # AJE-6: bank service fee charged by the bank (an expense), reduces cash.
    ajes.append(("AJE-6 Record bank service fee",
                 [("5500 Bank Charges", BANK["bank_service_fee"], 0),
                  ("1000 Cash", 0, BANK["bank_service_fee"])]))

    # AJE-7: NSF (bounced) customer check: reinstate the receivable, reduce cash.
    ajes.append(("AJE-7 Reinstate AR for NSF check",
                 [("1100 Accounts Receivable", BANK["nsf_check"], 0),
                  ("1000 Cash", 0, BANK["nsf_check"])]))

    return ajes

def aje_effects(ajes):
    """Net signed effect (debit +, credit -) per account across all AJEs."""
    eff = defaultdict(int)
    for _title, lines in ajes:
        for acct, dr, cr in lines:
            eff[acct] += dr - cr
    return eff

def corrected_tb():
    """UNADJUSTED with the transposition transcription error restated to the
    subledger (AR 148,500 -> 145,800). After this the TB balances, BEFORE any
    period-end AJE is posted."""
    tc = transposition_correction()
    tb = dict(UNADJUSTED)
    tb[tc["account"]] = tc["to_bal"]
    return tb

def adjusted_tb():
    ajes = build_ajes()
    eff = aje_effects(ajes)
    base = corrected_tb()
    adj = {}
    for acct, bal in base.items():
        adj[acct] = bal + eff.get(acct, 0)
    for acct in eff:
        if acct not in adj:
            adj[acct] = eff[acct]
    return adj

def totals(tb):
    dr = sum(v for v in tb.values() if v > 0)
    cr = -sum(v for v in tb.values() if v < 0)
    return dr, cr

def net_income(tb):
    rev = sum(-v for a, v in tb.items() if COA[a] == "R")
    exp = sum(v for a, v in tb.items() if COA[a] == "X")
    return rev - exp

if __name__ == "__main__":
    dr0, cr0 = totals(UNADJUSTED)
    print("=== unadjusted trial balance ===")
    print(f"total debits  = {dr0:,}")
    print(f"total credits = {cr0:,}")
    print(f"out of balance by {dr0-cr0:,}  (the AR transposition)")

    tc = transposition_correction()
    print("\n=== step 1: transposition correction (NOT a journal entry) ===")
    print(f"{tc['account']}: {tc['from_bal']:,} -> {tc['to_bal']:,} "
          f"(diff {tc['diff']:,}, divisible by 9: {tc['div9']})")
    drc, crc = totals(corrected_tb())
    print(f"corrected TB: debits {drc:,} = credits {crc:,}  balanced: {drc==crc}")

    ajes = build_ajes()
    print(f"\n=== {len(ajes)} adjusting journal entries ===")
    for title, lines in ajes:
        bal_dr = sum(l[1] for l in lines); bal_cr = sum(l[2] for l in lines)
        flag = "OK" if bal_dr == bal_cr else "!!IMBALANCED!!"
        print(f"{title}  [{flag} {bal_dr}={bal_cr}]")
        for acct, dr, cr in lines:
            print(f"    {acct:28s} Dr {dr:>8,} Cr {cr:>8,}")

    adj = adjusted_tb()
    drA, crA = totals(adj)
    print("\n=== adjusted trial balance ===")
    for acct in COA:
        v = adj.get(acct, 0)
        side = "Dr" if v > 0 else ("Cr" if v < 0 else "  ")
        print(f"  {acct:28s} {side} {abs(v):>10,}")
    print(f"\ntotal debits  = {drA:,}")
    print(f"total credits = {crA:,}")
    print(f"balanced: {drA == crA}")
    print(f"adjusted net income = {net_income(adj):,}")

    # bank reconciliation (reconciling items, not JEs)
    b = BANK
    adj_bank = b["balance_per_bank"] + b["deposit_in_transit"] - b["outstanding_checks"]
    adj_book = UNADJUSTED["1000 Cash"] - b["bank_service_fee"] - b["nsf_check"]
    print("\n=== bank reconciliation ===")
    print(f"adjusted bank balance = {adj_bank:,}  (bank + DIT - O/S checks)")
    print(f"adjusted book cash    = {adj_book:,}  (cash - fee - NSF)")
    print(f"reconciles: {adj_bank == adj_book}")
