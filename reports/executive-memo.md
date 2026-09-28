# EXECUTIVE MEMORANDUM

**TO:** Arjun Mehta, Finance Controller, Vireo Audio  
**FROM:** Financial Data Audit & Analytics Team  
**DATE:** September 28, 2026  
**SUBJECT:** Refund Reconciliation, Root Cause Analysis & Policy Triage — Audit Period January 2025 – June 2026  

---

### Executive Summary

Across the 18-month audit period, Vireo Audio processed **11,600 canonical customer support tickets**, resulting in **2,340 canonical refunds** totalling **₹67.10 lakh (₹6,709,932) in reconciled refund spend**, with an **average refund of ₹2,867.49**. Quarterly spend averaged **~₹11.18 lakh/quarter**. The initial Finance export figure that appeared to exceed ₹1 crore per quarter has been fully explained and reconciled (see Section 1 below).

---

### 1. Why Did the Finance Export Appear to Show >₹1 Crore per Quarter?

The initial raw export figure (>₹23 crore total) was caused by **two independent data-quality artefacts** introduced during the legacy-to-modern platform migration:

1. **Minor-unit storage in legacy records.** The legacy Freshdesk platform (`legacy_fd`, active through 14 September 2025) stored monetary amounts in native minor units (paise), requiring division by 100 to convert to INR. The modern helpdesk platform records amounts in standard Rupees. Without this conversion, legacy records appeared 100× their true INR value.
2. **Migration duplication.** 638 tickets were re-imported during the platform cutover and appeared twice in the raw export. Deduplicating these against canonical helpdesk records eliminated 1,276 duplicated rows.

*Conclusion:* This is a data-structure and system-migration finding. Finance's underlying records are fully reconcilable once normalization and deduplication are applied. Reconciled quarterly refund spend is **~₹11.18 lakh** — well within historical business expectations.

---

### 2. Major Refund Reasons & Operational Distribution

All reconciled refunds map to the eight Support Policy §5 reason codes:

| Reason Code | Description | Tickets | Spend (INR) | % Spend |
|---|---|---|---|---|
| **GW-OTHER** | Goodwill / Other (catch-all) | 991 | ₹29,07,036 | 43.3% |
| **RETURN-QC-OK** | Return Passed QC | 452 | ₹11,81,386 | 17.6% |
| **DUP-PAYMENT** | Duplicate Payment | 321 | ₹8,84,586 | 13.2% |
| **CANCEL** | Pre-Dispatch Cancellation | 222 | ₹6,12,950 | 9.1% |
| **DOA-REPL** | Dead-on-Arrival Replacement | 147 | ₹4,71,190 | 7.0% |
| **WTY-BUYBACK** | Warranty Buy-Back | 89 | ₹2,89,154 | 4.3% |
| **PRICE-ADJ** | Price Adjustment | 71 | ₹2,07,073 | 3.1% |
| **LOST-TRANSIT** | Lost in Transit | 47 | ₹1,56,557 | 2.3% |

---

### 3. GW-OTHER: Catch-All Code Requiring Management Action

`GW-OTHER` absorbed legitimate returns, cancellations, and warranty cases because it appeared first in the agent dropdown menu.

- **879 GW-OTHER tickets exceed the stated ₹500 goodwill credit threshold.** These are **review candidates requiring human text and policy validation — they are not confirmed policy violations.** The ₹500 cap applies specifically to goodwill credits; agents likely miscoded legitimate returns or cancellations under this catch-all code rather than applying non-compliant goodwill credits.
- **574 candidate reclassifications (₹15,76,028):** Rule-based NLP analysis identified these tickets as containing explicit text evidence matching other policy codes. Correcting reason codes reallocates spend to its true commercial driver. **This ₹15.76 lakh is not cash savings — it is a cost-attribution correction opportunity that requires human confirmation before any accounting modification.**

---

### 4. Operational Exceptions

- **Refund + Replacement Indicators:** **166 tickets** show both a cash refund and a replacement unit dispatch (total refund cash: ₹5,74,191). **158 are unambiguously order-linked**; **8 are ambiguous**. Require verification against warehouse manifests to prevent duplicate fulfilment costs.
- **Ambiguous Order Matches:** **707 tickets overall** match multiple order records; require customer-order data sanitation.
- **Quarterly Trend:** Refund spend rose from ₹12,07,091 (Q3 2025) to **₹16,27,575 (Q4 2025) (+₹4,20,484 / +34.8%)**. CSAT shifted from 3.478 to 3.507 (+0.029 points). Observed data **does not establish any causal relationship** between operational changes and satisfaction scores.
- **Tier Separation:** High Tier 1 refund volume reflects dedicated Returns Desk and Billing Escalations roles, not policy evasion. Tier 2 Escalations appropriately handles warranty buy-backs.

---

### 5. Actionable Management Recommendations

1. **Restructure the GW-OTHER dropdown.** Remove from the top position; require a mandatory reason subcategory selection to reduce catch-all usage.
2. **Enforce goodwill credit thresholds.** Require Team Lead counter-sign for any goodwill credit above the stated ₹500 policy cap. *(Proposed management control: implement a hard system block for values above ₹1,000, subject to operations sign-off.)*
3. **Close double-dip process gaps.** Add a hard-stop preventing concurrent refund and replacement execution on identical order IDs.
4. **Formalise monthly reconciliation.** Institute a monthly cadence matching helpdesk refund records against payment gateway settlements.
5. **Review the 574 reclassification candidates.** Operations team leads to review flagged GW-OTHER tickets before any accounting change. No ledger entry may be changed without human sign-off.
6. **Verify 166 refund + replacement exceptions** against warehouse return receipts and carrier manifests within 30 days.
7. **Use AI classification as decision-support only.** All ledger changes require human confirmation; AI recommendations are strictly advisory.