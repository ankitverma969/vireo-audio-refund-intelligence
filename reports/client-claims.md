# Vireo Audio — Client Email Claims Reconciliation

> **Objective**: Factual and empirical evaluation of specific executive statements in `email-thread.txt` against the reconciled canonical dataset.

---

## Claim 1: Finance Export Sums to 'Well Over a Crore a Quarter'

- **Speaker**: Arjun Mehta, Finance Controller
- **Claimed**: Quarterly refund export exceeds ₹1 Crore per quarter (observed ~₹3.84 Crore/qtr on naive export).
- **Observed**: Raw export sum across 6 quarters is **₹230,124,081.00** (~₹23.01 Crore). However, this total reflects legacy Freshdesk storing monetary amounts in paise/native minor units, requiring division by 100 to convert to INR. Stored legacy values are 100x the INR representation. In addition, 638 tickets were re-imported duplicates across systems.
- **Reconciled Reality**: When legacy amounts are normalized (`raw_amount / 100`) to standard INR and duplicate re-imports are resolved to helpdesk canonical records, the true 18-month refund spend is **₹6,709,932.00**, or **₹1,118,322.00 (~₹11.18 Lakh) per quarter**.
- **Interpretation**: The Finance Controller's raw export was mathematically inflated because legacy Freshdesk stored monetary amounts in paise/native minor units, requiring division by 100 to convert to INR. Stored legacy values are 100x the INR representation. Reconciled reality disproves the ₹1 Crore/quarter run-rate while preserving the essential distinction between the raw stored amount and the normalized INR amount.

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
- **Evaluation Status**: **Not supported by the observed data.**
- **Observed Empirical Data**:
  - **2025 Q3 Mean CSAT**: **3.478** (826 responses, 44.8% response rate, median 3.0)
  - **2025 Q4 Mean CSAT**: **3.507** (1,242 responses, 46.4% response rate, median 4.0)
  - **Observed Change**: **+0.029 points** (Q3 mean CSAT = 3.478, Q4 mean CSAT = 3.507, observed change = +0.029 points, not +0.40)
  - **Refund Outlay Increase**: Rose from ₹1,207,091.00 in Q3 to ₹1,627,575.00 in Q4 (**+34.8% growth**, refund outlay increased 34.8%).
- **Interpretation**: The claim is **not supported by the observed data**. Q3 mean CSAT = 3.478, Q4 mean CSAT = 3.507, and the observed change = +0.029 points, while refund outlay increased 34.8%. Crucially, this analysis does NOT establish causality between the operational policy change and CSAT/refund movement.

---

## Claim 4: Spot Checks Found Customers Receiving Both a Refund and a Replacement

- **Speaker**: Neha Kulkarni, Support Operations Manager
- **Claimed**: Spot check of twenty tickets revealed a couple where the customer received both a new unit and a refund; assumed to be 'probably one-offs'.
- **Observed Empirical Data**:
  - **Total Double-Dip Indicators**: Exactly **166 canonical refund tickets** had both a refund and replacement indicator.
  - **Total Cash Refund Outlay**: **₹574,191.00**.
  - **Order Linkage Breakdown**: **158 tickets** are unambiguously order-linked (quoted order or single fallback match) and **8 tickets** remain ambiguous.
- **Interpretation**: 166 canonical refund tickets had both a refund and replacement indicator; 158 are unambiguously order-linked and 8 remain ambiguous. The total refund cash outlay is ₹574,191.00; replacement inventory/logistics cost is additional and not included in that cash figure.