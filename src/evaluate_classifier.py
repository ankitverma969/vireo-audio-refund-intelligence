"""Evaluation module for refund reason classification against human validation labels.

Calculates:
- Sample size and labeled coverage
- Exact accuracy
- Macro precision, recall, and F1
- Per-class confusion matrix
- Classifier agreement vs existing reason code discrepancy
- Abstention / review rate

Handles unvalidated states gracefully without fabricating metrics.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np

from src.config import DATA_VALIDATION_DIR, REPORTS_DIR
from src.classify import AUTHORITATIVE_REASON_CODES


def compute_classification_metrics(
    y_true: List[str],
    y_pred: List[Optional[str]],
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Pure mathematical computation of classification metrics.
    
    Handles unclassified / abstained predictions (None) cleanly.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have identical length.")
    
    if len(y_true) == 0:
        return {
            "sample_size": 0,
            "accuracy": 0.0,
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "confusion_matrix": pd.DataFrame(),
            "per_class": {},
            "abstention_count": 0,
            "abstention_rate": 0.0,
        }

    all_labels = labels or AUTHORITATIVE_REASON_CODES
    
    # Track predictions including unclassified
    clean_true = [str(t).strip() for t in y_true]
    clean_pred = [str(p).strip() if (pd.notna(p) and p is not None) else "UNCLASSIFIED" for p in y_pred]

    total_samples = len(clean_true)
    correct_count = sum(1 for t, p in zip(clean_true, clean_pred) if t == p)
    accuracy = correct_count / total_samples

    # Build confusion matrix
    cm_cols = all_labels + ["UNCLASSIFIED"] if "UNCLASSIFIED" in clean_pred else all_labels
    cm_df = pd.DataFrame(0, index=all_labels, columns=cm_cols)

    for t, p in zip(clean_true, clean_pred):
        if t in cm_df.index:
            if p in cm_df.columns:
                cm_df.loc[t, p] += 1
            else:
                if "UNCLASSIFIED" not in cm_df.columns:
                    cm_df["UNCLASSIFIED"] = 0
                cm_df.loc[t, "UNCLASSIFIED"] += 1

    # Per-class precision, recall, F1
    per_class: Dict[str, Dict[str, float]] = {}
    precisions: List[float] = []
    recalls: List[float] = []
    f1s: List[float] = []

    for cls in all_labels:
        tp = sum(1 for t, p in zip(clean_true, clean_pred) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(clean_true, clean_pred) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(clean_true, clean_pred) if t == cls and p != cls)
        support = sum(1 for t in clean_true if t == cls)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

        per_class[cls] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": support,
        }

        # Include in macro average only if class is present in true ground truth
        if support > 0:
            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

    macro_p = float(np.mean(precisions)) if precisions else 0.0
    macro_r = float(np.mean(recalls)) if recalls else 0.0
    macro_f1 = float(np.mean(f1s)) if f1s else 0.0

    abstention_count = sum(1 for p in clean_pred if p == "UNCLASSIFIED")
    abstention_rate = abstention_count / total_samples

    return {
        "sample_size": total_samples,
        "correct_count": correct_count,
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "macro_f1": round(macro_f1, 4),
        "confusion_matrix": cm_df,
        "per_class": per_class,
        "abstention_count": abstention_count,
        "abstention_rate": round(abstention_rate, 4),
    }


def evaluate_validation_file(
    sample_path: Path,
    confusion_matrix_out: Optional[Path] = None,
) -> Dict[str, Any]:
    """Inspect and evaluate human review validation sample file."""
    if not sample_path.is_file():
        return {
            "status": "missing_file",
            "message": f"Validation sample file not found at: {sample_path}",
            "total_sample_size": 0,
            "labeled_count": 0,
        }

    df = pd.read_csv(sample_path)
    total_samples = len(df)

    # Check for non-blank human labels
    if "human_label" not in df.columns:
        return {
            "status": "invalid_schema",
            "message": "Missing 'human_label' column in validation dataset.",
            "total_sample_size": total_samples,
            "labeled_count": 0,
        }

    # Clean human labels
    df["clean_human_label"] = df["human_label"].fillna("").astype(str).str.strip()
    df_labeled = df[df["clean_human_label"] != ""].copy()
    labeled_count = len(df_labeled)

    if labeled_count == 0:
        return {
            "status": "validation_pending",
            "message": (
                "Validation not yet completed: 0 human-labeled rows found in "
                f"{sample_path.name}. Evaluation metrics will be calculated "
                "once verified human labels are populated."
            ),
            "total_sample_size": total_samples,
            "labeled_count": 0,
        }

    # Evaluate labeled rows
    y_true = df_labeled["clean_human_label"].tolist()
    y_pred = df_labeled["predicted_reason_code"].tolist()
    existing_reasons = df_labeled["existing_reason_code"].tolist()

    metrics = compute_classification_metrics(y_true, y_pred)

    # Discrepancy calculations
    existing_diff_human = sum(1 for e, h in zip(existing_reasons, y_true) if e != h)
    classifier_agree_human = sum(1 for p, h in zip(y_pred, y_true) if p == h)
    classifier_disagree_human = sum(1 for p, h in zip(y_pred, y_true) if p != h and pd.notna(p))
    manual_review_needed = sum(1 for p in y_pred if pd.isna(p) or p is None)

    metrics["status"] = "completed"
    metrics["total_sample_size"] = total_samples
    metrics["labeled_count"] = labeled_count
    metrics["existing_diff_human_count"] = existing_diff_human
    metrics["classifier_agree_human_count"] = classifier_agree_human
    metrics["classifier_disagree_human_count"] = classifier_disagree_human
    metrics["manual_review_needed"] = manual_review_needed

    if confusion_matrix_out is not None:
        confusion_matrix_out.parent.mkdir(parents=True, exist_ok=True)
        metrics["confusion_matrix"].to_csv(confusion_matrix_out, index=True)

    return metrics


def main() -> None:
    """CLI Entrypoint for running classifier evaluation."""
    print("=" * 60)
    print("Vireo Audio — Classification Evaluation Engine")
    print("=" * 60)

    sample_file = DATA_VALIDATION_DIR / "gw_other_validation_sample.csv"
    cm_file = REPORTS_DIR / "classification_confusion_matrix.csv"

    print(f"\nEvaluating validation sample: {sample_file}")
    res = evaluate_validation_file(sample_file, confusion_matrix_out=cm_file)

    if res["status"] == "validation_pending":
        print("\n[VALIDATION STATUS]: PENDING HUMAN AUDIT")
        print(f"  • Total Sample Tickets: {res['total_sample_size']}")
        print(f"  • Labeled Tickets: {res['labeled_count']}")
        print(f"  • Note: {res['message']}")
        print("  • No metrics fabricated. Evaluation ready for verified labels.")
    elif res["status"] == "completed":
        print("\n[VALIDATION STATUS]: EVALUATION COMPLETED")
        print(f"  • Sample Size: {res['labeled_count']} / {res['total_sample_size']}")
        print(f"  • Exact Accuracy: {res['accuracy']:.1%}")
        print(f"  • Macro F1 Score: {res['macro_f1']:.3f}")
        print(f"  • Macro Precision: {res['macro_precision']:.3f}")
        print(f"  • Macro Recall: {res['macro_recall']:.3f}")
        print(f"  • Abstention / Review Rate: {res['abstention_rate']:.1%}")
        print(f"  • Classifier Agreed with Human: {res['classifier_agree_human_count']}")
        print(f"  • Classifier Disagreed with Human: {res['classifier_disagree_human_count']}")
        print(f"  • Existing Code Mismatched Human: {res['existing_diff_human_count']}")
        print(f"  • Confusion Matrix exported to: {cm_file}")
    else:
        print(f"\n[VALIDATION STATUS]: {res['status'].upper()}")
        print(f"  • Message: {res['message']}")


if __name__ == "__main__":
    main()
