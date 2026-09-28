"""Test suite for Vireo Audio Refund Intelligence data loaders and audit engine.

Validates data loading, schema integrity, duplicate detection, date/numeric parsing,
referential integrity, and monetary normalization logic.
"""

import pandas as pd
import pytest

from src.config import (
    AGENTS_FILE,
    CUSTOMERS_FILE,
    HELPDESK_GO_LIVE_DATE,
    ORDERS_FILE,
    PRODUCTS_FILE,
    TICKETS_FILE,
    VALID_REASON_CODES,
)
from src.loader import (
    EXPECTED_SCHEMAS,
    add_normalized_refund_column,
    load_agents,
    load_customers,
    load_orders,
    load_products,
    load_tickets,
    normalize_refund_value,
    validate_columns,
)
from src.audit import run_comprehensive_audit


class TestDataLoadingAndSchemas:
    """Test CSV loading and column presence."""

    def test_load_agents_schema(self):
        df = load_agents()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 44
        for col in EXPECTED_SCHEMAS["agents"]:
            assert col in df.columns

    def test_load_customers_schema(self):
        df = load_customers()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 9500
        for col in EXPECTED_SCHEMAS["customers"]:
            assert col in df.columns

    def test_load_orders_schema(self):
        df = load_orders()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 15000
        for col in EXPECTED_SCHEMAS["orders"]:
            assert col in df.columns

    def test_load_products_schema(self):
        df = load_products()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 14
        for col in EXPECTED_SCHEMAS["products"]:
            assert col in df.columns

    def test_load_tickets_schema(self):
        df = load_tickets()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 12238
        for col in EXPECTED_SCHEMAS["tickets"]:
            assert col in df.columns

    def test_invalid_schema_detection(self):
        df_invalid = pd.DataFrame({"dummy_col": [1, 2]})
        with pytest.raises(ValueError, match="Missing columns"):
            validate_columns(df_invalid, "agents")


class TestDuplicatesAndSourceSystems:
    """Test duplicate detection and source system categorization."""

    def test_ticket_duplicate_counts(self):
        df = load_tickets()
        unique_ids = df["ticket_id"].nunique()
        assert unique_ids == 11600
        
        dup_mask = df.duplicated(subset=["ticket_id"], keep=False)
        df_dups = df[dup_mask]
        assert len(df_dups) == 1276
        assert df_dups["ticket_id"].nunique() == 638

    def test_duplicate_source_pairings(self):
        df = load_tickets()
        dup_mask = df.duplicated(subset=["ticket_id"], keep=False)
        df_dups = df[dup_mask]
        
        # Every duplicate ticket must have exactly 1 helpdesk and 1 legacy_fd row
        src_counts = (
            df_dups.groupby(["ticket_id", "source_system"])
            .size()
            .unstack(fill_value=0)
        )
        assert (src_counts["helpdesk"] == 1).all()
        assert (src_counts["legacy_fd"] == 1).all()

    def test_source_system_names(self):
        df = load_tickets()
        sources = set(df["source_system"].unique())
        assert sources == {"helpdesk", "legacy_fd"}


class TestDataParsingAndIntegrity:
    """Test date parsing, numeric conversions, and referential constraints."""

    def test_date_parsing_ranges(self):
        df = load_tickets()
        created_dt = pd.to_datetime(df["created_at"])
        assert created_dt.min() >= pd.Timestamp("2025-01-01 00:00:00")
        assert created_dt.max() <= pd.Timestamp("2026-06-30 23:59:59")

    def test_numeric_parsing(self):
        df_tickets = load_tickets()
        refunds = df_tickets["refund_amount_inr"].dropna()
        assert (refunds > 0).all()

        df_orders = load_orders()
        assert (df_orders["order_value_inr"] > 0).all()

        df_products = load_products()
        assert (df_products["unit_cost_inr"] > 0).all()
        assert (df_products["retail_price_inr"] > df_products["unit_cost_inr"]).all()

    def test_referential_integrity(self):
        df_tickets = load_tickets()
        df_customers = load_customers()
        df_agents = load_agents()
        df_products = load_products()
        df_orders = load_orders()

        # All customer_ids in tickets must exist in customers
        assert df_tickets["customer_id"].isin(df_customers["customer_id"]).all()

        # All agent_ids in tickets must exist in agents
        assert df_tickets["agent_id"].isin(df_agents["agent_id"]).all()

        # All product_skus in tickets must exist in products
        assert df_tickets["product_sku"].isin(df_products["sku"]).all()

        # Quoted order_ids in tickets must exist in orders
        quoted_orders = df_tickets["order_id"].dropna()
        assert quoted_orders.isin(df_orders["order_id"]).all()


class TestMonetaryNormalization:
    """Test mathematical proof of 100x ratio and reconciliation totals."""

    def test_duplicate_exact_100x_ratio(self):
        df = load_tickets()
        dup_mask = df.duplicated(subset=["ticket_id"], keep=False)
        df_dups = df[dup_mask]
        
        dup_refunds = df_dups[df_dups["refund_amount_inr"].notna()]
        piv = dup_refunds.pivot(
            index="ticket_id", columns="source_system", values="refund_amount_inr"
        ).dropna()
        
        assert len(piv) == 125
        ratios = piv["legacy_fd"] / piv["helpdesk"]
        assert (ratios == 100.0).all()

    def test_reconciliation_totals(self):
        summary = run_comprehensive_audit()
        scens = summary["monetary_investigation"]["reconciliation_scenarios"]
        
        # Raw export sum must match the un-normalized figure (~23.01 Crore)
        assert scens["scenario_a_raw_export"]["total_inr"] == 230124081.0
        
        # Reconciled sum must equal exactly Rs 6,709,932.00 (~11.18 Lakh / quarter)
        assert scens["scenario_d_reconciled"]["total_inr"] == 6709932.0
        assert scens["scenario_d_reconciled"]["count"] == 2340

    def test_normalized_refund_does_not_exceed_order_value(self):
        summary = run_comprehensive_audit()
        order_val = summary["monetary_investigation"]["refund_vs_order_validation"]
        assert order_val["exceeding_order_count"] == 0
        assert order_val["max_ratio"] <= 1.0


class TestReasonCodesAndAnomalies:
    """Test policy constraint verification."""

    def test_reason_codes_validity(self):
        df = load_tickets()
        non_null_codes = df["refund_reason_code"].dropna().unique()
        for code in non_null_codes:
            assert code in VALID_REASON_CODES

    def test_double_dips_detected(self):
        summary = run_comprehensive_audit()
        double_dips = summary["anomalies"]["double_dips"]
        # Exactly 166 unique tickets have both refund and replacement
        assert double_dips["count"] == 166
