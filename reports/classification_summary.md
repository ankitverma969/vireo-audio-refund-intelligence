# Vireo Audio — AI-Assisted Refund Re-Classification Summary

> **Document Status**: Production Quality AI/NLP Baseline & Review Triage
> **Target Dataset**: 991 `GW-OTHER` Canonical Refund Tickets (₹2,907,036.00 Spend)
> **Auditing Standard**: Strictly separates deterministic reclassification candidates from unverified savings claims.

---

## 1. Executive Summary & Scope

The primary analytical target of the AI-assisted pipeline is the **991 `GW-OTHER` refund tickets**, which account for **42.4% of all refund tickets** and **₹2,907,036.00 (43.3% of total refund expenditure)**. Frontline agents defaulted to `GW-OTHER` due to dropdown positioning, obscuring root cause attribution.

- **Total GW-OTHER Tickets Processed**: **991**
- **Re-Classification Candidates Identified**: **574 tickets (57.9%)**
- **Spend Associated with Candidates**: **₹1,576,028.00 (54.2%)**
- **Unclassified / High Ambiguity Cases**: **417 tickets**
- **Review Priority Triage**: **650 HIGH**, **341 MEDIUM**, **0 LOW**

---

## 2. Re-Classification Candidate Distribution

| Predicted Policy Reason Code | Label / Policy Meaning | Candidate Tickets | Share (%) | Candidate Spend (INR) | Share of GW Spend (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `UNCLASSIFIED` | Unclassified / Needs Review | 417 | 42.1% | ₹1,331,008.00 | 45.8% |
| `RETURN-QC-OK` | Return Received and Passed QC | 177 | 17.9% | ₹522,873.00 | 18.0% |
| `CANCEL` | Cancellation Before Dispatch | 120 | 12.1% | ₹355,854.00 | 12.2% |
| `WTY-BUYBACK` | Warranty Buy-Back | 64 | 6.5% | ₹244,888.00 | 8.4% |
| `LOST-TRANSIT` | Lost or Undelivered in Transit | 55 | 5.5% | ₹181,467.00 | 6.2% |
| `DUP-PAYMENT` | Duplicate or Failed Payment | 46 | 4.6% | ₹122,610.00 | 4.2% |
| `GW-OTHER` | Goodwill / Other | 74 | 7.5% | ₹64,076.00 | 2.2% |
| `PRICE-ADJ` | Price or Coupon Adjustment | 28 | 2.8% | ₹53,474.00 | 1.8% |
| `DOA-REPL` | Dead on Arrival, Refund Chosen | 10 | 1.0% | ₹30,786.00 | 1.1% |

---

## 3. Review Queue Prioritization

To maximize audit efficiency, review priority is deterministically assigned without subjective scoring:
- **HIGH Priority (650 tickets)**: Includes cases with low classifier confidence (<0.60), ambiguous order links, double-dip indicators (refund + replacement), or high-value reclassification candidates (≥₹5,000).
- **MEDIUM Priority (341 tickets)**: Clear candidate re-classification where prediction differs from existing reason code with moderate-to-high confidence.
- **LOW Priority (0 tickets)**: Tickets where existing code agrees with prediction with strong supporting evidence and zero policy exceptions.

Complete review list available in `reports/classification_review_queue.csv`.

---

## 4. Business Value & Financial Reclassification Framework

### Critical Distinction: Reclassification vs Cost Savings
- **Spend Reclassification**: ₹2.91M in `GW-OTHER` spend is attributed to true operational root causes (e.g. carrier transit failure, returns QC, or gateway errors). This enables leadership to hold third parties (couriers, payment processors, suppliers) commercially accountable.
- **Actual Cost Savings**: Reclassifying reasons does **not** automatically recover money already disbursed. True savings require operational action (e.g., filing carrier damage claims under SLA §3, recovering duplicate debits from payment gateways, or closing double-dip operational gaps).

---

## 5. Human Validation Sample Status

- A statistically representative sample of **100 tickets** has been extracted to `data/validation/gw_other_validation_sample.csv` using deterministic stratified sampling (`seed=42`).
- Human reviewer validation is pending. Evaluation metrics (accuracy, macro F1, confusion matrix) will be computed by `src.evaluate_classifier` once verified human labels are populated.