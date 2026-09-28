"""Test suite for classifier evaluation metrics and human validation handling.

Covers:
- Graceful handling of unvalidated sample (no fake metrics generated)
- Accurate computation of exact accuracy, macro precision, recall, and F1 on synthetic data
- Correct construction of confusion matrix
- Abstention (None / UNCLASSIFIED) handling
- Metric behavior on empty datasets
"""

import pytest
import pandas as pd
from pathlib import Path

from src.config import DATA_VALIDATION_DIR
from src.evaluate_classifier import (
    compute_classification_metrics,
    evaluate_validation_file,
)


class TestValidationSampleHandling:
    """Validate behavior on the actual validation sample file."""

    def test_unvalidated_sample_reports_validation_pending(self):
        """1. Real validation sample without human labels reports 'validation_pending' without fake metrics."""
        sample_path = DATA_VALIDATION_DIR / "gw_other_validation_sample.csv"
        if not sample_path.is_file():
            pytest.skip("Validation sample file not yet generated.")

        res = evaluate_validation_file(sample_path)
        assert res["status"] == "validation_pending"
        assert res["labeled_count"] == 0
        assert res["total_sample_size"] == 100
        # Ensure no fabricated precision/recall/F1 exists
        assert "accuracy" not in res
        assert "macro_f1" not in res


class TestSyntheticEvaluationMetrics:
    """Validate mathematical correctness of metric computations on synthetic ground truth."""

    def test_perfect_agreement_metrics(self):
        """2. When predictions perfectly match true labels, accuracy and macro F1 are 1.0."""
        y_true = ["CANCEL", "RETURN-QC-OK", "LOST-TRANSIT", "DUP-PAYMENT"]
        y_pred = ["CANCEL", "RETURN-QC-OK", "LOST-TRANSIT", "DUP-PAYMENT"]

        metrics = compute_classification_metrics(y_true, y_pred)
        assert metrics["sample_size"] == 4
        assert metrics["correct_count"] == 4
        assert metrics["accuracy"] == 1.0
        assert metrics["macro_precision"] == 1.0
        assert metrics["macro_recall"] == 1.0
        assert metrics["macro_f1"] == 1.0
        assert metrics["abstention_count"] == 0
        assert metrics["abstention_rate"] == 0.0

    def test_known_discrepancy_and_confusion_matrix(self):
        """3. Metrics and confusion matrix correctly account for misclassifications."""
        # 4 true samples: 2 CANCEL, 2 RETURN-QC-OK
        # Predictions: 1 CANCEL (correct), 1 RETURN-QC-OK (misclassified as CANCEL)
        # 1 RETURN-QC-OK (correct), 1 None (abstained)
        y_true = ["CANCEL", "CANCEL", "RETURN-QC-OK", "RETURN-QC-OK"]
        y_pred = ["CANCEL", "RETURN-QC-OK", "RETURN-QC-OK", None]

        metrics = compute_classification_metrics(y_true, y_pred)
        assert metrics["sample_size"] == 4
        assert metrics["correct_count"] == 2  # 1 CANCEL + 1 RETURN-QC-OK
        assert metrics["accuracy"] == 0.50
        assert metrics["abstention_count"] == 1
        assert metrics["abstention_rate"] == 0.25

        cm = metrics["confusion_matrix"]
        assert cm.loc["CANCEL", "CANCEL"] == 1
        assert cm.loc["CANCEL", "RETURN-QC-OK"] == 1
        assert cm.loc["RETURN-QC-OK", "RETURN-QC-OK"] == 1
        assert cm.loc["RETURN-QC-OK", "UNCLASSIFIED"] == 1

        # Check CANCEL class: TP=1, FP=0, FN=1 -> Prec=1.0, Rec=0.5, F1=0.6667
        cancel_stats = metrics["per_class"]["CANCEL"]
        assert cancel_stats["precision"] == 1.0
        assert cancel_stats["recall"] == 0.5
        assert abs(cancel_stats["f1"] - 0.6667) < 1e-3

    def test_empty_dataset_handling(self):
        """4. Empty input lists return 0 sample size cleanly without error."""
        metrics = compute_classification_metrics([], [])
        assert metrics["sample_size"] == 0
        assert metrics["accuracy"] == 0.0
        assert metrics["macro_f1"] == 0.0

    def test_synthetic_evaluation_file_workflow(self, tmp_path):
        """5. Complete workflow from synthetic CSV with human labels produces valid evaluation."""
        synthetic_csv = tmp_path / "synthetic_validation.csv"
        df = pd.DataFrame({
            "ticket_id": ["T1", "T2", "T3", "T4"],
            "existing_reason_code": ["GW-OTHER", "GW-OTHER", "GW-OTHER", "GW-OTHER"],
            "predicted_reason_code": ["CANCEL", "RETURN-QC-OK", "LOST-TRANSIT", None],
            "human_label": ["CANCEL", "RETURN-QC-OK", "CANCEL", "DOA-REPL"],
        })
        df.to_csv(synthetic_csv, index=False)

        cm_out = tmp_path / "cm_out.csv"
        res = evaluate_validation_file(synthetic_csv, confusion_matrix_out=cm_out)

        assert res["status"] == "completed"
        assert res["labeled_count"] == 4
        assert res["total_sample_size"] == 4
        assert res["correct_count"] == 2  # T1 (CANCEL) and T2 (RETURN-QC-OK)
        assert res["accuracy"] == 0.50
        assert res["existing_diff_human_count"] == 4  # All 4 human labels differ from GW-OTHER
        assert res["classifier_agree_human_count"] == 2
        assert res["classifier_disagree_human_count"] == 1  # T3 predicted LOST-TRANSIT, human said CANCEL
        assert res["manual_review_needed"] == 1  # T4 predicted None
        assert cm_out.is_file()
