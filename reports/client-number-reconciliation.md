# Client-Facing Number Reconciliation Report
## Vireo Audio Refund Intelligence — Phase 11 Verification

**Date:** September 28, 2026  
**Method:** Direct extraction from `data/processed/canonical_tickets.parquet` using clean-venv Python 3.11.9  
**Authority:** Canonical parquet file produced by `src/normalize.py` — the single source of truth for all financial metrics.

---

## 1. Core Invariants

| Metric | Canonical Source (Parquet) | executive-memo.md | submission-form.md | demo-script.md | Status |
|---|---|---|---|---|---|
| Total canonical tickets | **11,600** | 11,600 ✓ | 11,600 ✓ | 11,600 ✓ | ✅ PASS |
| Total canonical refunds | **2,340** | 2,340 ✓ | 2,340 ✓ | 2,340 ✓ | ✅ PASS |
| Total reconciled spend | **₹6,709,932** | ₹67.10 lakh / ₹6,709,932 ✓ | ₹67.10 lakh / ₹6,709,932 ✓ | ₹67.10 lakh ✓ | ✅ PASS |
| Average refund | **₹2,867.49** | ₹2,867.49 ✓ | — | ₹2,867 ✓ | ✅ PASS |
| Quarterly avg spend | **₹11,18,322** | ~₹11.18 lakh ✓ | — | ₹11.18 lakh ✓ | ✅ PASS |

---

## 2. Reason Code Breakdown (Canonical vs. Executive Memo)

Source: `canonical_tickets.parquet` → verified via `reports/analysis-summary.md`

| Reason Code | Canonical Tickets | Canonical Spend | Canonical % | Memo Tickets | Memo Spend | Memo % | Status |
|---|---|---|---|---|---|---|---|
| **GW-OTHER** | 991 | ₹29,07,036 | 43.3% | 991 ✓ | ₹29,07,036 ✓ | 43.3% ✓ | ✅ PASS |
| **RETURN-QC-OK** | 452 | ₹11,81,386 | 17.6% | 452 ✓ | ₹11,81,386 ✓ | 17.6% ✓ | ✅ PASS |
| **DUP-PAYMENT** | 321 | ₹8,84,586 | 13.2% | 321 ✓ | ₹8,84,586 ✓ | 13.2% ✓ | ✅ PASS |
| **CANCEL** | 222 | ₹6,12,950 | 9.1% | 222 ✓ | ₹6,12,950 ✓ | 9.1% ✓ | ✅ PASS |
| **DOA-REPL** | 147 | ₹4,71,190 | 7.0% | 147 ✓ | ₹4,71,190 ✓ | 7.0% ✓ | ✅ PASS |
| **WTY-BUYBACK** | 89 | ₹2,89,154 | 4.3% | 89 ✓ | ₹2,89,154 ✓ | 4.3% ✓ | ✅ PASS |
| **PRICE-ADJ** | 71 | ₹2,07,073 | 3.1% | 71 ✓ | ₹2,07,073 ✓ | 3.1% ✓ | ✅ PASS |
| **LOST-TRANSIT** | 47 | ₹1,56,557 | 2.3% | 47 ✓ | ₹1,56,557 ✓ | 2.3% ✓ | ✅ PASS |

> **Note:** The executive memo was corrected during Phase 11 from previously incorrect historical values.  
> The prior memo incorrectly showed RETURN-QC-OK=563/₹16,73,348, CANCEL=375/₹11,23,054, WTY-BUYBACK=122/₹4,46,140. These are now corrected to canonical values.

---

## 3. GW-OTHER Metrics

| Metric | Canonical | Memo | Submission | Demo | Status |
|---|---|---|---|---|---|
| GW-OTHER tickets | **991** | 991 ✓ | 991 ✓ | 991 ✓ | ✅ PASS |
| GW-OTHER spend | **₹2,907,036** | ₹29,07,036 ✓ | ₹29.07 lakh ✓ | ₹29.07 lakh ✓ | ✅ PASS |
| GW-OTHER > ₹500 count | **879** | 879 ✓ | 879 ✓ | 879 ✓ | ✅ PASS |
| GW-OTHER > ₹500 spend | **₹2,871,632** | — (not stated) | — | — | N/A |
| Candidate reclassifications | **574** | 574 ✓ | 574 ✓ | 574 ✓ | ✅ PASS |
| Candidate reclassification spend | **₹1,576,028** | ₹15,76,028 ✓ | ₹15.76 lakh ✓ | ₹15.76 lakh ✓ | ✅ PASS |

---

## 4. Exception Metrics

| Metric | Canonical | Memo | Submission | Demo | Status |
|---|---|---|---|---|---|
| Double-dip total | **166** | 166 ✓ | 166 ✓ | 166 ✓ | ✅ PASS |
| Double-dip unambiguous | **158** | 158 ✓ | — | 158 ✓ | ✅ PASS |
| Double-dip ambiguous | **8** | 8 ✓ | — | — | ✅ PASS |
| Double-dip cash spend | **₹574,191** | ₹5,74,191 ✓ | ₹574,191 ✓ | — | ✅ PASS |
| Ambiguous order matches (all) | **707** | 707 ✓ | 707 ✓ | — | ✅ PASS |

---

## 5. Quarterly Refund Breakdown

| Quarter | Canonical Count | Canonical Spend |
|---|---|---|
| 2025Q1 | 212 | ₹6,09,583 |
| 2025Q2 | 253 | ₹7,27,422 |
| **2025Q3** | **405** | **₹12,07,091** |
| **2025Q4** | **542** | **₹16,27,575** |
| 2026Q1 | 455 | ₹12,58,438 |
| 2026Q2 | 473 | ₹12,79,823 |

Q3→Q4 change verified: +₹4,20,484 / +34.8%

| Metric | Canonical | Memo | Status |
|---|---|---|---|
| Q3 2025 spend | **₹12,07,091** | ₹12,07,091 ✓ | ✅ PASS |
| Q4 2025 spend | **₹16,27,575** | ₹16,27,575 ✓ | ✅ PASS |
| Q3→Q4 change | **+₹4,20,484 / +34.8%** | +₹4,20,484 / +34.8% ✓ | ✅ PASS |

---

## 6. CSAT Verification

| Quarter | Canonical CSAT |
|---|---|
| 2025Q1 | 3.5399 |
| 2025Q2 | 3.5158 |
| **2025Q3** | **3.4782** |
| **2025Q4** | **3.5072** |
| 2026Q1 | 3.4891 |
| 2026Q2 | 3.4610 |

Q3 CSAT = 3.478 (rounded to 3 dp) ✓  
Q4 CSAT = 3.507 (rounded to 3 dp) ✓  
Change = +0.029 ✓

| Metric | Canonical | Memo | Status |
|---|---|---|---|
| Q3 CSAT | **3.4782** | 3.478 ✓ | ✅ PASS |
| Q4 CSAT | **3.5072** | 3.507 ✓ | ✅ PASS |
| CSAT change | **+0.029** | +0.029 ✓ | ✅ PASS |

---

## 7. Corrections Made in Phase 11

| Document | Old Value (Wrong) | Correct Value | Correction Applied |
|---|---|---|---|
| `reports/executive-memo.md` | RETURN-QC-OK: 563 / ₹16,73,348 / 24.9% | 452 / ₹11,81,386 / 17.6% | ✅ Fixed |
| `reports/executive-memo.md` | CANCEL: 375 / ₹11,23,054 / 16.7% | 222 / ₹6,12,950 / 9.1% | ✅ Fixed |
| `reports/executive-memo.md` | WTY-BUYBACK: 122 / ₹4,46,140 / 6.6% | 89 / ₹2,89,154 / 4.3% | ✅ Fixed |
| `reports/executive-memo.md` | Others (4 codes): 289 / ₹5,60,354 / 8.4% | Full 5-code breakdown added | ✅ Fixed |
| `reports/executive-memo.md` | Missing ₹1,000 label | Added "Proposed management control" label | ✅ Fixed |
| `submission-form.md` | ₹X placeholder for double-dip spend | ₹574,191 | ✅ Fixed |

---

## 8. Final Status

**All client-facing numbers verified against canonical parquet source.**  
**All corrections applied.**  
**No remaining discrepancies.**

| Check | Status |
|---|---|
| All reason code numbers match canonical | ✅ PASS |
| All exception numbers match canonical | ✅ PASS |
| All quarterly spend numbers match canonical | ✅ PASS |
| All CSAT values match canonical | ✅ PASS |
| No ₹X or TBD placeholders remain | ✅ PASS |
| Prohibited language absent | ✅ PASS |
| Proposed controls labelled correctly | ✅ PASS |