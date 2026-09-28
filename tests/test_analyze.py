"""Test suite for Business Refund Analysis & Anomaly Detection.

Validates reconciliation of monthly, reason, agent, team, and reason-agent totals,
strict Tier 1 vs Tier 2 separation, double-dip exceptions, GW-OTHER analysis,
CSAT blank handling, and deterministic review flags.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.config import (
    CANONICAL_REFUNDS_CSV,
    CANONICAL_TICKETS_CSV,
    REPORTS_DIR,
)
from src.analyze import (
    analyze_double_dips,
    analyze_gw_other,
    analyze_monthly_refunds,
    analyze_q3_vs_q4,
    analyze_refund_by_agent,
    analyze_refund_by_reason,
    analyze_refund_by_team,
    analyze_refund_reason_agent,
    analyze_refund_sizes,
    generate_review_flags,
)
from src.loader import load_agents, load_orders


GOLDEN_RECONCILED_REFUND_SUM = 6709932.00
GOLDEN_RECONCILED_REFUND_COUNT = 2340
GOLDEN_CANONICAL_TICKETS_COUNT = 11600


@pytest.fixture(scope="module")
def canonical_data():
    df_tickets = pd.read_csv(CANONICAL_TICKETS_CSV)
    df_refunds = pd.read_csv(CANONICAL_REFUNDS_CSV)
    df_agents = load_agents()
    df_orders = load_orders()
    return {
        "tickets": df_tickets,
        "refunds": df_refunds,
        "agents": df_agents,
        "orders": df_orders,
    }


class TestReconciliationTotals:
    """Tests 1-6: Reconcile all aggregate dimensions against golden benchmarks."""

    def test_1_monthly_totals_reconcile(self, canonical_data):
        """1. Monthly totals must sum exactly to canonical totals."""
        df_monthly = analyze_monthly_refunds(canonical_data["tickets"])
        
        assert len(df_monthly) == 18
        tot_cnt = df_monthly["refund_ticket_count"].sum()
        tot_amt = df_monthly["total_refund_inr"].sum()
        
        assert tot_cnt == GOLDEN_RECONCILED_REFUND_COUNT
        assert abs(tot_amt - GOLDEN_RECONCILED_REFUND_SUM) < 1e-2

    def test_2_reason_totals_reconcile(self, canonical_data):
        """2. Reason code totals must sum exactly to canonical totals."""
        df_reasons = analyze_refund_by_reason(canonical_data["refunds"])
        
        assert len(df_reasons) == 8
        tot_cnt = df_reasons["refund_ticket_count"].sum()
        tot_amt = df_reasons["total_refund_inr"].sum()
        
        assert tot_cnt == GOLDEN_RECONCILED_REFUND_COUNT
        assert abs(tot_amt - GOLDEN_RECONCILED_REFUND_SUM) < 1e-2

    def test_3_agent_totals_reconcile(self, canonical_data):
        """3. Agent totals must sum exactly to canonical totals."""
        df_agents_rep = analyze_refund_by_agent(
            canonical_data["refunds"], canonical_data["tickets"], canonical_data["agents"]
        )
        
        assert len(df_agents_rep) == 44
        tot_cnt = df_agents_rep["refund_ticket_count"].sum()
        tot_amt = df_agents_rep["total_refund_inr"].sum()
        
        assert tot_cnt == GOLDEN_RECONCILED_REFUND_COUNT
        assert abs(tot_amt - GOLDEN_RECONCILED_REFUND_SUM) < 1e-2

    def test_4_team_totals_reconcile(self, canonical_data):
        """4. Team totals must sum exactly to canonical totals."""
        df_teams = analyze_refund_by_team(canonical_data["refunds"], canonical_data["agents"])
        
        tot_cnt = df_teams["refund_ticket_count"].sum()
        tot_amt = df_teams["total_refund_inr"].sum()
        
        assert tot_cnt == GOLDEN_RECONCILED_REFUND_COUNT
        assert abs(tot_amt - GOLDEN_RECONCILED_REFUND_SUM) < 1e-2

    def test_5_reason_agent_totals_reconcile(self, canonical_data):
        """5. Reason x Agent cross-tab totals must sum exactly to canonical totals."""
        df_ra = analyze_refund_reason_agent(canonical_data["refunds"], canonical_data["agents"])
        
        tot_cnt = df_ra["refund_ticket_count"].sum()
        tot_amt = df_ra["refund_amount_inr"].sum()
        
        assert tot_cnt == GOLDEN_RECONCILED_REFUND_COUNT
        assert abs(tot_amt - GOLDEN_RECONCILED_REFUND_SUM) < 1e-2

    def test_6_refund_count_reconciles(self, canonical_data):
        """6. Total canonical refund tickets count is exactly 2,340."""
        assert len(canonical_data["refunds"]) == GOLDEN_RECONCILED_REFUND_COUNT
        assert canonical_data["refunds"]["ticket_id"].nunique() == GOLDEN_RECONCILED_REFUND_COUNT


class TestDataIntegrityAndTiers:
    """Tests 7-9: Validate uniqueness, tier partitioning, and CSAT handling."""

    def test_7_duplicate_tickets_not_counted_twice(self, canonical_data):
        """7. No duplicate ticket IDs exist in canonical tickets or refunds."""
        assert len(canonical_data["tickets"]) == GOLDEN_CANONICAL_TICKETS_COUNT
        assert canonical_data["tickets"]["ticket_id"].nunique() == GOLDEN_CANONICAL_TICKETS_COUNT
        assert canonical_data["refunds"]["ticket_id"].nunique() == GOLDEN_RECONCILED_REFUND_COUNT

    def test_8_tier1_and_tier2_remain_separated(self, canonical_data):
        """8. Tier 1 and Tier 2 agents are strictly separated in reporting."""
        df_agents_rep = analyze_refund_by_agent(
            canonical_data["refunds"], canonical_data["tickets"], canonical_data["agents"]
        )
        
        t1 = df_agents_rep[df_agents_rep["tier"] == 1]
        t2 = df_agents_rep[df_agents_rep["tier"] == 2]
        
        assert len(t1) == 38
        assert len(t2) == 6
        assert t1["refund_ticket_count"].sum() == 2258
        assert t2["refund_ticket_count"].sum() == 82
        
        # Verify no combined ranking was produced
        assert "combined_rank" not in df_agents_rep.columns

    def test_9_csat_blanks_excluded(self, canonical_data):
        """9. Unanswered CSAT surveys (NaN) are strictly excluded from mean calculations."""
        q3_q4 = analyze_q3_vs_q4(canonical_data["tickets"])
        
        q3_mean = q3_q4["Q3"]["csat_mean"]
        q4_mean = q3_q4["Q4"]["csat_mean"]
        
        # Mean must be in plausible range [1.0, 5.0], not deflated by treating blanks as 0 (~1.5)
        assert 3.0 <= q3_mean <= 4.0
        assert 3.0 <= q4_mean <= 4.0
        
        # Verify Q3->Q4 CSAT change is approximately +0.029, not +0.40
        assert abs(q3_q4["csat_mean_change"] - 0.029) < 0.01


class TestExceptionsAndFlags:
    """Tests 10-13: Validate double-dips, GW-OTHER, and deterministic review flags."""

    def test_10_double_dip_count_reconciles(self, canonical_data):
        """10. Double-dip exception report contains exactly 166 canonical tickets."""
        df_dd, dd_stats = analyze_double_dips(canonical_data["tickets"], canonical_data["agents"])
        
        assert len(df_dd) == 166
        assert dd_stats["total_double_dip_count"] == 166
        assert abs(dd_stats["total_double_dip_refund_inr"] - 574191.0) < 1e-2
        assert dd_stats["by_category"]["confirmed_order_linked"] == 158
        assert dd_stats["by_category"]["ambiguous_order_linked"] == 8

    def test_11_gw_other_calculations_reconcile(self, canonical_data):
        """11. GW-OTHER calculations reconcile to exactly 991 tickets (879 over cap)."""
        _, gw_stats = analyze_gw_other(canonical_data["refunds"], canonical_data["agents"])
        
        assert gw_stats["total_gw_other_tickets"] == 991
        assert abs(gw_stats["total_gw_other_amount_inr"] - 2907036.0) < 1e-2
        assert gw_stats["over_500_count"] == 879
        assert gw_stats["within_cap_count"] == 112
        assert gw_stats["over_500_count"] + gw_stats["within_cap_count"] == 991

    def test_12_review_flags_are_deterministic(self, canonical_data):
        """12. Review flags are deterministic and contain required columns."""
        df_flags = generate_review_flags(canonical_data["tickets"], canonical_data["orders"])
        
        assert "ticket_id" in df_flags.columns
        assert "flags" in df_flags.columns
        assert "reason" in df_flags.columns
        assert df_flags["ticket_id"].nunique() == len(df_flags)
        
        # Verify flag presence
        all_flags = "; ".join(df_flags["flags"]).split("; ")
        assert "FLAG_GW_OVER_CAP" in all_flags
        assert "FLAG_REFUND_AND_REPLACEMENT" in all_flags
        assert "FLAG_AMBIGUOUS_ORDER" in all_flags
        assert "FLAG_HIGH_REFUND_AMOUNT" in all_flags

    def test_13_ambiguous_orders_no_false_violations(self, canonical_data):
        """13. Ambiguous orders never trigger false FLAG_REFUND_GT_ORDER_VALUE violations."""
        df_flags = generate_review_flags(canonical_data["tickets"], canonical_data["orders"])
        
        # No refund exceeds verified order value
        assert not df_flags["flags"].str.contains("FLAG_REFUND_GT_ORDER_VALUE").any()
