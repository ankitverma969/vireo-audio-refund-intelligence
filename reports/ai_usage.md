# Vireo Audio — AI Model Usage & Token Cost Tracking

> **Audit Governance**: Detailed accounting of external API calls, token volumes, and incurred expenses.

---

## 1. Executive Summary

- **External API Calls Made**: **0**
- **Total Tickets Processed via API**: **0**
- **Total Prompt Tokens**: **0**
- **Total Completion Tokens**: **0**
- **Aggregate Tokens**: **0**
- **Total Incurred Cost (USD)**: **$0.0000** (Monetary cost: $0.00 / Not calculated (no external calls))
- **Default Pipeline Mode**: `CLASSIFIER_PROVIDER=local` (100% offline rule-based NLP baseline)

---

## 2. Model & Fallback Transparency

No live external API calls were executed during the pipeline run.
- The system ran using the deterministic **local rule-based baseline** (`RuleBasedRefundClassifier`).
- Zero API credentials were required or consumed.
- Zero financial cost was incurred.

### Configuration Options
To enable live OpenAI classification on a sample batch:
```bash
export CLASSIFIER_PROVIDER=openai
export OPENAI_API_KEY=your-api-key-here
export OPENAI_MODEL=gpt-4o-mini
python -m src.classify
```

---

## 3. Pricing & Billing Limitations

- Provider token pricing changes dynamically across model generations.
- In the absence of an explicit pricing configuration table, token counts are strictly preserved as primary truth.
- Token counts are reported directly from provider completion usage metadata.