# Vireo Audio — Refund Intelligence & Support Analytics

Production-quality data audit, multi-source reconciliation, and refund intelligence engine for **Vireo Audio Support Tickets (Set C)**.

---

## 1. Project Overview & Engagement Context

This repository houses the audit foundation and analytics engine for Vireo Audio's executive leadership and Finance Controller ahead of the upcoming Board meeting. 

### The Core Problem:
- **Finance Controller (Arjun Mehta)** observed that raw helpdesk exports summed to **>Rs 1 Crore per quarter** (over Rs 23 Crore across 6 quarters), suspecting severe data corruption or revenue leakage.
- **Helpdesk Administrator (Sameer Qureshi)** reported operational refunds running at **~Rs 11 Lakh per quarter**.
- **Head of Customer Experience (Priya Raman)** claimed frontline leniency drove CSAT up by **+0.4** in Q4 2025.

### Root Cause Discovered:
1. **Paise vs. Rupees Denomination**: Legacy Freshdesk (`legacy_fd`) stored monetary values in native subunits (**Paise**, 1/100th of an INR Rupee). The new helpdesk (`helpdesk`, launched 14 Sep 2025) stores values in standard **Rupees**.
2. **Migration Re-import Duplication**: 638 tickets were re-imported during reconciliation and appear twice (once under `legacy_fd` and once under `helpdesk`).
3. **Reconciled Reality**: When legacy records are normalized (`legacy_amount / 100`) and duplicate re-imports are resolved using `helpdesk` as canonical, true refunds total **Rs 6,709,932.00 across 18 months**, averaging **Rs 1,118,322.00 per quarter (~Rs 11.18 Lakh/quarter)**. This perfectly confirms the Helpdesk Administrator's operational observation.

---

## 2. Directory Structure

```text
vireo-audio-refund-intelligence/
│
├── data/
│   ├── raw/                       # Raw immutable source files
│   │   ├── agents.csv
│   │   ├── customers.csv
│   │   ├── email-thread.txt
│   │   ├── orders.csv
│   │   ├── products.csv
│   │   ├── README.txt
│   │   ├── support-policy.pdf
│   │   └── tickets.csv
│   └── processed/                 # Canonical processed datasets
│       ├── canonical_tickets.parquet
│       ├── canonical_tickets.csv
│       └── canonical_refunds.csv
│
├── src/
│   ├── __init__.py                # Package declaration
│   ├── config.py                  # Policy constants & dynamic path resolution
│   ├── loader.py                  # Schema validation & immutable data loaders
│   ├── audit.py                   # Comprehensive audit engine & CLI
│   ├── normalize.py               # Deterministic reconciliation & normalization layer
│   └── analyze.py                 # Business refund analysis & anomaly detection
│
├── tests/
│   ├── test_audit.py              # Schema, duplicate, parsing, & integrity tests
│   ├── test_normalize.py          # 18-point normalization & reconciliation suite
│   └── test_analyze.py            # Business refund analysis & anomaly verification
│
├── reports/
│   ├── data-audit.md              # Initial data audit report
│   ├── data_audit_summary.json    # Machine-readable audit summary
│   ├── reconciliation-report.md   # Deterministic reconciliation report
│   ├── reconciliation_summary.json # Machine-readable reconciliation summary
│   ├── analysis-summary.md        # Comprehensive business analytics report
│   ├── client-claims.md           # Claim vs reality audit report
│   ├── ai-opportunity.md          # AI opportunity assessment & classifier proposal
│   └── *.csv                      # Detailed tabular breakdowns & review flags
│
├── docs/
│   └── source-context.md          # Policy synthesis & canonical reconciliation rules
│
├── app/                           # Future analytics/AI application module
│
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Minimal production dependencies
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment variable template
└── README.md                      # Project documentation
```

---

## 3. Quick Start & Execution

### Prerequisites:
- Python 3.10+
- Virtual environment (recommended)

### Installation:
```bash
pip install -r requirements.txt
```

### Run the Data Audit:
Execute the unified audit CLI to validate schemas, verify referential integrity, calculate reconciliation totals, and regenerate audit reports:
```bash
python -m src.audit
```
Outputs: `reports/data-audit.md`, `reports/data_audit_summary.json`

### Run the Normalization & Reconciliation Pipeline:
Execute the deterministic reconciliation pipeline to generate canonical datasets and reconciliation reports:
```bash
python -m src.normalize
```
Outputs:
- `data/processed/canonical_tickets.parquet`
- `data/processed/canonical_tickets.csv`
- `data/processed/canonical_refunds.csv`
- `reports/reconciliation-report.md`
- `reports/reconciliation_summary.json`

### Run Business Refund & Anomaly Analysis:
Execute the analytics pipeline to generate monthly summaries, agent/team breakdowns, double-dip exception audits, review flags, and executive narratives:
```bash
python -m src.analyze
```
Outputs:
- `reports/monthly_refunds.csv` & `monthly_refunds.md`
- `reports/refund_by_reason.csv`
- `reports/refund_by_agent.csv`
- `reports/refund_by_team.csv`
- `reports/refund_reason_agent.csv`
- `reports/refund_replacement_exceptions.csv`
- `reports/gw_other_analysis.csv`
- `reports/refund_review_flags.csv`
- `reports/client-claims.md`
- `reports/ai-opportunity.md`
- `reports/analysis-summary.md`

### Run Automated Test Suite:
Run the complete test suite (48 automated tests covering schemas, duplicates, monetary conversion, reconciliation, business analysis, and immutability):
```bash
pytest -v
```

---

## 4. Key Metrics & Findings Summary

| Metric | Raw Export Value | Reconciled Value | Notes |
| :--- | :--- | :--- | :--- |
| **Total Tickets** | 12,238 | 11,600 unique | 638 re-imported duplicates (1,276 rows) |
| **Total Refunds** | Rs 230,124,081.00 | **Rs 6,709,932.00** | 100x Paise adjustment on legacy records |
| **Quarterly Average** | ~Rs 3.84 Crore/qtr | **Rs 1,118,322.00 (~11.18 L/qtr)** | Reconciles Finance vs. Helpdesk debate |
| **Double-Dips** | N/A | **166 unique tickets** | Both refund and replacement unit issued |
| **GW-OTHER Concentration** | N/A | **924 tickets > Rs 500** | 88.8% of GW-OTHER refunds exceed Rs 500 cap; exception pattern requiring text investigation |
| **Replacements (General)**| N/A | **1,100 issued by Tier 1** | Total replacements issued generally; non-warranty vs certified warranty replacements must be distinguished |
| **CSAT Shift (Q4)** | Claimed: +0.4 | **Observed: +0.03** | Mean rose from 3.48 to 3.51 (not +0.4) |
| **SLA Breaches** | N/A | **2,476 tickets (21.3%)** | Rs 866,600.00 in contractual breach credits |

---

## 5. Authoritative References

- `docs/source-context.md`: Complete synthesis of business policies, SLAs, contact costs, tier rules, and canonical reconciliation rules.
- `reports/data-audit.md`: In-depth analytical and empirical audit report.
- `reports/reconciliation-report.md`: Formal reconciliation report and golden benchmark verification.
