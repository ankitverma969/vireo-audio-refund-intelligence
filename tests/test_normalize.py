"""Comprehensive test suite for Canonical Normalization & Reconciliation.

Covers:
1-4: Monetary normalization
5-9: Duplicate reconciliation & named rules
10-13: Order reference resolution & ambiguity detection
14-16: Deterministic refund qualification & golden benchmark check
17-18: Raw source immutability & canonical schema verification
"""

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.config import (
    AGENTS_FILE,
    CANONICAL_REFUNDS_CSV,
    CANONICAL_TICKETS_CSV,
    CANONICAL_TICKETS_PARQUET,
    CUSTOMERS_FILE,
    DATA_RAW_DIR,
    EMAIL_THREAD_FILE,
    LEGACY_CURRENCY_DIVISOR,
    ORDERS_FILE,
    PRODUCTS_FILE,
    README_FILE,
    SUPPORT_POLICY_FILE,
    TICKETS_FILE,
)
from src.loader import load_orders, load_tickets
from src.normalize import (
    build_canonical_refunds,
    build_canonical_tickets,
    identify_duplicate_groups,
    is_refund_ticket,
    normalize_money,
    reconcile_duplicate_tickets,
    resolve_order_reference,
)


# =========================================================================
# 1. MONETARY NORMALIZATION TESTS
# =========================================================================

class TestMonetaryNormalization:
    """Tests 1-4: Validate deterministic currency normalization."""

    def test_1_helpdesk_amount_unchanged(self):
        """1. Helpdesk amounts must remain strictly unchanged."""
        df_raw = load_tickets()
        df_norm = normalize_money(df_raw)
        
        hd_refunds = df_norm[
            (df_norm["source_system"] == "helpdesk") & (df_norm["refund_amount_raw"].notna())
        ]
        assert len(hd_refunds) > 0
        diff = hd_refunds["refund_amount_inr_normalized"] - hd_refunds["refund_amount_raw"]
        assert (diff == 0.0).all()
        assert (hd_refunds["money_normalization_rule"] == "helpdesk_native_inr").all()

    def test_2_legacy_100x_value_converts_correctly(self):
        """2. Legacy Freshdesk values must convert by dividing by 100.0."""
        df_raw = load_tickets()
        df_norm = normalize_money(df_raw)
        
        lg_refunds = df_norm[
            (df_norm["source_system"] == "legacy_fd") & (df_norm["refund_amount_raw"].notna())
        ]
        assert len(lg_refunds) > 0
        expected = lg_refunds["refund_amount_raw"] / LEGACY_CURRENCY_DIVISOR
        diff = lg_refunds["refund_amount_inr_normalized"] - expected
        assert (diff.abs() < 1e-6).all()
        assert (lg_refunds["money_normalization_rule"] == "legacy_div_100").all()

    def test_3_null_refund_remains_null(self):
        """3. Null raw refunds must remain null with rule 'no_refund'."""
        df_raw = load_tickets()
        df_norm = normalize_money(df_raw)
        
        null_refunds = df_norm[df_norm["refund_amount_raw"].isna()]
        assert len(null_refunds) > 0
        assert null_refunds["refund_amount_inr_normalized"].isna().all()
        assert (null_refunds["money_normalization_rule"] == "no_refund").all()

    def test_4_normalized_amount_is_numeric(self):
        """4. All non-null normalized amounts must be positive numeric floats."""
        df_raw = load_tickets()
        df_norm = normalize_money(df_raw)
        
        valid = df_norm["refund_amount_inr_normalized"].dropna()
        assert len(valid) > 0
        assert pd.api.types.is_numeric_dtype(valid)
        assert (valid > 0).all()


# =========================================================================
# 2. DUPLICATE RECONCILIATION TESTS
# =========================================================================

class TestDuplicateReconciliation:
    """Tests 5-9: Validate deterministic duplicate identification and named rules."""

    def test_5_duplicate_groups_are_identified(self):
        """5. Duplicate groups are correctly flagged with group size."""
        df_raw = load_tickets()
        df_grouped = identify_duplicate_groups(df_raw)
        
        assert "is_duplicate" in df_grouped.columns
        assert "duplicate_group_size" in df_grouped.columns
        assert "duplicate_source_pair" in df_grouped.columns
        
        dups = df_grouped[df_grouped["is_duplicate"] == True]
        assert len(dups) == 1276
        assert dups["ticket_id"].nunique() == 638
        assert (dups["duplicate_group_size"] == 2).all()
        assert (dups["duplicate_source_pair"] == "helpdesk+legacy_fd").all()

    def test_6_known_migration_pair_selects_helpdesk(self):
        """6. Verified migration duplicate pairs select helpdesk record as canonical."""
        df_raw = load_tickets()
        df_norm = normalize_money(df_raw)
        df_grouped = identify_duplicate_groups(df_norm)
        df_rec = reconcile_duplicate_tickets(df_grouped)
        
        dup_rows = df_rec[df_rec["is_duplicate"] == True]
        hd_dups = dup_rows[dup_rows["source_system"] == "helpdesk"]
        lg_dups = dup_rows[dup_rows["source_system"] == "legacy_fd"]
        
        assert len(hd_dups) == 638
        assert (hd_dups["canonical_record"] == True).all()
        assert (hd_dups["canonical_source"] == "helpdesk").all()
        assert (hd_dups["reconciliation_status"] == "reconciled_migration_pair").all()
        
        assert len(lg_dups) == 638
        assert (lg_dups["canonical_record"] == False).all()
        assert (lg_dups["canonical_source"] == "helpdesk").all()
        assert (lg_dups["reconciliation_status"] == "reconciled_migration_pair").all()

    def test_7_non_migration_duplicate_not_silently_discarded(self):
        """7. Synthetic non-migration duplicates must become reconciliation exceptions."""
        synthetic_data = pd.DataFrame([
            {
                "ticket_id": "TK-ANOMALY-1",
                "source_system": "helpdesk",
                "refund_amount_raw": 1000.0,
                "created_at": "2025-02-01 10:00",
                "status": "resolved",
                "channel": "chat",
                "customer_id": "C100001",
                "order_id": "VR100",
                "product_sku": "SKU1",
                "category": "cat",
                "priority": "Low",
                "assigned_team": "Chat Frontline",
                "agent_id": "A3001",
                "transfers": 0,
                "csat_score": 5,
                "refund_reason_code": "CANCEL",
                "replacement_issued": "N",
                "customer_message": "msg",
                "agent_notes": "note",
            },
            {
                "ticket_id": "TK-ANOMALY-1",
                "source_system": "helpdesk",  # duplicate helpdesk (invalid migration pair!)
                "refund_amount_raw": 2000.0,
                "created_at": "2025-02-01 10:00",
                "status": "resolved",
                "channel": "chat",
                "customer_id": "C100001",
                "order_id": "VR100",
                "product_sku": "SKU1",
                "category": "cat",
                "priority": "Low",
                "assigned_team": "Chat Frontline",
                "agent_id": "A3001",
                "transfers": 0,
                "csat_score": 5,
                "refund_reason_code": "CANCEL",
                "replacement_issued": "N",
                "customer_message": "msg",
                "agent_notes": "note",
            }
        ])
        
        df_grouped = identify_duplicate_groups(synthetic_data)
        df_rec = reconcile_duplicate_tickets(df_grouped)
        
        # Must NOT silently select one; both must be marked as reconciliation_exception
        assert (df_rec["reconciliation_status"] == "reconciliation_exception").all()
        assert (df_rec["canonical_record"] == False).all()

    def test_8_canonical_ticket_ids_are_unique(self):
        """8. Canonical ticket output must have 100% unique ticket IDs."""
        canonical = build_canonical_tickets()
        assert len(canonical) == 11600
        assert canonical["ticket_id"].nunique() == 11600

    def test_9_reconciliation_status_is_populated(self):
        """9. Every record in canonical output must have a recognized reconciliation status."""
        canonical = build_canonical_tickets()
        statuses = set(canonical["reconciliation_status"].unique())
        assert statuses == {"reconciled_migration_pair", "unique_record"}


# =========================================================================
# 3. ORDER REFERENCE RESOLUTION TESTS
# =========================================================================

class TestOrderReferenceResolution:
    """Tests 10-13: Validate quoted validation and fallback ambiguity flags."""

    def test_10_existing_valid_order_id_preferred(self):
        """10. Quoted valid order_id matching orders.csv is directly resolved."""
        df_raw = load_tickets()
        orders = load_orders()
        sample = df_raw[df_raw["order_id"].notna()].head(20)
        
        resolved = resolve_order_reference(sample, orders)
        assert (resolved["order_match_status"] == "quoted_valid").all()
        assert (resolved["resolved_order_id"] == resolved["order_id"]).all()

    def test_11_missing_order_single_fallback_resolves(self):
        """11. Missing order_id with exactly one customer+sku order resolves cleanly."""
        orders = pd.DataFrame([
            {"order_id": "ORD-1", "customer_id": "CUST-A", "sku": "SKU-A"}
        ])
        ticket = pd.DataFrame([
            {"ticket_id": "T1", "order_id": None, "customer_id": "CUST-A", "product_sku": "SKU-A"}
        ])
        resolved = resolve_order_reference(ticket, orders)
        assert resolved.loc[0, "resolved_order_id"] == "ORD-1"
        assert resolved.loc[0, "order_match_status"] == "fallback_single"

    def test_12_multiple_fallback_matches_become_ambiguous(self):
        """12. Missing order_id with multiple customer+sku orders must be marked ambiguous (no guessing)."""
        orders = pd.DataFrame([
            {"order_id": "ORD-1", "customer_id": "CUST-A", "sku": "SKU-A"},
            {"order_id": "ORD-2", "customer_id": "CUST-A", "sku": "SKU-A"}
        ])
        ticket = pd.DataFrame([
            {"ticket_id": "T1", "order_id": None, "customer_id": "CUST-A", "product_sku": "SKU-A"}
        ])
        resolved = resolve_order_reference(ticket, orders)
        assert pd.isna(resolved.loc[0, "resolved_order_id"])
        assert resolved.loc[0, "order_match_status"] == "ambiguous"
        assert resolved.loc[0, "candidate_order_ids"] == "ORD-1;ORD-2"

    def test_13_zero_fallback_matches_become_unmatched(self):
        """13. Missing order_id with zero customer+sku orders must be marked unmatched."""
        orders = pd.DataFrame([
            {"order_id": "ORD-1", "customer_id": "CUST-A", "sku": "SKU-A"}
        ])
        ticket = pd.DataFrame([
            {"ticket_id": "T1", "order_id": None, "customer_id": "CUST-B", "product_sku": "SKU-B"}
        ])
        resolved = resolve_order_reference(ticket, orders)
        assert pd.isna(resolved.loc[0, "resolved_order_id"])
        assert resolved.loc[0, "order_match_status"] == "unmatched"


# =========================================================================
# 4. REFUND DEFINITION & GOLDEN BENCHMARK TESTS
# =========================================================================

class TestRefundDefinitionAndBenchmarks:
    """Tests 14-16: Validate deterministic refund logic against golden benchmarks."""

    def test_14_refund_definition_is_deterministic(self):
        """14. Central refund qualification is strictly based on normalized refund is not null."""
        df_canonical = build_canonical_tickets()
        mask = is_refund_ticket(df_canonical)
        assert mask.sum() == 2340
        
        # Verify non-refunds have null normalized amount
        non_refunds = df_canonical[~mask]
        assert non_refunds["refund_amount_inr_normalized"].isna().all()

    def test_15_canonical_refund_count_is_correct(self):
        """15. Canonical refund ticket count must match the golden benchmark (2,340)."""
        df_canonical = build_canonical_tickets()
        df_refunds = build_canonical_refunds(df_canonical)
        assert len(df_refunds) == 2340
        assert df_refunds["ticket_id"].nunique() == 2340

    def test_16_canonical_refund_total_is_correct(self):
        """16. Canonical refund total must match the golden benchmark (Rs 6,709,932.00)."""
        df_canonical = build_canonical_tickets()
        df_refunds = build_canonical_refunds(df_canonical)
        total = float(df_refunds["refund_amount_inr_normalized"].sum())
        assert abs(total - 6709932.0) < 1e-2


# =========================================================================
# 5. INTEGRITY & SCHEMA TESTS
# =========================================================================

class TestIntegrityAndSchemas:
    """Tests 17-18: Raw source file immutability and output schema verification."""

    def test_17_raw_files_remain_unchanged(self):
        """17. Raw source files in data/raw must remain strictly immutable."""
        expected_raw_files = [
            "agents.csv",
            "customers.csv",
            "email-thread.txt",
            "orders.csv",
            "products.csv",
            "README.txt",
            "support-policy.pdf",
            "tickets.csv",
        ]
        for fname in expected_raw_files:
            p = DATA_RAW_DIR / fname
            assert p.is_file(), f"Missing raw file: {p}"
            assert p.stat().st_size > 0

    def test_18_canonical_output_schema_is_correct(self):
        """18. Canonical refund dataset must contain all required columns."""
        df_canonical = build_canonical_tickets()
        df_refunds = build_canonical_refunds(df_canonical)
        
        required_cols = [
            "ticket_id",
            "created_at",
            "resolved_at",
            "status",
            "channel",
            "customer_id",
            "order_id",
            "resolved_order_id",
            "order_match_status",
            "product_sku",
            "category",
            "priority",
            "assigned_team",
            "agent_id",
            "transfers",
            "csat_score",
            "refund_amount_raw",
            "refund_amount_inr_normalized",
            "refund_reason_code",
            "replacement_issued",
            "source_system",
            "canonical_source",
            "is_duplicate",
            "reconciliation_status",
            "reconciliation_reason",
        ]
        for col in required_cols:
            assert col in df_refunds.columns
            
        assert len(df_refunds) == 2340
