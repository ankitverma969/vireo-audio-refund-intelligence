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


def generate_validation_report(
    eval_result: Dict[str, Any],
    sample_df: pd.DataFrame,
    ai_sample_path: Optional[Path],
    output_path: Path,
) -> None:
    """Generate reports/ai-validation.md documenting validation status and multi-way agreement."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = len(sample_df)
    labeled_count = eval_result.get("labeled_count", 0)

    # Inspect AI sample results if present
    ai_sample_df = None
    if ai_sample_path is not None and ai_sample_path.is_file():
        try:
            ai_sample_df = pd.read_csv(ai_sample_path)
        except Exception:
            ai_sample_df = None

    md = [
        "# Vireo Audio — AI Classification Validation & Multi-Way Agreement Report",
        "",
        "> **Audit Standard**: Evaluates model performance against human ground truth and inspects model agreement.",
        "> **Methodological Rule**: Never treat existing reason codes, rule-based outputs, or LLM predictions as ground truth.",
        "",
        "---",
        "",
        "## 1. Validation Status & Ground Truth Availability",
        "",
        f"- **Validation Sample Size**: **{total_samples:,} tickets** (stratified random sample, `seed=42`)",
        f"- **Verified Human Annotations Completed**: **{labeled_count:,} / {total_samples:,}**",
    ]

    if labeled_count == 0:
        md.extend([
            f"- **Validation Benchmark Status**: **PENDING HUMAN AUDIT**",
            "",
            "> [!IMPORTANT]",
            "> **Formal model accuracy has not yet been established because human ground truth is pending.**",
            "> No synthetic or fabricated labels have been substituted. Accuracy, precision, recall, and F1 metrics",
            "> will be computed exclusively once operational reviewers populate `human_label` in `data/validation/gw_other_validation_sample.csv`.",
        ])
    else:
        acc = eval_result.get("accuracy", 0.0)
        macro_f1 = eval_result.get("macro_f1", 0.0)
        macro_p = eval_result.get("macro_precision", 0.0)
        macro_r = eval_result.get("macro_recall", 0.0)
        abst_rate = eval_result.get("abstention_rate", 0.0)

        md.extend([
            f"- **Validation Benchmark Status**: **COMPLETED ON {labeled_count} LABELED TICKETS**",
            f"- **Exact Accuracy vs Human**: **{acc:.1%}**",
            f"- **Macro F1 Score**: **{macro_f1:.3f}**",
            f"- **Macro Precision**: **{macro_p:.3f}**",
            f"- **Macro Recall**: **{macro_r:.3f}**",
            f"- **Model Abstention / Review Rate**: **{abst_rate:.1%}**",
            f"- **Existing Reason Mismatched Human**: **{eval_result.get('existing_diff_human_count', 0)} tickets**",
            f"- **Model Agreed with Human**: **{eval_result.get('classifier_agree_human_count', 0)} tickets**",
            f"- **Model Disagreed with Human**: **{eval_result.get('classifier_disagree_human_count', 0)} tickets**",
        ])

    md.extend([
        "",
        "---",
        "",
        "## 2. Multi-Way Classifier Agreement Analysis",
        "",
    ])

    if ai_sample_df is not None and not ai_sample_df.empty:
        n_ai = len(ai_sample_df)
        agr_counts = ai_sample_df["agreement_rule_vs_llm"].value_counts().to_dict()
        pending_cred = agr_counts.get("PENDING_CREDENTIALS", 0)

        md.append(f"Analyzed controlled subset of **{n_ai} tickets** from the human validation sample:\n")

        if pending_cred > 0:
            md.extend([
                "- **LLM Execution Status**: `LLM execution pending credentials (OPENAI_API_KEY not configured)`",
                "- **Live API Calls Made**: `0`",
                "- **Rule-Based Predictions**: Successfully computed for all 30 sample tickets.",
                "- **LLM Agreement Calculation**: Deferred until API credentials are provided.",
                "",
                "To execute live LLM comparison on this subset:",
                "```bash",
                "export OPENAI_API_KEY=your_key_here",
                "python -m src.classify",
                "python -m src.evaluate_classifier",
                "```",
            ])
        else:
            agree_count = agr_counts.get("AGREE", 0)
            disagree_count = agr_counts.get("DISAGREE", 0)
            unclass_count = agr_counts.get("BOTH_UNCLASSIFIED", 0)
            partial_count = agr_counts.get("PARTIAL_ABSTAIN", 0)

            agree_pct = (agree_count / n_ai) if n_ai > 0 else 0.0

            md.extend([
                f"- **Total Controlled AI Subset**: **{n_ai} tickets**",
                f"- **Exact Agreement (Rule-Based == LLM)**: **{agree_count} tickets ({agree_pct:.1%})**",
                f"- **Disagreements**: **{disagree_count} tickets**",
                f"- **Both Abstained / Unclassified**: **{unclass_count} tickets**",
                f"- **Partial Abstention (One Model Abstained)**: **{partial_count} tickets**",
                "",
                "### Disagreement & Edge Case Examples",
                "",
                "| Ticket ID | Existing Reason | Rule-Based Prediction | LLM Prediction | LLM Confidence | Notes |",
                "| :--- | :--- | :--- | :--- | :---: | :--- |",
            ])

            disagreements = ai_sample_df[ai_sample_df["agreement_rule_vs_llm"].isin(["DISAGREE", "PARTIAL_ABSTAIN"])]
            for _, r in disagreements.head(5).iterrows():
                md.append(
                    f"| `{r['ticket_id']}` | `{r['existing_reason_code']}` | `{r['rule_based_prediction']}` | "
                    f"`{r['llm_prediction']}` | {r['llm_confidence']} | {str(r['llm_explanation'])[:60]}... |"
                )
    else:
        md.append("- No AI sample results available yet. Run `python -m src.classify` to generate `reports/ai_sample_results.csv`.\n")

    md.extend([
        "",
        "---",
        "",
        "## 3. Review Workflow & Next Steps for Operational Leads",
        "",
        "1. Open `data/validation/gw_other_validation_sample.csv` in Excel or an internal audit tool.",
        "2. For each of the 100 tickets, review `customer_message`, `agent_notes`, and `refund_amount_inr_normalized` against Support Policy §5.",
        "3. Enter the authoritative policy code into `human_label` (`GW-OTHER`, `DOA-REPL`, `LOST-TRANSIT`, `DUP-PAYMENT`, `CANCEL`, `PRICE-ADJ`, `RETURN-QC-OK`, `WTY-BUYBACK`).",
        "4. Record `human_reviewer` initials and brief `review_notes`.",
        "5. Save the CSV and run:",
        "   ```bash",
        "   python -m src.evaluate_classifier",
        "   ```",
        "6. The evaluation engine will automatically compute exact accuracy, macro F1, and export `reports/classification_confusion_matrix.csv`.",
        "",
        "---",
        "",
        "## 4. Limitations & Governance Safeguards",
        "",
        "- **Lexical Ambiguity**: Rule-based baseline relies on deterministic pattern weights; edge cases with conflicting customer narratives are routed to HIGH priority review.",
        "- **Zero Automated Mutations**: Predictions are advisory. The canonical financial ledger (`canonical_tickets.parquet`) is never modified by the classifier.",
        "- **No Misconduct Inferences**: Models do not score agent integrity or performance.",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main() -> None:
    """CLI Entrypoint for running classifier evaluation."""
    print("=" * 60)
    print("Vireo Audio — Classification Evaluation Engine")
    print("=" * 60)

    sample_file = DATA_VALIDATION_DIR / "gw_other_validation_sample.csv"
    cm_file = REPORTS_DIR / "classification_confusion_matrix.csv"
    ai_sample_file = REPORTS_DIR / "ai_sample_results.csv"
    validation_report_file = REPORTS_DIR / "ai-validation.md"

    print(f"\n[1/2] Evaluating human validation sample: {sample_file}")
    res = evaluate_validation_file(sample_file, confusion_matrix_out=cm_file)

    sample_df = pd.read_csv(sample_file) if sample_file.is_file() else pd.DataFrame()

    print(f"[2/2] Generating multi-way validation report: {validation_report_file}")
    generate_validation_report(
        eval_result=res,
        sample_df=sample_df,
        ai_sample_path=ai_sample_file,
        output_path=validation_report_file,
    )

    if res["status"] == "validation_pending":
        print("\n[VALIDATION STATUS]: PENDING HUMAN AUDIT")
        print(f"  • Total Sample Tickets: {res['total_sample_size']}")
        print(f"  • Labeled Tickets: {res['labeled_count']}")
        print(f"  • Note: {res['message']}")
        print("  • No metrics fabricated. Evaluation ready for verified labels.")
        print(f"  • Validation report written to: {validation_report_file}")
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
        print(f"  • Validation report written to: {validation_report_file}")
    else:
        print(f"\n[VALIDATION STATUS]: {res['status'].upper()}")
        print(f"  • Message: {res['message']}")


if __name__ == "__main__":
    main()

