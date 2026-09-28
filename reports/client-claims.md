# Vireo Audio — Client Email Claims Reconciliation

> **Objective**: Factual and empirical evaluation of specific executive statements in `email-thread.txt` against the reconciled canonical dataset.

---

## Claim 1: Finance Export Sums to 'Well Over a Crore a Quarter'

- **Speaker**: Arjun Mehta, Finance Controller
- **Claimed**: Quarterly refund export exceeds ₹1 Crore per quarter (observed ~₹3.84 Crore/qtr on naive export).
- **Observed**: Raw export sum across 6 quarters is **₹230,124,081.00** (~₹23.01 Crore). However, in `legacy_fd`, monetary amounts were stored in **Paise** (1/100 INR), and **638 tickets were re-imported duplicates**.
- **Reconciled Reality**: When legacy amounts are normalized (`/100`) and duplicate re-imports are resolved to helpdesk canonical records, the true 18-month refund spend is **₹6,709,932.00**, or **₹1,118,322.00 (~₹11.18 Lakh) per quarter**.
- **Interpretation**: The Finance Controller's raw export was mathematically inflated by 100x for pre-September 2025 records. Reconciled reality disproves the ₹1 Crore/quarter run-rate.

---

## Claim 2: Helpdesk Report Says Refunds Run 'Around Rs 11 Lakh a Quarter'

- **Speaker**: Sameer Qureshi, Helpdesk Administrator
- **Claimed**: Helpdesk operational reports show refunds running around ₹11 Lakh per quarter.
- **Observed**: Fully reconciled canonical refund spend across all 6 quarters is **₹6,709,932.00**.
- **Quarterly Average**: **₹1,118,322.00 (~₹11.18 Lakh per quarter)**.
- **Interpretation**: **Confirmed**. Sameer Qureshi's figure aligns with the reconciled canonical data to within ₹18,000 per quarter.

---

## Claim 3: Leniency in Q4 2025 Drove CSAT Up by 0.4

- **Speaker**: Priya Raman, Head of Customer Experience
- **Claimed**: Frontline stopped arguing with customers in Q4, and CSAT went up by **+0.4** in the same period.
- **Observed Empirical Data**:
  - **2025 Q3 CSAT Mean**: **3.478** (826 responses, 44.8% response rate, median 3.0)
  - **2025 Q4 CSAT Mean**: **3.507** (1,242 responses, 46.4% response rate, median 4.0)
  - **Actual CSAT Shift**: **+0.029 points** (only +0.03, not +0.40)
  - **Refund Spend Surge**: Rose from ₹1,207,091.00 in Q3 to ₹1,627,575.00 in Q4 (**+34.8% growth**).
- **Interpretation**: The data does **not** support the claim of a +0.4 CSAT increase. Mean customer satisfaction was virtually flat (+0.03 points), despite a 34.8% increase in quarterly refund cash outlay.

---

## Claim 4: Spot Checks Found Customers Receiving Both a Refund and a Replacement

- **Speaker**: Neha Kulkarni, Support Operations Manager
- **Claimed**: Spot check of twenty tickets revealed a couple where the customer received both a new unit and a refund; assumed to be 'probably one-offs'.
- **Observed Empirical Data**:
  - **Total Double-Dip Tickets**: Exactly **166 canonical tickets** (7.1% of all refund tickets).
  - **Total Refund Cash Outlay**: **₹574,191.00** (plus inventory and shipping costs of unit replacement).
  - **Confirmed Order-Linked**: **158 tickets** (quoted order or unambiguous single fallback match).
  - **Ambiguous Order-Linked**: **8 tickets**.
- **Interpretation**: **Confirmed and widespread**. These are not isolated 'one-offs'; 166 separate orders were provided both full cash reimbursement and a replacement device, representing a systemic operational exception across 6 frontline teams.