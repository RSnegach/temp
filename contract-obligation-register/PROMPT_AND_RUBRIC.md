# Contract Obligation Register (MER-2025-0087) - Prompt and Rubric

## PROMPT (practitioner voice, paste verbatim)

I need a deadline calendar built off our services agreement so nothing gets missed this year. The contract is in `MSA_and_Amendment.docx`: the master agreement, Amendment No. 1, and Exhibit B. Read all of it, including the exhibit, because the facts that decide some of the deadlines live down there.

Pull every dated obligation and compute its due date for 2025. A few things to watch. The amendment changes some of the original terms, so do not calendar a clause the amendment deleted; use the amended version. Some obligations only apply if a condition is met, and the conditions are stated in the document (the fee threshold, whether we process personal data, the data classification in the exhibit), so include or drop each on its facts. At least one deadline is measured off another obligation's due date rather than a fixed date, so compute the driver first. And use the document's own day-count rules: calendar days count every day and roll forward to the next business day if they land on a weekend or holiday, business-day counts skip weekends and the Exhibit B holidays and are not rolled again.

Give it back as `Obligation_Register.xlsx`: one row per dated obligation occurrence with the clause, a short title, and the due date, sorted by date. List the monthly and quarterly items as separate dated rows for the year. Put the dropped obligations on their own tab with the reason each was dropped. Compute the dates with live date formulas off an anchor-dates block and the holiday list so the calendar rebuilds if a date changes.

---

## RUBRIC (weights in the numeric field only)

Each criterion is one atomic check. Due dates state their derivation from the contract's dates and rules.

Supersession and scope (read the amendment and exhibit):
**+4** The original Section 7.2 non-renewal notice at 60 business days before Dec 31 is NOT calendared; the amended 90-business-days-before-Dec-31 version is used instead (due 2025-08-21).
**+2** The termination true-up statement (new Section 4.3 from Amendment No. 1) is included, due 45 calendar days after the amendment date, 2025-04-17.
**-3** The deleted original Section 7.2 (60 business days) is calendared, or both the original and amended versions appear.

Conditionals (include or drop on the stated facts):
**+3** The annual audit support package is included because total annual fees ($312,000 in Exhibit B) exceed $250,000; due 2025-07-31.
**+3** The independent security review (Section 9.2) is included because the Exhibit B data classification is High; due 2025-03-31 (75 calendar days after the Effective Date).
**+3** The data-protection breach drill (Section 9.1) is dropped because the Provider does not Process Personal Data.
**-3** The breach drill is calendared despite the no-personal-data fact, or the security review is dropped despite the High classification, or the audit package is dropped despite fees over the threshold.

Chained deadline:
**+4** The integration report (Section 4.2) is due 20 business days after the SOW sign-off DUE DATE (2025-02-14), computed as 2025-03-17, not measured from the Effective Date or an assumed actual sign-off.
**-3** The integration report is measured from the Effective Date, or from a date other than the Section 4.1 sign-off due date.

Day-count and rolling:
**+3** The 5-business-day first invoice is 2025-01-23 (skipping the Jan 20 holiday), and the 10-calendar-day kickoff rolls from Sat Jan 25 to Mon 2025-01-27.
**+2** Quarterly reviews are 3 business days before each quarter-end: 2025-03-26, 2025-06-25, 2025-09-25, 2025-12-26 (the Q4 date clears the Dec 25 holiday and the weekend).
**+2** Monthly status reports on the 5th roll forward only when the 5th is a weekend: Apr 2025-04-07, Jul 2025-07-07, Oct 2025-10-06; the others stay on the 5th.
**-3** Calendar-day deadlines are not rolled off weekends/holidays, or business-day counts are rolled a second time, shifting multiple dates.

Structure and completeness:
**+3** The register has exactly 24 active dated rows (7 one-time obligations plus 4 quarterly plus 11 monthly plus the chained report and the security review), sorted by due date.
**+2** Due dates are live date formulas (business-day and calendar-day functions off an anchor block and the holiday list), not typed-in dates.
**+2** Dropped obligations are listed with their reason (Section 7.2 original superseded; Section 9.1 breach drill condition not met).

---

## Golden scores 100 against this rubric
The golden `Obligation_Register.xlsx` produces 24 active dated rows, uses the amended 90-day non-renewal deadline (2025-08-21), includes the audit package and the security review on their met conditions, drops the breach drill, computes the integration report as a chained deadline (2025-03-17), rolls calendar deadlines off weekends and holidays while leaving business-day counts unrolled, and lists the two dropped obligations with reasons. All dates are live formulas off the anchor and holiday cells.

## Metadata
- O*NET occupation: Paralegals and Legal Assistants (23-2011.00)
- O*NET tasks (verbatim from O*NET):
  - Prepare affidavits, legal correspondence, or other documents for attorneys.
  - Organize and maintain documents in paper or electronic filing systems.
  - Meet with clients or other professionals to discuss details of a case.
  - Investigate facts or law to determine causes of action or to prepare cases.
- O*NET skills (Skills section): Reading Comprehension, Critical Thinking, Active Listening, Writing.
- Web search allowed: No (self-contained in the contract document).
- Multimodal: No (a single prose document).
- Time estimate: 5 to 6 hours by hand (read the full agreement, amendment, and exhibit, identify each dated obligation, resolve the supersession and the conditionals, compute the chained deadline and every calendar-day and business-day date against the holiday calendar with the correct rolling, and build the workbook with live date formulas).
