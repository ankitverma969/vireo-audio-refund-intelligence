# AI & NLP Opportunity Specification: Text Discrepancy & Reason Re-Classification

> **Scope**: Factual assessment of where deterministic heuristics are insufficient and require semantic Natural Language Processing.

---

## 1. Where Deterministic Logic Reaches Its Limits

Deterministic rule-based pipelines successfully resolve currency scaling, migration duplication, and order joins. However, deterministic logic cannot reliably resolve **semantic mismatch** between agent UI selections and free-text customer conversations.

### Key Target Area: The `GW-OTHER` Dropdown Default
- In canonical data, **991 tickets (42.4% of all refund tickets)** carry reason code `GW-OTHER`, absorbing **₹2,907,036.00 (43.3% of all refund spend)**.
- **879 of these tickets (88.7%)** are GW-OTHER refunds above the stated ₹500 goodwill threshold (reaching up to ₹13,998.00), representing review candidates requiring text/policy validation.

---

## 2. Text Keyword Spot-Check Findings

A preliminary keyword scan found operational terms associated with specific policy scenarios in 669/991 (67.5%) GW-OTHER tickets. This suggests a substantial candidate set for reason-code reclassification, but keyword presence alone does not establish the true reason.

### Preliminary Keyword Breakdown (Indicator Scan Only):
- **Cancellation Terms**: 120 tickets contain cancellation terms before dispatch (e.g., *'cancellation request', 'cancelled before dispatch'*).
- **Return & QC Terms**: 336 tickets contain terms referencing return pickup, reverse logistics, or QC pass (e.g., *'return received', 'qc ok', 'reverse pickup'*).
- **DOA / Hardware Defect Terms**: 29 tickets describe dead-on-arrival or unboxing hardware defects.
- **Carrier / Non-Delivery Terms**: 114 tickets document courier delays, lost shipments, and transit failures.
- **Duplicate Payment Terms**: 201 tickets reference payment gateway double charges and failed debits.

### Evidentiary Distinctions:
- **Deterministic Fact**: Exactly 991 canonical refund tickets carry the `GW-OTHER` reason code, totaling ₹2,907,036.00 in reconciled spend, of which 879 tickets exceed ₹500.
- **Preliminary Keyword Evidence**: A preliminary keyword scan found operational terms associated with specific policy scenarios in 669/991 (67.5%) GW-OTHER tickets. This suggests a substantial candidate set for reason-code reclassification, but keyword presence alone does not establish the true reason.
- **Future AI/NLP Classification**: Evaluating true underlying reason codes requires deeper semantic classification and human-in-the-loop validation against a human-reviewed sample.

---

## 3. Scope & Financial Exposure for the AI Classifier

| Evaluation Dimension | Value | Business Significance |
| :--- | :--- | :--- |
| **Target Review Tickets** | **991 tickets** | High-priority tickets tagged as `GW-OTHER` |
| **Share of Refund Tickets** | **42.4%** | Over four in ten refund tickets |
| **Financial Exposure Involved** | **₹2,907,036.00** | Over 43% of total Vireo refund expenditure |
| **Spend Above ₹500 Goodwill Threshold** | **₹2,467,536.00** | Review candidates requiring text/policy validation |

---

## 4. Proposed AI Classifier Architecture

Phase 4 will evaluate an auditable NLP classification approach with validation against a human-reviewed sample.

1. **Input Features**: `customer_message`, `agent_notes`, `category`, and `product_sku`.
2. **Target Classes**: The 8 authoritative reason codes defined in Support Policy §5 (`DOA-REPL`, `LOST-TRANSIT`, `DUP-PAYMENT`, `CANCEL`, `PRICE-ADJ`, `RETURN-QC-OK`, `WTY-BUYBACK`, `GW-OTHER`).
3. **Validation & Audit Protocol**: Phase 4 will evaluate an auditable NLP classification approach with validation against a human-reviewed sample, accompanied by confidence scoring and evidence text citation.
4. **Deliverable**: An audited re-classification candidate matrix providing leadership with evaluated root cause distributions for Vireo's ₹6.71M refund spend.