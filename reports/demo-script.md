# Demo Script — Vireo Audio Refund Intelligence
## Screen Recording Script (≤ 3 Minutes)

**Format:** No slides. Screen recording only. Open the Streamlit dashboard (`streamlit run app.py`) before starting.

---

### [0:00 – 0:20] Problem & Business Question

**What to say:**

> "Vireo Audio's Finance Controller noticed that raw helpdesk exports appeared to show refund spend exceeding one crore rupees per quarter — an implausibly high figure for an audio accessories brand. The question: Is Vireo Audio actually spending this much on refunds? And if not, why does the export show it? This tool answers both questions."

**Screen:** Show the terminal with the repo directory. Optionally show the first few lines of the raw CSV to demonstrate the raw amount field values.

---

### [0:20 – 0:45] Data Quality & Reconciliation Finding

**What to say:**

> "The raw export problem has two causes. First, the legacy Freshdesk platform stored monetary amounts in native minor units — paise — so every legacy figure was 100 times its true Rupee value. Second, 638 tickets were duplicated during the system migration, appearing twice in the export. After normalization and deduplication, the reconciled total is ₹67.10 lakh across 2,340 refunds — an average of ₹11.18 lakh per quarter. This is a data-quality finding, not a Finance accounting error."

**Screen:** Run `python -m src.normalize` in the terminal so the audience can see it complete with exit code 0. Then show `data/processed/canonical_tickets.parquet` exists.

---

### [0:45 – 1:15] Executive Dashboard

**Navigate to:** Streamlit → **Executive Overview** page.

**What to say:**

> "The executive dashboard shows all six reconciled KPIs. ₹67.10 lakh total spend. 2,340 refunds. Average refund ₹2,867. GW-OTHER — the catch-all category — absorbs 43.3% of total spend at ₹29.07 lakh. The bar chart shows monthly spend trajectory. There was a 34.8% increase from Q3 to Q4 2025; we have documented this as a factual observation — the underlying cause is not yet established."

**Screen:** Point at each metric card in turn. Scroll down to show the monthly bar chart and the reason code pie chart.

---

### [1:15 – 1:45] Reason & Agent / Team Analysis

**Navigate to:** Streamlit → **Reason Code Breakdown**, then **Agent & Operations View**.

**What to say:**

> "The reason code breakdown shows the full eight-code financial distribution — GW-OTHER alone is ₹29 lakh. The monthly trajectory shows it rising in Q4. Switching to the Agent & Operations view — note the disclaimer at the top. High refund concentration in Tier 1 reflects the dedicated Returns Desk and Billing Escalations roles, not individual agent behaviour. The Tier 2 tab shows the warranty buy-back specialists handled separately."

**Screen:** Show the reason code table sorted by spend. Switch to Agent view, point at the disclaimer banner. Click the Tier 2 tab.

---

### [1:45 – 2:20] AI-Assisted GW-OTHER Review

**Navigate to:** Streamlit → **AI-Assisted Review (GW-OTHER)**.

**What to say:**

> "This is the AI-assisted reclassification workbench. 991 GW-OTHER tickets were run through a rule-based NLP classifier — the default mode, which requires no API key. It identified 574 candidate reclassifications totalling ₹15.76 lakh. I want to be explicit: this is not money saved. It is a reason-code correction opportunity that requires human sign-off before any accounting change. The advisory notice at the top makes this clear. Let me select a HIGH-priority ticket and open the inspector."

**Screen:** Filter by Priority = HIGH. Click a ticket in the table. Show the inspector panel on the right: existing code, predicted code, confidence score, evidence text, customer message. Point at the "Advisory Notice" blue banner.

**What to say:**

> "The system shows the original code, the predicted code, the extracted evidence text from the ticket, and the full customer message. A human reviewer decides whether to accept the suggestion. The classifier cannot change the financial ledger — only a human can."

---

### [2:20 – 2:40] Exception Queue

**Navigate to:** Streamlit → **Exception & Audit Queue**.

**What to say:**

> "The exception queue surfaces four categories. The most operationally urgent: 166 tickets where both a cash refund and a replacement unit were dispatched. 158 of these are unambiguously order-linked. These need verification against warehouse manifests to confirm whether a genuine duplicate fulfilment occurred. The GW-OTHER cap tab shows 879 review candidates above ₹500 — again, these are candidates for review, not confirmed violations."

**Screen:** Click "Double-Dip (Refund + Replacement)" tab — show count and table. Click "GW-OTHER Above Goodwill Cap" tab — show the note about review candidates.

---

### [2:40 – 3:00] Recommendations & Limitations

**Navigate to:** Streamlit → **Business Value Framework**.

**What to say:**

> "The business value framework summarises the reclassification opportunity and the distinction between reason-code correction and actual cash recovery. The validation status section is honest: the 100-ticket human review sample is unannotated — we have not published any accuracy metrics, because we have no verified ground truth yet. The tool is ready for the operations team to begin labelling. To close: all figures here are deterministic and reproducible. The AI component is advisory only. No live LLM calls were made during this demo — the OpenAI adapter is fully implemented but requires a real API key to activate."

**Screen:** Show the "Spend Reclassification Opportunity" section. Scroll to the "Human Validation & Machine Learning Benchmark Status" section — point at the "Label Status: Unannotated" line.

---

### Post-Demo Notes (not spoken aloud)

- **Changed/discarded work:** An early version of the executive memo used "paise (1/100 INR)" incorrectly. Corrected to "legacy Freshdesk storing amounts in paise/native minor units." An early draft described GW-OTHER above ₹500 as "confirmed policy violations." Corrected to "review candidates."
- **No fabricated accuracy:** The classifier has been evaluated only on synthetic golden tests in `tests/test_evaluate_classifier.py`. Real accuracy is pending human annotation.
- **Full reproducibility:** All pipeline stages run with `exit code 0` from a fresh virtual environment using only `requirements.txt`. No manual site-packages edits required.