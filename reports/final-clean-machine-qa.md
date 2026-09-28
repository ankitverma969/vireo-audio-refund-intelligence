# Final Clean-Machine End-to-End Quality Assurance Report

> **Audit Standard**: Complete, independent verification of repository reproducibility, dependency integrity, pipeline execution, and financial invariants on a clean environment.

> **Execution Date**: September 28, 2026  
> **Executed By**: Automated QA pass (Antigravity IDE — Conversation 777ba1cd)

---

## 1. Executive Summary

| Verification Category | Status | Details |
| :--- | :---: | :--- |
| **Clean Environment Setup** | **PASS** | `.clean_test_venv` isolated from global packages; all deps from `requirements.txt` |
| **Pipeline Reproducibility** | **PASS** | All 5 deterministic modules executed with exit code 0 |
| **Automated Test Suite** | **PASS** | **72 passed / 0 failed in 49.43s** |
| **App Import Check** | **PASS** | `python -c "import app; print('APP_IMPORT_OK')"` → `APP_IMPORT_OK` |
| **Financial Invariants** | **PASS** | 100% agreement across all 7 core financial and volume metrics |
| **Security & Secrets** | **PASS** | Zero real credentials, keys, or hardcoded local paths detected |
| **Monkey Patches** | **PASS** | Zero `sys.modules` patches or site-package edits in `app.py` or any source file |

---

## 2. Environment & Dependency Specifications

- **Operating System**: Windows 11 (PowerShell)
- **Python Version**: `Python 3.11.9`
- **Clean Environment Method**:
  ```powershell
  python -m venv .clean_test_venv
  .clean_test_venv\Scripts\python.exe -m pip install --upgrade pip --quiet
  .clean_test_venv\Scripts\pip.exe install -r requirements.txt --quiet
  ```
- **Dependency Installation Result**: Exit code 0 (`PIP_INSTALL_DONE`)
- **Virtual Environment**: `.clean_test_venv/` (excluded from git via `.gitignore`)
- **Pinned version ranges in `requirements.txt`**:
  - `pandas>=2.0.0,<3.0.0`
  - `pyarrow>=14.0.0,<25.0.0`
  - `numpy>=1.24.0,<3.0.0`
  - `pypdf>=3.0.0,<6.0.0`
  - `streamlit>=1.30.0,<2.0.0`
  - `starlette>=0.45.0,<1.0.0`
  - `plotly>=5.18.0,<7.0.0`
  - `openai>=1.12.0,<3.0.0`
  - `pytest>=7.0.0,<9.0.0`

**Issue Resolved Prior to This Run:**  
Streamlit 1.60.0 HTTP gzip middleware requires `starlette>=0.45.0`. Pinned in `requirements.txt`. All prior monkey-patches and `sys.modules` polyfills removed from `app.py`. Verified absent via `grep sys.modules` (no results).

---

## 3. Pre-Flight Static Checks

| Check | Result |
|---|---|
| `app.py` Starlette monkey patches | **None found** (`grep sys.modules` → 0 results) |
| `app.py` environment-specific polyfills | **None found** |
| Hardcoded local paths (`E:\...`) in source | **None found** (`grep "E:\\"` → 0 results) |
| Real OpenAI API key (`sk-...`) in repo | **None found** |
| `.env` ignored | **YES** (`.gitignore` line 48: `.env`, line 49: `!.env.example`) |
| `.env.example` placeholder only | **YES** (`OPENAI_API_KEY=` — empty value) |
| Machine-specific credentials required | **None** |

---

## 4. Pipeline Execution Verification

All 5 pipeline stages executed from the clean environment (`.clean_test_venv`):

```
Stage 1: python -m src.audit
  ✓ Total raw tickets: 12,238
  ✓ Unique ticket IDs: 11,600
  ✓ Migration duplicates: 638 IDs (1,276 rows)
  ✓ Raw export refund total: ₹23,01,24,081.00
  ✓ Fully reconciled refund total: ₹6,709,932.00
  ✓ Exit code: 0

Stage 2: python -m src.normalize
  ✓ Canonical ticket count: 11,600
  ✓ Canonical refund count: 2,340
  ✓ Reconciled refund total: ₹6,709,932.00
  ✓ Ambiguous order matches: 707
  ✓ Reconciliation exceptions: 0
  ✓ Exit code: 0

Stage 3: python -m src.analyze
  ✓ Reconciled Refund Count: 2,340
  ✓ Reconciled Refund Total: ₹6,709,932.00
  ✓ Double-Dip Exceptions: 166
  ✓ GW-OTHER Above ₹500 Threshold: 879/991
  ✓ Q3→Q4 CSAT Shift: +0.029 (claimed +0.40 not reproducible)
  ✓ Exit code: 0

Stage 4: python -m src.classify
  ✓ 991 GW-OTHER tickets classified
  ✓ 574 candidate reclassifications identified
  ✓ 0 external API calls made
  ✓ classification_results.csv generated
  ✓ Exit code: 0

Stage 5: python -m src.evaluate_classifier
  ✓ VALIDATION STATUS: PENDING HUMAN AUDIT
  ✓ 100 sample tickets present; 0 labeled
  ✓ No metrics fabricated
  ✓ Exit code: 0
```

---

## 5. Financial Invariant Verification

Verified from clean-environment pipeline outputs:

| Financial / Volume Metric | Expected | Verified | Status |
| :--- | :--- | :--- | :---: |
| Canonical Ticket Count | 11,600 | **11,600** | **PASS** |
| Canonical Refund Count | 2,340 | **2,340** | **PASS** |
| Reconciled Refund Spend | ₹6,709,932 | **₹6,709,932** | **PASS** |
| GW-OTHER Ticket Volume | 991 | **991** | **PASS** |
| GW-OTHER Refund Spend | ₹2,907,036 | **₹2,907,036** | **PASS** |
| Double-Dip Indicators | 166 | **166** | **PASS** |
| Ambiguous Order Matches | 707 | **707** | **PASS** |

---

## 6. Automated Test Suite

```
Platform: win32 — Python 3.11.9, pytest-8.4.2
Clean venv: .clean_test_venv

============================= 72 passed in 49.43s =============================
```

| Module | Tests | Result |
|---|---|---|
| `tests/test_audit.py` | 17 | ✓ All PASSED |
| `tests/test_normalize.py` | 18 | ✓ All PASSED |
| `tests/test_analyze.py` | 13 | ✓ All PASSED |
| `tests/test_classify.py` | 19 | ✓ All PASSED |
| `tests/test_evaluate_classifier.py` | 5 | ✓ All PASSED |
| **Total** | **72** | **72 PASSED / 0 FAILED** |

---

## 7. Dashboard Startup & App Import

```
Command: python -c "import app; print('APP_IMPORT_OK')"
Result:  APP_IMPORT_OK
Notes:   Streamlit ScriptRunContext warnings are expected in bare-import mode
         and are explicitly documented as ignorable.
         No ImportError, no AttributeError, no missing dependency.
```

**Streamlit launch** (via `streamlit run app.py`): Starts Uvicorn server on port 8501.  
All 7 navigation views render without runtime exceptions:
- Executive Overview ✓
- Monthly & Cohort View ✓
- Reason Code Breakdown ✓
- Agent & Operations View ✓
- AI-Assisted Review (GW-OTHER) ✓
- Exception & Audit Queue ✓
- Business Value Framework ✓

---

## 8. Security Scan

| Scan | Tool | Result |
|---|---|---|
| Real OpenAI keys | `grep "sk-"` | **0 matches** |
| Hardcoded local paths | `grep "E:\\"` | **0 matches** |
| `sys.modules` patches | `grep "sys.modules"` | **0 matches** |
| `.env` committed | `git status` check | **Not committed** (gitignored) |
| `.env.example` | Manual review | Placeholders only |

---

## 9. Issues Encountered & Resolved

| Issue | Root Cause | Fix |
|---|---|---|
| Streamlit `ImportError` on `IdentityResponder` | Starlette < 0.45.0 missing gzip middleware symbols | Pinned `starlette>=0.45.0,<1.0.0` in `requirements.txt` |
| Prior `sys.modules` monkey-patch in `app.py` | Workaround before pinning | Removed entirely; clean import now works |

---

## 10. Audit Conclusion

The Vireo Audio Refund Intelligence repository is **100% clean-machine reproducible**. A fresh virtual environment installing only the pinned `requirements.txt` correctly reproduces every financial figure, report, test, and dashboard view without manual interventions, site-package edits, or external API dependencies.