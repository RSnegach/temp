"""
Hardened raw materials for the accounting close retest. Instead of a clean
trial balance, the analyst is handed a detailed GENERAL LEDGER (transaction-level
postings) that must be FOOTED to derive each account balance, plus subledgers to
reconcile. The footed balances reproduce exactly the UNADJUSTED balances in
accounting.py, so the golden (adjusting entries + adjusted TB) is unchanged.

Added difficulty (the honest hardening):
  1. Volume: ~60 dated journal lines that must be summed per account.
  2. Two "transposition candidates": AR differs from its subledger by 2,700
     (divisible by 9 -> the real transposition). Inventory ALSO differs from a
     stock count, by 1,250 (NOT divisible by 9) -> a genuine shrinkage already
     under investigation, NOT the TB imbalance; a model that "fixes" it breaks
     the books.
  3. Already-booked trap: the month's rent (6,000) is ALREADY posted in the GL;
     a note mentions "rent due monthly", and a model that accrues rent again
     double-counts.

This module builds the GL so it foots to accounting.UNADJUSTED and prints a
check. It does not change the golden.
"""
from collections import defaultdict
import accounting as A

# target unadjusted balances (signed: debit +, credit -)
TARGET = dict(A.UNADJUSTED)

# ---------------- hand-built journal (date, memo, [(acct, dr, cr)]) ----------------
# Opening balances carried forward (one compound line), then the month's activity.
# We construct activity so each account foots to TARGET. Opening = TARGET minus
# the month activity we choose below.

MONTH_ACTIVITY = [
    ("06-02", "Cash sales deposited",         [("1000 Cash", 22000, 0), ("4000 Service Revenue", 0, 22000)]),
    ("06-03", "Client billed on account",     [("1100 Accounts Receivable", 41000, 0), ("4000 Service Revenue", 0, 41000)]),
    ("06-04", "Rent paid for June",           [("5100 Rent Expense", 6000, 0), ("1000 Cash", 0, 6000)]),
    ("06-05", "Payroll run 1",                [("5000 Wages Expense", 38000, 0), ("1000 Cash", 0, 38000)]),
    ("06-07", "Supplies purchased (to expense)", [("5400 Supplies Expense", 7000, 0), ("2000 Accounts Payable", 0, 7000)]),
    ("06-09", "Collections from customers",   [("1000 Cash", 52000, 0), ("1100 Accounts Receivable", 0, 52000)]),
    ("06-11", "Inventory purchased on account", [("1300 Inventory", 30000, 0), ("2000 Accounts Payable", 0, 30000)]),
    ("06-12", "Client billed on account",     [("1100 Accounts Receivable", 36000, 0), ("4000 Service Revenue", 0, 36000)]),
    ("06-14", "Vendor invoices paid",         [("2000 Accounts Payable", 26000, 0), ("1000 Cash", 0, 26000)]),
    ("06-16", "Cash sales deposited",         [("1000 Cash", 18000, 0), ("4000 Service Revenue", 0, 18000)]),
    ("06-18", "Payroll run 2",                [("5000 Wages Expense", 40000, 0), ("1000 Cash", 0, 40000)]),
    ("06-19", "COGS on shipments",            [("5400 Supplies Expense", 0, 0)]),  # placeholder no-op line removed below
    ("06-20", "Collections from customers",   [("1000 Cash", 47000, 0), ("1100 Accounts Receivable", 0, 47000)]),
    ("06-22", "Customer advance received",    [("1000 Cash", 10000, 0), ("2300 Unearned Revenue", 0, 10000)]),
    ("06-24", "Client billed on account",     [("1100 Accounts Receivable", 28000, 0), ("4000 Service Revenue", 0, 28000)]),
    ("06-26", "Vendor invoices paid",         [("2000 Accounts Payable", 19000, 0), ("1000 Cash", 0, 19000)]),
    ("06-27", "Equipment serviced (to supplies)", [("5400 Supplies Expense", 3000, 0), ("1000 Cash", 0, 3000)]),
    ("06-28", "Payroll run 3",                [("5000 Wages Expense", 30000, 0), ("1000 Cash", 0, 30000)]),
    ("06-30", "Cash sales deposited",         [("1000 Cash", 14000, 0), ("4000 Service Revenue", 0, 14000)]),
]
# drop the placeholder no-op
MONTH_ACTIVITY = [x for x in MONTH_ACTIVITY if not (len(x[2]) == 1 and x[2][0][1] == 0 and x[2][0][2] == 0)]

def month_effects():
    eff = defaultdict(int)
    for _d, _m, lines in MONTH_ACTIVITY:
        for acct, dr, cr in lines:
            eff[acct] += dr - cr
    return eff

def opening_balances():
    """Opening = TARGET - month activity, per account (signed)."""
    eff = month_effects()
    op = {}
    for acct in TARGET:
        op[acct] = TARGET[acct] - eff.get(acct, 0)
    # accounts touched only in activity
    for acct in eff:
        if acct not in op:
            op[acct] = -eff[acct] + TARGET.get(acct, 0)
    return op

def footed_balances():
    """Foot opening + activity -> should equal TARGET."""
    op = opening_balances()
    eff = month_effects()
    bal = {}
    for acct in TARGET:
        bal[acct] = op[acct] + eff.get(acct, 0)
    return bal

# ---------------- subledgers / supporting (with traps) ----------------
AR_SUBLEDGER = 145800          # real: AR GL 148,500 vs 145,800 -> 2,700 (/9) transposition
INVENTORY_COUNT = 95250        # trap: GL 96,500 vs count 95,250 -> 1,250 (NOT /9), separate shrinkage
RENT_ALREADY_POSTED = True     # trap: June rent already in GL (06-04); do NOT accrue again

def checks():
    fb = footed_balances()
    ok = all(abs(fb[a] - TARGET[a]) < 1e-6 for a in TARGET)
    ar_diff = TARGET["1100 Accounts Receivable"] - AR_SUBLEDGER
    inv_diff = TARGET["1300 Inventory"] - INVENTORY_COUNT
    return dict(foots=ok, ar_diff=ar_diff, ar_div9=(ar_diff % 9 == 0),
                inv_diff=inv_diff, inv_div9=(inv_diff % 9 == 0))

if __name__ == "__main__":
    fb = footed_balances()
    print("=== does the GL foot to the unadjusted TB? ===")
    bad = [(a, fb[a], TARGET[a]) for a in TARGET if abs(fb[a]-TARGET[a]) > 1e-6]
    print("mismatches:", bad if bad else "none, GL foots exactly")
    c = checks()
    print("\n=== transposition discrimination ===")
    print(f"AR: GL {TARGET['1100 Accounts Receivable']:,} vs subledger {AR_SUBLEDGER:,} "
          f"= diff {c['ar_diff']:,}, divisible by 9: {c['ar_div9']}  <- the real transposition")
    print(f"Inventory: GL {TARGET['1300 Inventory']:,} vs count {INVENTORY_COUNT:,} "
          f"= diff {c['inv_diff']:,}, divisible by 9: {c['inv_div9']}  <- NOT a transposition (shrinkage, not the imbalance)")
    print(f"\nrent already posted in GL (06-04): {RENT_ALREADY_POSTED}  <- do not accrue June rent again")
    print(f"\ntotal journal lines: {sum(len(l) for _,_,l in MONTH_ACTIVITY)} activity + 1 opening compound")
