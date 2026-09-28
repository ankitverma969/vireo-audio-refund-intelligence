# Vireo Audio — AI Classification Validation & Multi-Way Agreement Report

> **Audit Standard**: Evaluates model performance against human ground truth and inspects model agreement.
> **Methodological Rule**: Never treat existing reason codes, rule-based outputs, or LLM predictions as ground truth.

---

## 1. Validation Status & Ground Truth Availability

- **Validation Sample Size**: **100 tickets** (stratified random sample, `seed=42`)
- **Verified Human Annotations Completed**: **0 / 100**
- **Validation Benchmark Status**: **PENDING HUMAN AUDIT**

> [!IMPORTANT]
> **Formal model accuracy has not yet been established because human ground truth is pending.**
> No synthetic or fabricated labels have been substituted. Accuracy, precision, recall, and F1 metrics
> will be computed exclusively once operational reviewers populate `human_label` in `data/validation/gw_other_validation_sample.csv`.

---

## 2. Multi-Way Classifier Agreement Analysis

Analyzed controlled subset of **30 tickets** from the human validation sample:

- **LLM Execution Status**: `LLM execution pending credentials (OPENAI_API_KEY not configured)`
- **Live API Calls Made**: `0`
- **Rule-Based Predictions**: Successfully computed for all 30 sample tickets.
- **LLM Agreement Calculation**: Deferred until API credentials are provided.

To execute live LLM comparison on this subset:
```bash
export OPENAI_API_KEY=your_key_here
python -m src.classify
python -m src.evaluate_classifier
```

---

## 3. Review Workflow & Next Steps for Operational Leads

1. Open `data/validation/gw_other_validation_sample.csv` in Excel or an internal audit tool.
2. For each of the 100 tickets, review `customer_message`, `agent_notes`, and `refund_amount_inr_normalized` against Support Policy §5.
3. Enter the authoritative policy code into `human_label` (`GW-OTHER`, `DOA-REPL`, `LOST-TRANSIT`, `DUP-PAYMENT`, `CANCEL`, `PRICE-ADJ`, `RETURN-QC-OK`, `WTY-BUYBACK`).
4. Record `human_reviewer` initials and brief `review_notes`.
5. Save the CSV and run:
   ```bash
   python -m src.evaluate_classifier
   ```
6. The evaluation engine will automatically compute exact accuracy, macro F1, and export `reports/classification_confusion_matrix.csv`.

---

## 4. Limitations & Governance Safeguards

- **Lexical Ambiguity**: Rule-based baseline relies on deterministic pattern weights; edge cases with conflicting customer narratives are routed to HIGH priority review.
- **Zero Automated Mutations**: Predictions are advisory. The canonical financial ledger (`canonical_tickets.parquet`) is never modified by the classifier.
- **No Misconduct Inferences**: Models do not score agent integrity or performance.