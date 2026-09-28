# AI & NLP Opportunity Specification: Text Discrepancy & Reason Re-Classification

> **Scope**: Factual assessment of where deterministic heuristics are insufficient and require semantic Natural Language Processing.

---

## 1. Where Deterministic Logic Reaches Its Limits

Deterministic rule-based pipelines successfully resolve currency scaling, migration duplication, and order joins. However, deterministic logic cannot reliably resolve **semantic mismatch** between agent UI selections and free-text customer conversations.

### Key Target Area: The `GW-OTHER` Dropdown Default
- Helpdesk Admin Sameer Qureshi noted that `GW-OTHER` (Goodwill / Other) is the first option in the UI dropdown.
- In canonical data, **991 tickets (42.4% of all refund tickets)** carry reason code `GW-OTHER`, absorbing **₹2,907,036.00 (43.3% of all refund spend)**.
- **879 of these tickets (88.7%)** exceed the ₹500 policy cap for goodwill credits, with refund amounts reaching up to ₹13,998.00.

---

## 2. Text Keyword Spot-Check Findings

Preliminary inspection of `customer_message` and `agent_notes` within `GW-OTHER` tickets demonstrates that agents routinely select `GW-OTHER` for specific policy scenarios:
- **Cancellation Evidence**: 120 tickets explicitly describe cancellations before dispatch (e.g., *'cancellation request', 'cancelled before dispatch'*).
- **Return & QC Evidence**: 336 tickets explicitly reference return pickup, reverse logistics, and QC pass (e.g., *'return received', 'qc ok', 'reverse pickup'*).
- **DOA / Hardware Faults**: 29 tickets describe dead-on-arrival or unboxing hardware defects.
- **Carrier Non-Delivery**: 114 tickets document courier delays, lost shipments, and transit failures.
- **Duplicate Payments**: 201 tickets reference payment gateway double charges and failed debits.

> **Total Review Candidates**: At least **669 tickets (67.5% of all GW-OTHER refunds)** contain unmistakable operational keywords pointing to specific policy categories.

---

## 3. Scope & Financial Exposure for the AI Classifier

| Evaluation Dimension | Value | Business Significance |
| :--- | :--- | :--- |
| **Target Review Tickets** | **991 tickets** | High-priority tickets tagged as `GW-OTHER` |
| **Share of Refund Tickets** | **42.4%** | Over four in ten refund tickets |
| **Financial Exposure Involved** | **₹2,907,036.00** | Over 43% of total Vireo refund expenditure |
| **Excess Above ₹500 Goodwill Cap** | **₹2,467,536.00** | Unverified spend currently marked as goodwill |

---

## 4. Proposed AI Classifier Architecture

1. **Input Features**: `customer_message`, `agent_notes`, `category`, and `product_sku`.
2. **Target Classes**: The 8 authoritative reason codes defined in Support Policy §5 (`DOA-REPL`, `LOST-TRANSIT`, `DUP-PAYMENT`, `CANCEL`, `PRICE-ADJ`, `RETURN-QC-OK`, `WTY-BUYBACK`, `GW-OTHER`).
3. **Zero-Hallucination Constraints**: Constrained classification with prediction confidence scores and text quote citation.
4. **Deliverable**: A re-classified refund audit matrix providing leadership with the true root cause breakdown of Vireo's ₹6.71M refund spend.