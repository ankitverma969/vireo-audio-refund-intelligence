# Assignment Submission Form — Vireo Audio Refund Intelligence

---

## Project Information

| Field | Value |
|---|---|
| **Project Name** | Vireo Audio Refund Intelligence & AI Audit Platform |
| **Repository** | `vireo-audio-refund-intelligence` (local git, 1 commit ahead of initial baseline) |
| **Submission Date** | September 28, 2026 |
| **Author** | (see repository git log — no personal information invented) |

---

## Problem Statement

Vireo Audio's Finance Controller observed that raw helpdesk exports appeared to show refund spend exceeding ₹1 crore per quarter — an implausibly high figure. The task was to:

1. Audit and reconcile the raw ticket data to arrive at a defensible financial baseline.
2. Identify the root causes of the apparent discrepancy.
3. Analyse refund reasons, operational patterns, and anomalies.
4. Build an AI-assisted classification tool to help triage the largest catch-all reason code (`GW-OTHER`).
5. Deliver a business-facing dashboard and a one-page executive memo.

---

## Business Outcome (Explicit Number + Money)

**Primary Outcome:**  
Reconcile and explain ₹67.10 lakh (₹6,709,932) of canonical refund spend across 2,340 refunds, including ₹29.07 lakh currently classified as GW-OTHER, while identifying ₹15.76 lakh of candidate reason-code reclassification opportunities for human review.

> Note: The ₹15.76 lakh is a **candidate reclassification opportunity**, not cash savings, recovered money, or prevented loss. All reclassifications require human confirmation.

**Secondary Outcomes:**
- Identified 166 refund + replacement double-dip indicators (₹574,191 total refund cash) requiring warehouse verification.
- Identified 707 ambiguous order-match records requiring data sanitation.
- Explained the apparent >₹1 crore/quarter Finance figure as a data-quality artefact (paise minor units + 638 migration duplicates).

---

## Approach

### Data Quality Issues Identified

| Issue | Root Cause | Resolution |
|---|---|---|
| Apparent ₹23 crore raw spend | Legacy `legacy_fd` platform stored amounts in paise (100× INR) | Divide legacy amounts by 100 during normalization |
| 1,276 duplicate rows | 638 tickets re-imported during platform migration cutover | Deduplicate by `ticket_id` preferring `helpdesk` source records |
| 707 ambiguous order matches | Multiple order records share the same customer identifier | Flagged as `order_match_status = ambiguous` for human review |
| GW-OTHER catch-all overuse | First item in agent dropdown; no enforcement of subcategory | Identified via NLP keyword analysis; 574 candidates flagged |

### Normalization & Reconciliation (`src/normalize.py`)

- Loaded raw tickets from `data/raw/` (immutable).
- Applied 100× paise-to-INR conversion for all `legacy_fd` source records.
- Deduplicated 638 migration duplicate groups (1,276 rows).
- Produced `data/processed/canonical_tickets.parquet` (11,600 rows) and `data/processed/canonical_refunds.csv` (2,340 rows).
- Verified financial invariants: ₹6,709,932 total spend.

### Analysis (`src/analyze.py`)

- Monthly and quarterly refund trend analysis.
- Reason code distribution and spend breakdown.
- Agent and team operational breakdown with tier separation.
- GW-OTHER ≥ ₹500 candidate identification (879 tickets).
- Double-dip indicator detection: 166 refund + replacement tickets.
- Ambiguous order match flagging: 707 tickets overall.
- Quarterly CSAT correlation (factual, no causal claims).

### AI-Assisted Component (`src/classify.py`, `src/evaluate_classifier.py`)

**Architecture:**

```
GW-OTHER tickets (991)
     │
     ▼
RuleBasedRefundClassifier (default, local, zero API cost)
  - Keyword pattern matching against 7 non-GW policy code templates
  - Confidence scoring [0.0, 1.0], clamped
  - Evidence text extraction
  - Review priority assignment (HIGH / MEDIUM / LOW)
     │
     ▼ (optional, if OPENAI_API_KEY set)
OpenAIRefundClassifier adapter
  - Same structured output schema
  - Unsupported labels rejected
  - Financial fields immutable
     │
     ▼
Classification Results → reports/classification_results.csv
Review Queue → reports/classification_review_queue.csv
```

**Key Design Decisions:**
- AI/rule suggestions are stored in `predicted_reason_code` — a separate column. The canonical `refund_reason_code` is never modified by the classifier.
- Financial totals are derived exclusively from canonical data; the classifier cannot alter them.
- All AI suggestions are clearly labelled as advisory and require human confirmation.
- Unsupported or out-of-policy labels are rejected before output.

### Validation Approach (`src/evaluate_classifier.py`)

- 100-ticket stratified sample drawn deterministically from GW-OTHER tickets (`data/validation/gw_other_validation_sample.csv`).
- Human labellers fill in the `human_label` column.
- Accuracy, precision, recall, and F1 are computed **only** against verified `human_label` entries (not predicted).
- Confusion matrix output: `reports/classification_confusion_matrix.csv`.

**Current Validation Limitation:**  
The validation sample (100 tickets) is currently **unannotated** — `human_label` column is blank for all 100 tickets. No accuracy, precision, recall, or F1 metrics have been computed or published. No fabricated validation metrics are claimed.

### Dashboard (`app.py`)

Streamlit application with 7 navigation views:

1. **Executive Overview** — reconciled KPIs, spend/trend charts, reason code pie chart.
2. **Monthly & Cohort View** — filterable monthly breakdown by channel, team, tier.
3. **Reason Code Breakdown** — full 8-code financial table + monthly trajectory.
4. **Agent & Operations View** — tier-separated agent tables with per-agent case inspection.
5. **AI-Assisted Review (GW-OTHER)** — reclassification queue, confidence, priority, ticket inspector with advisory notice.
6. **Exception & Audit Queue** — double-dip indicators, ambiguous matches, high-value refunds, GW-OTHER cap candidates.
7. **Business Value Framework** — reclassification opportunity framework, potential recovery analysis, validation status.

---

## Testing

| Test Module | Tests | Scope |
|---|---|---|
| `tests/test_audit.py` | 17 | Schema, duplicates, date/numeric parsing, referential integrity |
| `tests/test_normalize.py` | 18 | 100× normalization, migration dedup, order matching, golden benchmarks |
| `tests/test_analyze.py` | 13 | Monthly reconciliation, reason/agent breakdowns, double-dip isolation |
| `tests/test_classify.py` | 19 | 8-code label space, confidence clamping, mock LLM parsing, error fallbacks, metadata immutability |
| `tests/test_evaluate_classifier.py` | 5 | Unvalidated sample reporting, confusion matrix, synthetic F1 |
| **Total** | **72** | **72 passed / 0 failed** |

---

## Security

- No real API keys, passwords, tokens, or secrets in the repository.
- `.env` is `.gitignore`d; `.env.example` contains only empty placeholders.
- No hardcoded local machine paths (e.g., `E:\...`) anywhere in source code.
- `OPENAI_API_KEY` is consumed only from environment variable; never logged or stored.

---

## Reproducibility

```bash
# Fresh machine setup
git clone <repo>
cd vireo-audio-refund-intelligence
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Run full pipeline
python -m src.audit
python -m src.normalize
python -m src.analyze
python -m src.classify
python -m src.evaluate_classifier

# Run tests
pytest -v

# Launch dashboard
streamlit run app.py
```

No manual edits to site-packages required. No external APIs required for core functionality.

---

## AI Disclosure

| Field | Value |
|---|---|
| **AI/LLM component** | Optional OpenAI adapter (`src/classify.py` → `OpenAIRefundClassifier`) |
| **Default mode** | `RuleBasedRefundClassifier` (local, zero API cost) |
| **Model configured** | `gpt-4o-mini` (via `OPENAI_MODEL` env var) |
| **Actual API calls made** | **0** |
| **Actual API cost** | **$0** |
| **Reason no live LLM run occurred** | `OPENAI_API_KEY` was not available in the development environment |
| **AI output status** | All classification results in `classification_results.csv` are from the rule-based baseline |
| **AI autonomy** | None — all AI suggestions require explicit human confirmation before any accounting modification |
| **Fabricated accuracy** | None — no accuracy metrics are published because the validation sample is unannotated |
| **Fabricated LLM output** | None |

---

## Known Limitations

1. **Validation sample unannotated.** Classifier accuracy is unknown until operations team labels the 100-ticket sample.
2. **No live LLM run.** The OpenAI adapter is fully implemented and tested via mocks; a real run requires a valid `OPENAI_API_KEY`.
3. **GW-OTHER candidates unverified.** The 574 reclassification candidates are NLP suggestions requiring human review.
4. **Q4 refund spend increase unexplained.** The +34.8% Q3→Q4 rise is factual but its cause is unknown from the current data.
5. **Order ID sanitation incomplete.** 707 ambiguous order matches require a data-engineering pass on the CRM order table.

---

## How to Run

See `README.md` for complete step-by-step instructions including virtual environment setup, pipeline commands, test execution, and dashboard launch.

---

## Demo Instructions

See `reports/demo-script.md` for the 3-minute screen-recording demo script.