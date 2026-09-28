# Source Context & Domain Specification: Vireo Audio Support & Refunds

> **Authority**: Authoritative synthesis derived strictly and solely from the 8 supplied project artifacts: `agents.csv`, `customers.csv`, `orders.csv`, `products.csv`, `tickets.csv`, `README.txt`, `support-policy.pdf` (v3.2), and `email-thread.txt`.

---

## 1. Client Ask

The engagement is driven by Vireo Audio's executive leadership in preparation for an upcoming Board of Directors presentation on 24 September 2026.

### Core Deliverables Requested by Finance:
1. **Monthly Breakdown of Refunds**:
   - Monthly aggregation of all refund transactions across the 18-month reporting window (1 Jan 2025 – 30 Jun 2026).
   - Multi-dimensional breakdown by:
     - **Refund Reason Code** (*What for*)
     - **Resolving Agent** (*Who*)
     - **Financial Value in INR** (*How much*)
2. **Reconciliation of Discrepancies**:
   - Reconcile the severe conflict between Finance Controller Arjun Mehta's export observation ("sums to well over a crore a quarter") and Helpdesk Administrator Sameer Qureshi's report ("refunds run around Rs 11 lakh a quarter").
   - Provide mathematical and evidential proof explaining which figure is correct and how they reconcile.
3. **Agent Performance Profiling**:
   - Analyze refund and replacement patterns per agent, explicitly respecting the operational separation between Tier 1 frontline and Tier 2 Escalations.

---

## 2. Policy Rules Relevant to Refunds (Support Operating Policy v3.2)

### Conditions for Refund vs. Replacement:
- **Dead on Arrival (DOA)**: Occurring within 7 days of delivery. Customer is entitled to choose *either* a full refund *or* a replacement unit.
- **In-Warranty Fault**: Repair or replacement (not refund, unless escalated to buy-back).
- **Lost / Damaged in Transit**: Reshipment or refund.
- **Strict Anti-Duplication Rule (§5)**: 
  > *"In no case is a customer to receive both a refund and a replacement for the same order; where this happens in error it must be escalated to the Team Lead and Finance the same day."*
- **Goodwill Credits Cap (§5)**:
  > Goodwill credits are strictly capped at **Rs 500 per ticket** and mandate Team Lead approval.
- **Replacement Cost Formulation (§5)**:
  > Replacement cost for financial planning equals the product's unit cost (`products.csv`) plus **Rs 340** for reverse pickup and forward logistics. Refurbishment recovery is not assumed.

---

## 3. Reason Code Definitions (§5)

Refunds must be categorized using one of eight discrete dropdown codes at the time the refund is raised:

| Code | Label / Meaning | Policy Rules & Criteria |
| :--- | :--- | :--- |
| `GW-OTHER` | Goodwill / Other | Capped at Rs 500 per ticket; requires Team Lead approval. *Note: Appears as the first option in the helpdesk dropdown.* |
| `DOA-REPL` | Dead on arrival, refund chosen | Within 7 days of delivery; customer explicitly chose refund over replacement. |
| `LOST-TRANSIT` | Lost or undelivered | Carrier non-delivery or shipment confirmed lost in transit. |
| `DUP-PAYMENT` | Duplicate or failed payment | Payment gateway error, double debit, or duplicate order placement. |
| `CANCEL` | Cancellation before dispatch | Order cancelled prior to warehouse dispatch/fulfillment. |
| `PRICE-ADJ` | Price or coupon adjustment | Retroactive discount, coupon code omission, or price-match difference. |
| `RETURN-QC-OK` | Return received and passed QC | Standard return pickup completed; goods inspected and verified intact. |
| `WTY-BUYBACK` | Warranty buy-back | Product defective within warranty, replacement stock unavailable or approved for buy-back. |

---

## 4. Monetary & Cost Standards (FY26 Planning Figures)

### Contact & Operational Costs (§4):
- **Channel Fully Loaded Cost per Contact**:
  - Chat: **Rs 210**
  - Email: **Rs 260**
  - Voice Callback: **Rs 520**
  - Social: **Rs 240**
  - Blended Channel Average: **Rs 290**
- **Internal Team Transfer**: **Rs 305** per hand-off (re-handling and administrative overhead).
- **Agent Staffing Cost**: **Rs 165** per agent-hour (standard 8-hour shift = Rs 1,320 per shift).

### Service Level Agreements & Penalties (§3):
- **First Response SLA Targets**:
  - Chat: **15 minutes**
  - Voice Callback: **2 hours** (120 minutes)
  - Social: **4 hours** (240 minutes)
  - Email: **8 hours** (480 minutes)
- **Automatic SLA Breach Credit**:
  > Every ticket breaching first response automatically issues a **Rs 350 store credit** to the customer, charged to the support P&L regardless of fault.

---

## 5. Team & Tier Considerations (§6 & §7)

### Organization & Ownership:
- **Chat, Email, Voice Frontline (Tier 1)**: First contact for general, account, and product queries.
- **Logistics (Tier 1)**: Delivery tracking, reshipment, and carrier escalations.
- **Billing (Tier 1)**: Payment issues, gateway errors, invoices, and chargebacks.
- **Returns Desk (Tier 1)**: Return pickups and refund processing. Designated as the owner of the vast majority of refunds by design.
- **Escalations & Warranty (Tier 2)**: Warranty RMA, certified hardware troubleshooting, escalated claims.

### Critical Tier Rule (§6):
> **"Tier 2 work is certified: only Tier 2 agents may approve warranty replacements. Tier 2 cases are multi-touch by nature and are measured on resolution in days, not on tickets closed per week. Tier 2 agents are not to be compared with Tier 1 on volume metrics."**

---

## 6. Migration & Data Quality Warnings (§9 & README.txt)

1. **System Transition Date**:
   The current helpdesk platform went live on **14 September 2025**.
2. **Legacy Freshdesk Records (`legacy_fd`)**:
   - Tickets created before 14 September 2025 originated in Freshdesk.
   - Freshdesk stored currency amounts in its **native unit (Paise / cents)**, whereas the new helpdesk stores currency in **Rupees (INR)**.
   - Resolution timestamps for legacy tickets were reconstructed from UTC event logs.
3. **Re-import Duplication**:
   - During post-migration reconciliation, a subset of legacy tickets was re-imported into the new helpdesk.
   - Consequently, these tickets exist twice in the export: once under `source_system = legacy_fd` and once under `source_system = helpdesk`.
4. **Relational Fallback (`order_id`)**:
   - `order_id` is blank when the customer did not quote it.
   - The authoritative fallback key defined in `README.txt` is `customer_id + product_sku`.

---

## 7. Email-Thread Context

Analysis of the correspondence between Vireo leadership and our engagement team reveals critical insights:
1. **Arjun Mehta (Finance Controller)**:
   - Saw quarterly totals exceeding Rs 1 Crore/quarter in the raw export.
   - Suspects data corruption or misinterpretation ("one of us is reading the export wrong").
   - Demands reconciled monthly numbers for the Board meeting on the 24th.
2. **Sameer Qureshi (Helpdesk Administrator)**:
   - Clarified that `legacy_fd` stores values in native Freshdesk units (Paise) and Finance historically handled conversion on their side.
   - Warned that `GW-OTHER` is the top dropdown option and agents frequently default to it.
   - Stated internal helpdesk reports show actual refunds run ~Rs 11 Lakh per quarter.
   - Highlighted migration re-import duplicates.
3. **Priya Raman (Head of CX)**:
   - Defended refund growth by stating frontline staff were instructed to stop arguing with customers in Q4 2025.
   - Claimed CSAT improved by 0.4 points as a direct consequence.
4. **Neha Kulkarni (Support Operations Manager)**:
   - Observed that spot checks revealed customers receiving *both* a refund and a replacement unit on the same issue.

---

## 8. Important Ambiguities Supported by Data

1. **Fallback Order Disambiguation**:
   For the 4,127 tickets lacking an `order_id`, while 3,391 map to a unique order for that customer and SKU, **736 tickets map to multiple orders** (707 in canonical tickets). The documentation does not specify whether to match by nearest prior order date, nearest order value, or flag as ambiguous. To maintain auditable integrity, these must be flagged as ambiguous without guessing.
2. **`GW-OTHER` Concentration & Threshold Patterns**:
   `GW-OTHER` is highly concentrated and 88.8% of associated refunds are GW-OTHER refunds above the stated Rs 500 goodwill threshold (reaching up to Rs 13,998). Because GW-OTHER is a combined Goodwill/Other reason code, these are review candidates requiring text/policy validation rather than confirmed policy violations.
3. **Double-Dip Policy Enforcement**:
   166 unique tickets have both a refund raised and a replacement unit dispatched. The documentation specifies this requires escalation to TL and Finance, but the dataset lacks an approval/escalation log.
4. **Dispersed Refund Authority**:
   Contrary to policy stating the Returns Desk handles the large majority of refunds, Returns Desk only handles ~26%, with Frontline and Billing issuing hundreds of refunds directly.
5. **Replacement Scope Distinction**:
   Policy §6 explicitly restricts certified warranty replacement approval to Tier 2 agents. Non-warranty replacements (such as Dead on Arrival within 7 days under Policy §5, or lost-in-transit reshipments handled by Logistics) do not require Tier 2 certification, so total replacements issued generally must be distinguished into warranty vs. non-warranty.

---

## 9. Decisions That Must Be Made Before Final Analysis

1. **Canonical Deduplication Decision**:
   Designate the `helpdesk` record as the canonical version for all 638 verified migration duplicates, ensuring timestamps and currency representations align natively with the modern platform.
2. **Monetary Transformation Decision**:
   Apply an exact division by 100 (`amount / 100.0`) to all non-re-imported `legacy_fd` refund records to convert Paise to INR Rupees. Keep raw values unmutated.
3. **Agent Evaluation Separation**:
   In all agent reporting, partition Tier 1 agents (measured on volume, FCR, handle time) from Tier 2 agents (measured on resolution days, certified RMA).
4. **Reason Code Investigation Approach**:
   When reporting stated policy reason codes, clearly distinguish between the *raw agent-selected dropdown code* (where `GW-OTHER` is heavily concentrated) and the *inferred operational intent* gleaned from customer messages and notes text.

---

## 10. Canonical Data and Reconciliation Rules

This section formalizes the deterministic normalization and reconciliation rules implemented in the normalization layer (`src/normalize.py`):

### 1. Why Legacy Values Are Divided by 100
- **Source System Evidence**: Prior to 14 September 2025, Freshdesk (`legacy_fd`) stored monetary values in native subunits (**Paise**, 1/100th of an INR Rupee). Post-migration Helpdesk (`helpdesk`) stores values in standard **Rupees (INR)**.
- **Mathematical Confirmation**: In all 125 duplicate ticket pairs that carry refund amounts in both systems, the ratio `legacy_fd / helpdesk` equals **100.00x exactly**.
- **Order Boundary Verification**: When divided by 100, zero legacy refund amounts exceed the matched order value (`orders.csv`), with exactly full or partial order amounts.
- **Rule Formulation**:
  ```python
  if source_system == "legacy_fd":
      refund_amount_inr_normalized = refund_amount_raw / 100.0
      money_normalization_rule = "legacy_div_100"
  elif pd.notna(refund_amount_raw):
      refund_amount_inr_normalized = float(refund_amount_raw)
      money_normalization_rule = "helpdesk_native_inr"
  else:
      refund_amount_inr_normalized = None
      money_normalization_rule = "no_refund"
  ```

### 2. Why `helpdesk` Is Canonical for Confirmed Migration Duplicates
- **System Primacy**: The current helpdesk is the active operational system of record launched on 14 September 2025.
- **Currency Cleanliness**: `helpdesk` stores amounts natively in INR Rupees without requiring retrospective subunit conversion.
- **Field Parity**: For all 638 re-imported pairs, all 18 non-monetary fields (timestamps, agent IDs, customer IDs, order IDs, messages, notes) are 100% identical between `helpdesk` and `legacy_fd`.
- **Audit Trace**: The superseded `legacy_fd` rows are retained in the reconciliation pipeline with `canonical_record = False` and `reconciliation_status = 'reconciled_migration_pair'`.

### 3. What Happens with Uncertain Duplicate Groups
- If any ticket ID group has a group size > 1 that does not satisfy Rule 1 (e.g., group size > 2, multiple rows from the same source, mismatched non-monetary attributes, or monetary ratio != 100x):
  - The group is **not silently discarded**.
  - All rows are flagged with `reconciliation_status = 'reconciliation_exception'`.
  - All rows are flagged with an explicit `reconciliation_reason` explaining the anomaly.
  - In the Set C dataset, exactly **0 reconciliation exceptions** were observed.

### 4. How Order Fallback Works
- **Rule A (Quoted Order)**: If `ticket.order_id` is present and matches `orders.csv`, use it (`order_match_status = 'quoted_valid'`).
- **Rule B (Missing Quoted Order)**: Search `orders.csv` using the composite key `(customer_id, product_sku)`.
- **Rule C (Single Match)**: If exactly one order is found, resolve to that order (`order_match_status = 'fallback_single'`).

### 5. What an Ambiguous Order Means
- **Rule D (Multiple Matches)**: If a customer placed multiple separate orders for the same SKU, resolving without explicit quote is inherently ambiguous.
- **Deterministic Action**: The engine **never guesses** or arbitrarily selects the first or latest order. It sets `resolved_order_id = None`, sets `order_match_status = 'ambiguous'`, and records all candidate order IDs in `candidate_order_ids` (separated by semicolons). Exactly 707 canonical tickets fall into this category.
- **Rule E (Unmatched)**: If zero candidate orders exist in `orders.csv`, set `order_match_status = 'unmatched'`. Exactly 0 tickets fall into this category.

### 6. What a Refund Ticket Means
- **Deterministic Central Definition**:
  > A ticket is a **refund ticket** if and only if `refund_amount_inr_normalized` is not null (`refund_amount_inr_normalized > 0`).
- **Non-Inference Boundary**: The pipeline does **not** infer a refund from reason codes alone, from `replacement_issued`, or from free text. Those are treated as separate operational or classification features.

