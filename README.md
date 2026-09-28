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
│   ├── processed/                 # Canonical processed datasets
│   └── validation/                # Stratified human review sample
│       └── gw_other_validation_sample.csv
│
├── src/
│   ├── __init__.py                # Package declaration
│   ├── config.py                  # Policy constants & dynamic path resolution
│   ├── loader.py                  # Schema validation & immutable data loaders
│   ├── audit.py                   # Comprehensive audit engine & CLI
│   ├── normalize.py               # Deterministic reconciliation & normalization layer
│   ├── analyze.py                 # Business refund analysis & anomaly detection
│   ├── classify.py                # AI-assisted refund classification & baseline NLP
│   └── evaluate_classifier.py     # Evaluation metrics on human validation sample
│
├── tests/
│   ├── test_audit.py              # Schema, duplicate, parsing, & integrity tests
│   ├── test_normalize.py          # 18-point normalization & reconciliation suite
│   ├── test_analyze.py            # Business refund analysis & anomaly verification
│   ├── test_classify.py           # Classification constraints, labels, & triage tests
│   └── test_evaluate_classifier.py # Metric calculations & unvalidated sample tests
│
├── reports/
│   ├── data-audit.md              # Initial data audit report
│   ├── data_audit_summary.json    # Machine-readable audit summary
│   ├── reconciliation-report.md   # Deterministic reconciliation report
│   ├── reconciliation_summary.json # Machine-readable reconciliation summary
│   ├── analysis-summary.md        # Comprehensive business analytics report
│   ├── client-claims.md           # Claim vs reality audit report
│   ├── ai-opportunity.md          # AI opportunity assessment & classifier proposal
│   ├── classification_summary.md  # AI classification results and business framework
│   ├── classification_results.csv # Line-item classification of 991 GW-OTHER tickets
│   ├── classification_review_queue.csv # Prioritized audit queue (HIGH, MEDIUM, LOW)
│   ├── classification_confusion_matrix.csv # Confusion matrix against human labels
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

### Run AI-Assisted Refund Reason Classification:
Classify the 991 `GW-OTHER` refund tickets using the auditable rule-based baseline NLP engine, generate the reproducible 100-ticket human validation sample, and produce the prioritized review queue:
```bash
python -m src.classify
```
Outputs:
- `data/validation/gw_other_validation_sample.csv` (100-ticket stratified sample, seed=42)
- `reports/classification_results.csv`
- `reports/classification_review_queue.csv` (sorted by HIGH, MEDIUM, LOW priority)
- `reports/classification_summary.md`
- `reports/classification_confusion_matrix.csv`

### Run Classifier Evaluation:
Evaluate classifier performance against human labels when populated in `data/validation/gw_other_validation_sample.csv`:
```bash
python -m src.evaluate_classifier
```
Outputs:
- Live console evaluation report (exact accuracy, macro F1, precision, recall, review rate)
- `reports/classification_confusion_matrix.csv` (populated once human labels exist)

### Run Automated Test Suite:
Run the complete test suite (65 automated tests covering schemas, duplicates, monetary conversion, reconciliation, business analysis, NLP classification, evaluation, and immutability):
```bash
pytest -v
```

---

## 4. AI-Assisted Classification & Human Validation

### Why `GW-OTHER` Needs Review:
In helpdesk operations, `GW-OTHER` (Goodwill / Other) appears as the first item in the dropdown menu. Consequently, frontline agents frequently selected `GW-OTHER` as a default choice, absorbing **991 tickets (42.4% of all refund tickets)** and **₹2,907,036.00 (43.3% of total refund spend)**. Furthermore, **879 of these tickets exceed the ₹500 policy threshold** for goodwill credits, obscuring true commercial root causes.

### What the Classifier Does:
1. **Auditable Text Analysis**: Examines `customer_message` and `agent_notes` alongside refund amounts and order details.
2. **Policy Label Mapping**: Evaluates text against the 8 authoritative Support Policy §5 codes (`GW-OTHER`, `DOA-REPL`, `LOST-TRANSIT`, `DUP-PAYMENT`, `CANCEL`, `PRICE-ADJ`, `RETURN-QC-OK`, `WTY-BUYBACK`).
3. **Evidence Extraction & Confidence**: Extracts verbatim text evidence spans and assigns normalized confidence scores (0.0 to 1.0).
4. **Deterministic Risk Triage**: Prioritizes cases into **HIGH**, **MEDIUM**, and **LOW** review tiers based on financial exposure, ambiguous orders, double-dip indicators, and low model confidence.
5. **Zero Silent Overwriting**: The existing reason code in canonical datasets is **never** overwritten; predicted codes are maintained in separate audit columns.

### What the Classifier Does NOT Do:
- It does **not** make decisions on financial payouts or alter monetary ledgers.
- It does **not** impute agent fraud, assign misconduct scores, or rank agents.
- It does **not** fabricate savings numbers. Identifying ₹1.58M in reclassification candidates attributes spend to true causes (e.g. carrier damage or return QC); it does not imply money is automatically recoverable.

### Model / Provider & Cost Information:
- **Baseline Model Used**: Pure local rule-based NLP baseline (`RuleBasedRefundClassifier`).
- **External API Calls**: Zero (0) external API calls were made.
- **Model Cost**: **$0.00** (completely free, offline, running deterministically on any clean machine).
- **Optional LLM Adapter**: `LLMRefundClassifier` can be enabled by setting `CLASSIFIER_PROVIDER=openai` and providing `OPENAI_API_KEY` in `.env`. If unconfigured, the system automatically and safely defaults to the local baseline.

### Human Review Workflow:
1. **Extract Sample**: `python -m src.classify` extracts a statistically representative, stratified 100-ticket sample to `data/validation/gw_other_validation_sample.csv` using a fixed random seed (`seed=42`).
2. **Conduct Audit**: Human auditors inspect customer messages and agent notes, entering authoritative labels into `human_label`, reviewer initials into `human_reviewer`, and notes into `review_notes`.
3. **Run Evaluation**: Execute `python -m src.evaluate_classifier`. If no labels are entered, the system states "validation pending" and never fabricates synthetic accuracy metrics.

### Discarded Approaches & Known Limitations:
- **Discarded Approach**: Unconstrained generative LLM classification without strict JSON schema enforcement was discarded because open-ended generation can invent non-policy reason codes.
- **Discarded Approach**: Automatic database updates to reason codes were rejected; preserving original entries ensures audit trail traceability.
- **Known Limitation**: Rule-based baseline relies on explicit customer and agent terminology; subtle indirect complaints or heavily abbreviated shorthand may result in `UNCLASSIFIED` (triggering manual review).

---

## 5. Key Metrics & Findings Summary

| Metric | Raw Export Value | Reconciled Value | Notes |
| :--- | :--- | :--- | :--- |
| **Total Tickets** | 12,238 | 11,600 unique | 638 re-imported duplicates (1,276 rows) |
| **Total Refunds** | Rs 230,124,081.00 | **Rs 6,709,932.00** | Legacy Freshdesk stored in paise/native minor units, requiring division by 100 to convert to INR |
| **Quarterly Average** | ~Rs 3.84 Crore/qtr | **Rs 1,118,322.00 (~11.18 L/qtr)** | Reconciles Finance vs. Helpdesk debate |
| **Double-Dips** | N/A | **166 unique tickets** | Both refund and replacement indicator (158 confirmed order-linked, 8 ambiguous) |
| **GW-OTHER Concentration** | N/A | **879 tickets > Rs 500** | GW-OTHER refunds above stated Rs 500 goodwill threshold; review candidates requiring text/policy validation |
| **GW-OTHER Reclassified** | N/A | **574 candidate tickets** | ₹1,576,028.00 in candidate spend identified by baseline classifier |
| **Review Queue Triage** | N/A | **650 HIGH, 341 MEDIUM** | Prioritized operational queue for audit teams |
| **Validation Sample** | N/A | **100 tickets** | Stratified sample (seed=42) in `data/validation/gw_other_validation_sample.csv` |
| **Replacements (General)**| N/A | **1,100 issued by Tier 1** | Total replacements issued generally; non-warranty vs certified warranty replacements must be distinguished |
| **CSAT Shift (Q4)** | Claimed: +0.4 | **Observed: +0.029** | Q3 mean = 3.478, Q4 mean = 3.507 (+0.029 points; not supported by observed data) |
| **SLA Breaches** | N/A | **2,476 tickets (21.3%)** | Rs 866,600.00 in contractual breach credits |

---

## 6. Authoritative References

- `docs/source-context.md`: Complete synthesis of business policies, SLAs, contact costs, tier rules, and canonical reconciliation rules.
- `reports/data-audit.md`: In-depth analytical and empirical audit report.
- `reports/reconciliation-report.md`: Formal reconciliation report and golden benchmark verification.
- `reports/classification_summary.md`: AI-assisted classification breakdown and review triage.
- `reports/ai-opportunity.md`: AI opportunity assessment, architecture, and validation protocol.
