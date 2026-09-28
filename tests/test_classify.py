"""Test suite for AI-assisted refund reason classification and review triage.

Covers:
- Label space restriction to 8 authoritative policy codes
- Confidence bounded to [0.0, 1.0]
- Insufficient evidence triggers review_required = True
- Original reason code is never overwritten
- Deterministic reproducibility of rule-based baseline
- Deterministic reproducibility of human validation sample (seed=42)
- Review priority triage (HIGH, MEDIUM, LOW)
- Preservation of order match status and replacement flags
"""

import pytest
import pandas as pd
from pathlib import Path

from src.config import DATA_PROCESSED_DIR, DATA_VALIDATION_DIR
from src.classify import (
    AUTHORITATIVE_REASON_CODES,
    ClassificationResult,
    RuleBasedRefundClassifier,
    get_classifier,
    determine_review_priority,
    generate_human_validation_sample,
)


@pytest.fixture(scope="module")
def canonical_tickets_df():
    parquet_path = DATA_PROCESSED_DIR / "canonical_tickets.parquet"
    csv_path = DATA_PROCESSED_DIR / "canonical_tickets.csv"
    if parquet_path.is_file():
        return pd.read_parquet(parquet_path)
    return pd.read_csv(csv_path)


@pytest.fixture(scope="module")
def gw_other_df(canonical_tickets_df):
    return canonical_tickets_df[canonical_tickets_df["refund_reason_code"] == "GW-OTHER"].copy()


class TestClassifierLabelSpaceAndConstraints:
    """Validate label space, schema, and confidence boundaries."""

    def test_authoritative_label_space_has_exact_8_codes(self):
        """1. Authoritative label space must contain exactly the 8 Support Policy codes."""
        expected = {
            "GW-OTHER",
            "DOA-REPL",
            "LOST-TRANSIT",
            "DUP-PAYMENT",
            "CANCEL",
            "PRICE-ADJ",
            "RETURN-QC-OK",
            "WTY-BUYBACK",
        }
        assert set(AUTHORITATIVE_REASON_CODES) == expected
        assert len(AUTHORITATIVE_REASON_CODES) == 8

    def test_classifier_returns_only_allowed_labels_or_none(self, gw_other_df):
        """2. Classifier predictions must strictly be within the 8 codes or None."""
        classifier = RuleBasedRefundClassifier()
        sample = gw_other_df.head(50).to_dict(orient="records")
        results = classifier.classify_batch(sample)

        for res in results:
            if res.predicted_reason_code is not None:
                assert res.predicted_reason_code in AUTHORITATIVE_REASON_CODES

    def test_confidence_is_strictly_bounded(self, gw_other_df):
        """3. Confidence scores must strictly lie in [0.0, 1.0]."""
        classifier = RuleBasedRefundClassifier()
        sample = gw_other_df.head(50).to_dict(orient="records")
        results = classifier.classify_batch(sample)

        for res in results:
            assert 0.0 <= res.confidence <= 1.0

    def test_insufficient_evidence_triggers_review_required(self):
        """4. Tickets with no distinctive policy keywords must require review."""
        classifier = RuleBasedRefundClassifier()
        ambiguous_ticket = {
            "ticket_id": "TK-TEST-001",
            "refund_reason_code": "GW-OTHER",
            "refund_amount_inr_normalized": 3500.0,
            "customer_message": "Hello, please check my account query.",
            "agent_notes": "looked into customer account details ~Agent",
            "replacement_issued": "N",
            "order_match_status": "quoted_valid",
        }
        result = classifier.classify(ambiguous_ticket)

        assert result.predicted_reason_code is None
        assert result.confidence < 0.60
        assert result.review_required is True
        assert result.review_priority == "HIGH"

    def test_original_reason_code_is_never_overwritten(self, gw_other_df):
        """5. Existing reason code in result must exactly preserve the source record."""
        classifier = RuleBasedRefundClassifier()
        ticket = gw_other_df.iloc[0].to_dict()
        original_reason = ticket["refund_reason_code"]
        result = classifier.classify(ticket)

        assert result.existing_reason_code == original_reason
        assert ticket["refund_reason_code"] == original_reason


class TestClassifierDeterminismAndReproducibility:
    """Validate repeatability and determinism across multiple runs."""

    def test_local_classifier_is_deterministic(self, gw_other_df):
        """6. Re-running classification on identical tickets produces identical results."""
        classifier1 = RuleBasedRefundClassifier()
        classifier2 = RuleBasedRefundClassifier()

        sample = gw_other_df.head(25).to_dict(orient="records")
        res1 = classifier1.classify_batch(sample)
        res2 = classifier2.classify_batch(sample)

        for r1, r2 in zip(res1, res2):
            assert r1.predicted_reason_code == r2.predicted_reason_code
            assert abs(r1.confidence - r2.confidence) < 1e-6
            assert r1.review_required == r2.review_required
            assert r1.review_priority == r2.review_priority
            assert r1.evidence_text == r2.evidence_text

    def test_validation_sample_is_reproducible_with_seed(self, gw_other_df):
        """7. Validation sample generation with seed=42 produces identical ticket IDs."""
        sample1 = generate_human_validation_sample(gw_other_df, sample_size=100, seed=42)
        sample2 = generate_human_validation_sample(gw_other_df, sample_size=100, seed=42)

        assert len(sample1) == 100
        assert len(sample2) == 100
        assert list(sample1["ticket_id"]) == list(sample2["ticket_id"])

    def test_validation_sample_leaves_human_fields_blank(self, gw_other_df):
        """8. Generated validation sample must leave human audit fields unpopulated."""
        sample = generate_human_validation_sample(gw_other_df, sample_size=50, seed=42)
        assert (sample["human_label"] == "").all()
        assert (sample["human_reviewer"] == "").all()
        assert (sample["review_notes"] == "").all()


class TestReviewPrioritization:
    """Validate deterministic review prioritization rules."""

    def test_high_priority_triggers_on_ambiguous_order(self):
        """9. Ambiguous order status triggers HIGH review priority."""
        prio, req = determine_review_priority(
            existing_reason="GW-OTHER",
            predicted_reason="RETURN-QC-OK",
            confidence=0.85,
            refund_amount=1500.0,
            replacement_issued="N",
            order_match_status="ambiguous",
        )
        assert prio == "HIGH"
        assert req is True

    def test_high_priority_triggers_on_double_dip(self):
        """10. Replacement issued ('Y') triggers HIGH review priority."""
        prio, req = determine_review_priority(
            existing_reason="GW-OTHER",
            predicted_reason="DOA-REPL",
            confidence=0.90,
            refund_amount=2000.0,
            replacement_issued="Y",
            order_match_status="quoted_valid",
        )
        assert prio == "HIGH"
        assert req is True

    def test_high_priority_triggers_on_large_refund_reclassification(self):
        """11. High refund amount (>= Rs 5,000) with reason discrepancy triggers HIGH priority."""
        prio, req = determine_review_priority(
            existing_reason="GW-OTHER",
            predicted_reason="CANCEL",
            confidence=0.85,
            refund_amount=6500.0,
            replacement_issued="N",
            order_match_status="quoted_valid",
        )
        assert prio == "HIGH"
        assert req is True

    def test_low_priority_when_reasons_agree_with_high_confidence(self):
        """12. Agreement between existing reason and prediction with high confidence is LOW priority."""
        prio, req = determine_review_priority(
            existing_reason="RETURN-QC-OK",
            predicted_reason="RETURN-QC-OK",
            confidence=0.90,
            refund_amount=1200.0,
            replacement_issued="N",
            order_match_status="quoted_valid",
        )
        assert prio == "LOW"
        assert req is False
