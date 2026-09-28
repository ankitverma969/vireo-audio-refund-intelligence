# Vireo Audio — Comprehensive Refund & Support Business Analysis

> **Document Status**: Production Quality Business Analytics
> **Scope**: 18 Months (1 Jan 2025 – 30 Jun 2026), 11,600 Canonical Tickets, 2,340 Reconciled Refunds.

---

## 1. Executive Data Snapshot

- **Total Canonical Tickets**: **11,600**
- **Total Refund Tickets**: **2,340** (20.2% refund rate)
- **Total Reconciled Refund Spend**: **₹6,709,932.00**
- **Quarterly Average Refund Spend**: **₹1,118,322.00 (~₹11.18 Lakh / quarter)**
- **Average Refund per Refund Ticket**: **₹2,867.49**
- **Total Double-Dip Exceptions**: **166 tickets** (₹574,191.00)
- **GW-OTHER Concentration**: **991 tickets** (₹2,907,036.00, 43.3% of total spend)

---

## 2. Monthly Refund Trends

- Peak refund volume occurred in **December 2025 (205 tickets, ₹612,790.00)**, coinciding with festival season sales.
- Monthly refund rate has remained stable between **19.1% and 22.8%** throughout the 18-month timeframe.
- Complete tabular data available in `reports/monthly_refunds.csv` and `reports/monthly_refunds.md`.

---

## 3. Reason Code Concentrations

| Reason Code | Tickets | Share (%) | Total Spend (INR) | Share of Spend (%) | Avg Refund (INR) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GW-OTHER` | 991 | 42.4% | Rs 2,907,036.00 | 43.3% | Rs 2,933.44 |
| `RETURN-QC-OK` | 452 | 19.3% | Rs 1,181,386.00 | 17.6% | Rs 2,613.69 |
| `DUP-PAYMENT` | 321 | 13.7% | Rs 884,586.00 | 13.2% | Rs 2,755.72 |
| `CANCEL` | 222 | 9.5% | Rs 612,950.00 | 9.1% | Rs 2,761.04 |
| `DOA-REPL` | 147 | 6.3% | Rs 471,190.00 | 7.0% | Rs 3,205.37 |
| `WTY-BUYBACK` | 89 | 3.8% | Rs 289,154.00 | 4.3% | Rs 3,248.92 |
| `PRICE-ADJ` | 71 | 3.0% | Rs 207,073.00 | 3.1% | Rs 2,916.52 |
| `LOST-TRANSIT` | 47 | 2.0% | Rs 156,557.00 | 2.3% | Rs 3,331.00 |

---

## 4. Agent & Team Concentration (Tier-Aware)

### Strict Tier Separation Mandate
Per Support Policy §6, Tier 2 Escalations & Warranty agents are measured on resolution days and certified hardware RMA, not closed volume. Tier 1 and Tier 2 agents are evaluated strictly in separate cohorts:
- **Tier 1 Frontline / Returns / Billing (38 Agents)**: Handled **38 active refund agents**, issuing **2,258 refund tickets (₹6,411,197.00)**.
- **Tier 2 Escalations & Warranty (6 Agents)**: Handled **6 active refund agents**, issuing **82 refund tickets (₹298,735.00)**.
- **Concentration in Tier 1**: The top 5 Tier 1 agents (primarily Returns Desk and Billing specialists) account for **44.1% of Tier 1 refund spend**. This reflects functional specialization rather than agent misconduct.

---

## 5. Double-Dip Exceptions (Refund + Replacement)

- 166 canonical refund tickets had both a refund and replacement indicator; 158 are unambiguously order-linked and 8 remain ambiguous.
- The total refund cash outlay is **₹574,191.00**; replacement inventory/logistics cost is additional and not included in that cash figure.
- Detailed line-item breakdown with customer messages and notes available in `reports/refund_replacement_exceptions.csv`.

---

## 6. GW-OTHER Findings & Anomaly Patterns

- **879 out of 991 GW-OTHER tickets (88.7%)** are GW-OTHER refunds above the stated ₹500 goodwill threshold, serving as review candidates requiring text/policy validation.
- High concentration is directly associated with UI dropdown ordering.
- Full diagnostic available in `reports/gw_other_analysis.csv`.

---

## 7. Q3 vs Q4 Claim Evaluation

- **Observed CSAT Movement**: Q3 mean CSAT = 3.478, Q4 mean CSAT = 3.507 (observed change = +0.029 points), while refund outlay increased 34.8%; the claimed +0.40 increase is not supported by the observed data.
- **Causality Caveat**: This analysis does NOT establish causality between the operational policy change and CSAT/refund movement.
- Complete claim-by-claim analysis in `reports/client-claims.md`.

---

## 8. AI / NLP Opportunity Ahead

- High-value opportunity identified: Re-classifying 991 `GW-OTHER` refund tickets (₹2.91M spend) where agents defaulted to dropdown option 1 despite specific cancellation, return, or transit failure evidence in ticket text.
- Roadmap detailed in `reports/ai-opportunity.md`.

---

## 9. Important Methodological Caveats

1. **No Imputed Motivations**: Concentrated metrics and exception flags represent operational review candidates, not verified agent malfeasance.
2. **Ambiguous Order Preservation**: 707 canonical tickets match multiple candidate orders; they are not artificially resolved.
3. **Immutable Baseline**: All analyses stem strictly from canonical datasets without modifying raw source files.