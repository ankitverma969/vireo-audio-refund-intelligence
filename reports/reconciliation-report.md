# Vireo Audio — Support Ticket & Refund Reconciliation Report

> **Document Status**: Production Quality Reconciliation
> **Auditing Standard**: Deterministic, auditable rule-based normalization layer.

---

## 1. Executive Summary

This reconciliation report documents the deterministic transformation of Vireo Audio's raw support ticket export into a verified canonical dataset.

### Golden Benchmark Verification:
- **Canonical Refund Tickets**: **2,340** (Matches golden benchmark of 2,340).
- **Reconciled Refund Total**: **Rs 6,709,932.00** (Matches golden benchmark of Rs 6,709,932.00).
- **Quarterly Average Spend**: **Rs 1,118,322.00** (~Rs 11.18 Lakh / quarter across 6 quarters).
- **Reconciliation Exceptions**: **0** (0 unexpected duplicate patterns).

---

## 2. Core Reconciliation Metrics

| Metric | Value | Audit Rationale |
| :--- | :--- | :--- |
| **1. Raw Ticket Rows** | 12,238 | Full export row count including re-imports |
| **2. Unique Ticket IDs** | 11,600 | Distinct operational ticket entities |
| **3. Duplicate Ticket IDs** | 638 | Ticket IDs appearing >1 time |
| **4. Duplicate Rows** | 1,276 | Total rows participating in duplicate groups |
| **5. Migration Pairs** | 638 | Verified pairs (`helpdesk` + `legacy_fd`) |
| **6. Canonical Ticket Count** | 11,600 | De-duplicated canonical entities (11,600 unique) |
| **7. Raw Refund Total** | Rs 230,124,081.00 | Un-normalized sum (Paise + Duplicates: ~23.01 Cr) |
| **8. Normalized Refund Total (with Duplicates)** | Rs 7,070,943.00 | Legacy divided by 100, but duplicates kept (~70.71 L) |
| **9. Reconciled Refund Total** | **Rs 6,709,932.00** | Fully reconciled canonical reality (~67.10 L) |
| **10. Refund Count (Before / After)** | 2,465 / 2,340 | 125 duplicate refund records resolved to canonical |
| **11. Reconciliation Exceptions** | 0 | Groups failing automated rule verification |
| **12. Ambiguous Order Matches** | 707 | Unquoted tickets matching >1 orders (not guessed) |
| **13. Unmatched Orders** | 0 | Tickets with zero order matches |

---

## 3. Order Reference Resolution

| Match Category | Tickets | Share (%) | Resolution Logic |
| :--- | :--- | :--- | :--- |
| **Quoted Valid** | 7,701 | 66.4% | Order ID quoted by customer and verified in `orders.csv` |
| **Fallback Single Match** | 3,192 | 27.5% | Unquoted order resolved uniquely via `customer_id + product_sku` |
| **Ambiguous Fallback** | 707 | 6.1% | Multiple orders found for customer + SKU; flagged without guessing |
| **Unmatched** | 0 | 0.0% | Zero candidate orders found |

---

## 4. Named Reconciliation Rules Applied

### RULE 1: Migration Duplicate Pair Resolution
- **Condition**: Group size == 2, sources == `{'helpdesk', 'legacy_fd'}`. Non-monetary fields match 100%. If refund present, legacy amount / helpdesk amount == 100.00x.
- **Action**: Designate `helpdesk` row as `canonical_record = True`, `reconciliation_status = 'reconciled_migration_pair'`. The legacy row is retained in audit trace as superseded.
- **Applied Count**: Exactly **638 ticket IDs (1,276 rows)** reconciled successfully.

### RULE 2: Unique Record Preservation
- **Condition**: Group size == 1 (ticket ID appears once).
- **Action**: Set `canonical_record = True`, `reconciliation_status = 'unique_record'`, `canonical_source = source_system`.
- **Applied Count**: Exactly **10,962 tickets** preserved as unique.

### RULE 3: Anomaly / Exception Isolation
- **Condition**: Any duplicate group failing Rule 1 criteria.
- **Action**: Mark `reconciliation_status = 'reconciliation_exception'`. Retain all rows without guessing.
- **Applied Count**: **0 exceptions** in the Set C dataset.
