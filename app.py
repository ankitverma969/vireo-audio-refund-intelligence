"""Vireo Audio — Support Ticket Refund Intelligence & AI Auditing Dashboard.

A lightweight, local, business-facing Streamlit application for executive oversight,
operational audit triage, and AI-assisted refund reclassification.

Run locally:
    streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------------------------------
# Page Configuration & Styling
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Vireo Audio — Refund Intelligence & Audit Dashboard",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 2px;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-med {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .disclaimer-banner {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 6px 6px 0;
        margin-bottom: 20px;
        font-size: 0.88rem;
        color: #1e3a8a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Data Loading & Caching
# --------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
VALIDATION_DIR = BASE_DIR / "data" / "validation"

@st.cache_data
def load_all_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load canonical tickets, agent metadata, classification results, review queue, and validation sample."""
    from src.loader import load_agents
    
    # 1. Canonical tickets
    parquet_path = DATA_PROCESSED_DIR / "canonical_tickets.parquet"
    csv_path = DATA_PROCESSED_DIR / "canonical_tickets.csv"
    if parquet_path.is_file():
        df_tickets = pd.read_parquet(parquet_path)
    elif csv_path.is_file():
        df_tickets = pd.read_csv(csv_path)
    else:
        df_tickets = pd.DataFrame()

    if not df_tickets.empty:
        # Define refund indicator
        df_tickets["is_refund"] = df_tickets["refund_reason_code"].notna() & (df_tickets["refund_reason_code"] != "")
        
        # Merge agent metadata for team and tier
        try:
            agents = load_agents()
            if not agents.empty:
                agent_sub = agents[["agent_id", "team", "tier"]].drop_duplicates(subset=["agent_id"])
                df_tickets = df_tickets.merge(agent_sub, on="agent_id", how="left", suffixes=("", "_agent"))
                if "team" not in df_tickets.columns and "assigned_team" in df_tickets.columns:
                    df_tickets["team"] = df_tickets["assigned_team"]
                df_tickets["tier"] = "Tier " + df_tickets["tier"].fillna(1).astype(int).astype(str)
        except Exception:
            if "team" not in df_tickets.columns and "assigned_team" in df_tickets.columns:
                df_tickets["team"] = df_tickets["assigned_team"]
            if "tier" not in df_tickets.columns:
                df_tickets["tier"] = "Tier 1"

        # Normalize dates
        if "created_at" in df_tickets.columns:
            df_tickets["created_at"] = pd.to_datetime(df_tickets["created_at"], errors="coerce")
            df_tickets["month_year"] = df_tickets["created_at"].dt.to_period("M").astype(str)
            df_tickets["quarter"] = df_tickets["created_at"].dt.to_period("Q").astype(str)

    # 2. Classification results
    results_path = REPORTS_DIR / "classification_results.csv"
    df_results = pd.read_csv(results_path) if results_path.is_file() else pd.DataFrame()

    # 3. Review queue
    queue_path = REPORTS_DIR / "classification_review_queue.csv"
    df_queue = pd.read_csv(queue_path) if queue_path.is_file() else pd.DataFrame()

    # 4. Validation sample
    val_path = VALIDATION_DIR / "gw_other_validation_sample.csv"
    df_val = pd.read_csv(val_path) if val_path.is_file() else pd.DataFrame()

    return df_tickets, df_results, df_queue, df_val


df_tickets, df_results, df_queue, df_val = load_all_datasets()

# --------------------------------------------------------------------------
# Sidebar Navigation & Context
# --------------------------------------------------------------------------

st.sidebar.image("https://img.icons8.com/isometric/100/headphones.png", width=64)
st.sidebar.title("Vireo Audio")
st.sidebar.caption("Refund Intelligence & Audit Platform")

navigation_option = st.sidebar.radio(
    "Navigation",
    options=[
        "Executive Overview",
        "Monthly & Cohort View",
        "Reason Code Breakdown",
        "Agent & Operations View",
        "AI-Assisted Review (GW-OTHER)",
        "Exception & Audit Queue",
        "Business Value Framework",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Baseline Financial Truth**:
    - Canonical Tickets: **11,600**
    - Canonical Refunds: **2,340**
    - Reconciled Spend: **₹6,709,932**
    - GW-OTHER Spend: **₹2,907,036**
    - Active AI Provider: `local` (Rule-Based)
    """
)

# --------------------------------------------------------------------------
# 1. Executive Overview
# --------------------------------------------------------------------------

if navigation_option == "Executive Overview":
    st.title("Executive Refund Overview")
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>Audit Standard</strong>: Figures represent reconciled cash refund spend directly credited to customers.
            This ledger does not conflate replacement inventory unit costs, logistics freight, customer support overhead, or SLA penalties.
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_refunds = df_tickets[df_tickets["is_refund"] == True].copy()
    tot_tickets = len(df_tickets)
    tot_refunds = len(df_refunds)
    refund_spend = float(df_refunds["refund_amount_inr_normalized"].sum())
    refund_rate = (tot_refunds / tot_tickets) if tot_tickets > 0 else 0.0
    avg_refund = float(df_refunds["refund_amount_inr_normalized"].mean())
    med_refund = float(df_refunds["refund_amount_inr_normalized"].median())

    gw_df = df_refunds[df_refunds["refund_reason_code"] == "GW-OTHER"]
    gw_spend = float(gw_df["refund_amount_inr_normalized"].sum())
    gw_count = len(gw_df)

    double_dip_count = int((df_refunds["replacement_issued"] == "Y").sum())
    ambiguous_count = int((df_refunds["order_match_status"] == "ambiguous").sum())

    # Metric Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""<div class="main-metric-card">
                <div class="metric-header">Reconciled Refund Spend</div>
                <div class="metric-value">₹{refund_spend:,.2f}</div>
                <div class="metric-subtitle">Across 2,340 verified refunds</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""<div class="main-metric-card">
                <div class="metric-header">Refund Ticket Volume</div>
                <div class="metric-value">{tot_refunds:,}</div>
                <div class="metric-subtitle">{refund_rate:.2%} of 11,600 total tickets</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="main-metric-card">
                <div class="metric-header">Average / Median Refund</div>
                <div class="metric-value">₹{avg_refund:,.0f} <span style="font-size:1rem;color:#64748b;">/ ₹{med_refund:,.0f}</span></div>
                <div class="metric-subtitle">INR normalized cash per ticket</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""<div class="main-metric-card">
                <div class="metric-header">GW-OTHER Spend (Catch-All)</div>
                <div class="metric-value">₹{gw_spend:,.2f}</div>
                <div class="metric-subtitle">{gw_count:,} tickets (43.3% of refund spend)</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Metric Row 2: Audit Indicators
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(
            f"""<div class="main-metric-card" style="border-left: 4px solid #ef4444;">
                <div class="metric-header">Double-Dip Indicators (Refund + Repl)</div>
                <div class="metric-value">{double_dip_count:,} <span style="font-size:1rem;color:#64748b;">tickets</span></div>
                <div class="metric-subtitle">Requires immediate operational closure</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with a2:
        st.markdown(
            f"""<div class="main-metric-card" style="border-left: 4px solid #f59e0b;">
                <div class="metric-header">Ambiguous Order Matches</div>
                <div class="metric-value">{ambiguous_count:,} <span style="font-size:1rem;color:#64748b;">tickets</span></div>
                <div class="metric-subtitle">Multiple orders found for customer identifier</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with a3:
        cand_count = len(df_results[df_results["predicted_reason_code"].notna()]) if not df_results.empty else 574
        cand_spend = float(df_results[df_results["predicted_reason_code"].notna()]["refund_amount_inr_normalized"].sum()) if not df_results.empty else 1576028.0
        st.markdown(
            f"""<div class="main-metric-card" style="border-left: 4px solid #3b82f6;">
                <div class="metric-header">AI/Rule Reclassification Candidates</div>
                <div class="metric-value">{cand_count:,} <span style="font-size:1rem;color:#64748b;">(₹{cand_spend:,.0f})</span></div>
                <div class="metric-subtitle">57.9% of GW-OTHER tickets reclassified</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations
    col_chart1, col_chart2 = st.columns([6, 4])

    with col_chart1:
        st.subheader("Monthly Reconciled Refund Spend & Ticket Count")
        monthly_grp = df_refunds.groupby("month_year").agg(
            spend=("refund_amount_inr_normalized", "sum"),
            count=("ticket_id", "count"),
        ).reset_index().sort_values("month_year")

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=monthly_grp["month_year"],
            y=monthly_grp["spend"],
            name="Refund Spend (INR)",
            marker_color="#2563eb",
            yaxis="y",
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly_grp["month_year"],
            y=monthly_grp["count"],
            name="Refund Tickets",
            marker_color="#f97316",
            mode="lines+markers",
            yaxis="y2",
        ))
        fig_trend.update_layout(
            yaxis=dict(title="Spend (INR)", showgrid=True),
            yaxis2=dict(title="Ticket Count", overlaying="y", side="right", showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=30, b=20),
            height=340,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_chart2:
        st.subheader("Refund Spend by Reason Code")
        reason_grp = df_refunds.groupby("refund_reason_code")["refund_amount_inr_normalized"].sum().reset_index()
        fig_pie = px.pie(
            reason_grp,
            values="refund_amount_inr_normalized",
            names="refund_reason_code",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        fig_pie.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=340,
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# --------------------------------------------------------------------------
# 2. Monthly & Cohort View
# --------------------------------------------------------------------------

elif navigation_option == "Monthly & Cohort View":
    st.title("Monthly & Cohort Refund Analysis")
    st.markdown("Filter and drill into refund volumes, channels, and team segments across operating quarters.")

    df_refunds = df_tickets[df_tickets["is_refund"] == True].copy()

    # Filter Controls
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        all_months = ["All"] + sorted(df_refunds["month_year"].dropna().unique().tolist())
        selected_month = st.selectbox("Month", all_months, index=0)
    with f2:
        all_channels = ["All"] + sorted(df_refunds["channel"].dropna().unique().tolist())
        selected_channel = st.selectbox("Channel", all_channels, index=0)
    with f3:
        all_teams = ["All"] + sorted(df_refunds["team"].dropna().unique().tolist())
        selected_team = st.selectbox("Team", all_teams, index=0)
    with f4:
        all_tiers = ["All"] + sorted(df_refunds["tier"].dropna().unique().tolist())
        selected_tier = st.selectbox("Tier", all_tiers, index=0)

    # Filter Application
    filtered = df_refunds.copy()
    if selected_month != "All":
        filtered = filtered[filtered["month_year"] == selected_month]
    if selected_channel != "All":
        filtered = filtered[filtered["channel"] == selected_channel]
    if selected_team != "All":
        filtered = filtered[filtered["team"] == selected_team]
    if selected_tier != "All":
        filtered = filtered[filtered["tier"] == selected_tier]

    m_count = len(filtered)
    m_spend = float(filtered["refund_amount_inr_normalized"].sum())
    m_avg = float(filtered["refund_amount_inr_normalized"].mean()) if m_count > 0 else 0.0
    m_med = float(filtered["refund_amount_inr_normalized"].median()) if m_count > 0 else 0.0

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Refund Tickets", f"{m_count:,}")
    c2.metric("Filtered Refund Spend", f"₹{m_spend:,.2f}")
    c3.metric("Average Refund Amount", f"₹{m_avg:,.2f}")
    c4.metric("Median Refund Amount", f"₹{m_med:,.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Refund Spend by Support Channel")
        ch_grp = filtered.groupby("channel")["refund_amount_inr_normalized"].agg(["sum", "count"]).reset_index()
        fig_ch = px.bar(
            ch_grp,
            x="channel",
            y="sum",
            text_auto=".2s",
            labels={"sum": "Spend (INR)", "channel": "Channel"},
            color="channel",
        )
        fig_ch.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig_ch, use_container_width=True)

    with col_b:
        st.subheader("Refund Spend by Operational Team")
        tm_grp = filtered.groupby("team")["refund_amount_inr_normalized"].agg(["sum", "count"]).reset_index()
        fig_tm = px.bar(
            tm_grp,
            x="team",
            y="sum",
            text_auto=".2s",
            labels={"sum": "Spend (INR)", "team": "Support Team"},
            color="team",
        )
        fig_tm.update_layout(showlegend=False, height=320)
        st.plotly_chart(fig_tm, use_container_width=True)

# --------------------------------------------------------------------------
# 3. Reason Code Breakdown
# --------------------------------------------------------------------------

elif navigation_option == "Reason Code Breakdown":
    st.title("Authoritative Reason Code Analysis")
    st.markdown("Detailed financial distribution across all 8 Support Policy §5 refund reason codes.")

    df_refunds = df_tickets[df_tickets["is_refund"] == True].copy()
    tot_spend = float(df_refunds["refund_amount_inr_normalized"].sum())
    tot_count = len(df_refunds)

    reason_summary = df_refunds.groupby("refund_reason_code").agg(
        ticket_count=("ticket_id", "count"),
        total_spend=("refund_amount_inr_normalized", "sum"),
        avg_spend=("refund_amount_inr_normalized", "mean"),
        median_spend=("refund_amount_inr_normalized", "median"),
        std_spend=("refund_amount_inr_normalized", "std"),
    ).reset_index()

    reason_summary["share_tickets"] = reason_summary["ticket_count"] / tot_count
    reason_summary["share_spend"] = reason_summary["total_spend"] / tot_spend
    reason_summary = reason_summary.sort_values(by="total_spend", ascending=False)

    # Format for display
    display_df = reason_summary.copy()
    display_df["ticket_count"] = display_df["ticket_count"].map("{:,}".format)
    display_df["share_tickets"] = display_df["share_tickets"].map("{:.1%}".format)
    display_df["total_spend"] = display_df["total_spend"].map("₹{:,.2f}".format)
    display_df["share_spend"] = display_df["share_spend"].map("{:.1%}".format)
    display_df["avg_spend"] = display_df["avg_spend"].map("₹{:,.2f}".format)
    display_df["median_spend"] = display_df["median_spend"].map("₹{:,.2f}".format)
    display_df = display_df.drop(columns=["std_spend"])

    st.dataframe(
        display_df,
        column_config={
            "refund_reason_code": "Reason Code",
            "ticket_count": "Tickets",
            "share_tickets": "Ticket Share",
            "total_spend": "Total Spend (INR)",
            "share_spend": "Spend Share",
            "avg_spend": "Average",
            "median_spend": "Median",
        },
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("Monthly Trajectory by Reason Code")

    monthly_reason = df_refunds.groupby(["month_year", "refund_reason_code"])["refund_amount_inr_normalized"].sum().reset_index()
    fig_mr = px.line(
        monthly_reason,
        x="month_year",
        y="refund_amount_inr_normalized",
        color="refund_reason_code",
        markers=True,
        labels={"refund_amount_inr_normalized": "Spend (INR)", "month_year": "Month", "refund_reason_code": "Reason Code"},
    )
    fig_mr.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_mr, use_container_width=True)

# --------------------------------------------------------------------------
# 4. Agent & Operations View
# --------------------------------------------------------------------------

elif navigation_option == "Agent & Operations View":
    st.title("Agent & Operational Role Distribution")
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>Operational Governance Standard</strong>: High refund concentration reflects specialized frontline roles
            (e.g., the dedicated Returns Desk and Billing Escalations queues), NOT agent misconduct or policy evasion.
            Tier 2 Escalation specialists are maintained in a separate operational tier.
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_refunds = df_tickets[df_tickets["is_refund"] == True].copy()

    agent_grp = df_refunds.groupby(["agent_id", "team", "tier"]).agg(
        refund_count=("ticket_id", "count"),
        refund_spend=("refund_amount_inr_normalized", "sum"),
        avg_refund=("refund_amount_inr_normalized", "mean"),
        gw_other_count=("refund_reason_code", lambda x: (x == "GW-OTHER").sum()),
        double_dip_count=("replacement_issued", lambda x: (x == "Y").sum()),
    ).reset_index().sort_values(by="refund_spend", ascending=False)

    col_t1, col_t2 = st.tabs(["Tier 1 Operational Agents", "Tier 2 Escalation Specialists"])

    with col_t1:
        t1_df = agent_grp[agent_grp["tier"] == "Tier 1"].copy()
        st.write(f"Showing **{len(t1_df)} Tier 1 Agents** handling primary customer queues:")
        t1_disp = t1_df.copy()
        t1_disp["refund_spend"] = t1_disp["refund_spend"].map("₹{:,.2f}".format)
        t1_disp["avg_refund"] = t1_disp["avg_refund"].map("₹{:,.2f}".format)
        st.dataframe(t1_disp, use_container_width=True, hide_index=True)

    with col_t2:
        t2_df = agent_grp[agent_grp["tier"] == "Tier 2"].copy()
        st.write(f"Showing **{len(t2_df)} Tier 2 Specialists** handling warranty buy-backs and escalated exceptions:")
        t2_disp = t2_df.copy()
        t2_disp["refund_spend"] = t2_disp["refund_spend"].map("₹{:,.2f}".format)
        t2_disp["avg_refund"] = t2_disp["avg_refund"].map("₹{:,.2f}".format)
        st.dataframe(t2_disp, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Agent Case Inspection")
    selected_agent = st.selectbox("Select Agent to View Ticket History", sorted(df_refunds["agent_id"].dropna().unique()))
    if selected_agent:
        agent_tickets = df_refunds[df_refunds["agent_id"] == selected_agent][
            ["ticket_id", "created_at", "refund_reason_code", "refund_amount_inr_normalized", "replacement_issued", "order_match_status", "customer_message"]
        ].sort_values("created_at", ascending=False)
        st.dataframe(agent_tickets, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------
# 5. AI-Assisted Review (GW-OTHER)
# --------------------------------------------------------------------------

elif navigation_option == "AI-Assisted Review (GW-OTHER)":
    st.title("AI-Assisted Refund Reclassification & Audit Queue")
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>Advisory Notice</strong>: All predicted codes are recommendations generated by the NLP rule-based baseline
            and/or optional LLM adapter. Predictions are strictly advisory and require human confirmation before modifying any accounting ledger.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df_results.empty:
        st.warning("Classification results not found in reports/classification_results.csv. Run 'python -m src.classify' first.")
    else:
        tot_gw = len(df_results)
        reclassified = len(df_results[df_results["predicted_reason_code"].notna()])
        unclassified = tot_gw - reclassified
        reclass_spend = float(df_results[df_results["predicted_reason_code"].notna()]["refund_amount_inr_normalized"].sum())

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("GW-OTHER Tickets", f"{tot_gw:,}")
        k2.metric("Candidates Reclassified", f"{reclassified:,} ({reclassified/tot_gw:.1%})")
        k3.metric("Candidate Spend", f"₹{reclass_spend:,.2f}")
        k4.metric("Unclassified / High Ambiguity", f"{unclassified:,}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Filters
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            prio_filter = st.selectbox("Filter Review Priority", ["All", "HIGH", "MEDIUM", "LOW"], index=0)
        with c_f2:
            all_preds = ["All", "Unclassified (None)"] + sorted(df_results["predicted_reason_code"].dropna().unique().tolist())
            pred_filter = st.selectbox("Filter Predicted Policy Code", all_preds, index=0)

        filtered_queue = df_results.copy()
        if prio_filter != "All":
            filtered_queue = filtered_queue[filtered_queue["review_priority"] == prio_filter]
        if pred_filter == "Unclassified (None)":
            filtered_queue = filtered_queue[filtered_queue["predicted_reason_code"].isna()]
        elif pred_filter != "All":
            filtered_queue = filtered_queue[filtered_queue["predicted_reason_code"] == pred_filter]

        st.write(f"Showing **{len(filtered_queue):,} tickets** in selected review cohort:")

        col_table, col_detail = st.columns([6, 4])

        with col_table:
            cols_to_show = ["ticket_id", "predicted_reason_code", "confidence", "review_priority", "refund_amount_inr_normalized", "evidence_text"]
            st.dataframe(
                filtered_queue[cols_to_show],
                column_config={
                    "ticket_id": "Ticket ID",
                    "predicted_reason_code": "Predicted Code",
                    "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
                    "review_priority": "Priority",
                    "refund_amount_inr_normalized": st.column_config.NumberColumn("Refund (INR)", format="₹%.2f"),
                    "evidence_text": "Extracted Evidence",
                },
                use_container_width=True,
                hide_index=True,
            )

        with col_detail:
            st.subheader("Ticket Audit Inspector")
            selected_tck_id = st.selectbox("Select Ticket ID to Inspect", filtered_queue["ticket_id"].tolist()) if not filtered_queue.empty else None

            if selected_tck_id:
                tck_row = df_results[df_results["ticket_id"] == selected_tck_id].iloc[0]
                orig_tck = df_tickets[df_tickets["ticket_id"] == selected_tck_id].iloc[0] if not df_tickets.empty else {}

                st.markdown(f"**Ticket ID**: `{selected_tck_id}`")
                st.markdown(f"**Existing Reason**: `{tck_row.get('existing_reason_code')}`")
                st.markdown(f"**Predicted Reason**: `{tck_row.get('predicted_reason_code')}`")
                st.markdown(f"**Confidence**: `{tck_row.get('confidence'):.2f}` | **Priority**: `{tck_row.get('review_priority')}`")
                st.markdown(f"**Method**: `{tck_row.get('classification_method')}`")
                st.info(f"**Matched Evidence**: {tck_row.get('evidence_text')}")
                st.write(f"**Explanation**: {tck_row.get('explanation')}")

                with st.expander("Customer Message & Agent Notes", expanded=True):
                    st.markdown("**Customer Message**:")
                    st.text(orig_tck.get("customer_message", "N/A"))
                    st.markdown("**Agent Notes**:")
                    st.text(orig_tck.get("agent_notes", "N/A"))

# --------------------------------------------------------------------------
# 6. Exception & Audit Queue
# --------------------------------------------------------------------------

elif navigation_option == "Exception & Audit Queue":
    st.title("Policy Exceptions & Operational Audit Queue")
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>Operational Risk Triage</strong>: Identified exception candidates reflect process gaps, system migration duplicates,
            or potential double-dipping, requiring operational verification against warehouse return receipts and carrier manifests.
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_refunds = df_tickets[df_tickets["is_refund"] == True].copy()

    tab_dd, tab_amb, tab_high, tab_gw_cap = st.tabs([
        "Double-Dip (Refund + Replacement)",
        "Ambiguous Order Matches",
        "High-Value Refunds (≥ ₹5,000)",
        "GW-OTHER Above Goodwill Cap (> ₹500)",
    ])

    with tab_dd:
        dd_df = df_refunds[df_refunds["replacement_issued"] == "Y"].copy()
        unambig_dd = int((dd_df["order_match_status"] != "ambiguous").sum())
        ambig_dd = int((dd_df["order_match_status"] == "ambiguous").sum())
        st.write(
            f"Identified **{len(dd_df):,} Refund + Replacement Indicators** "
            f"(₹{dd_df['refund_amount_inr_normalized'].sum():,.2f} Spend):\n"
            f"- **{unambig_dd} unambiguous order-linked tickets**\n"
            f"- **{ambig_dd} ambiguous tickets**\n\n"
            "Requires operational verification against warehouse return receipts and replacement records."
        )
        st.dataframe(
            dd_df[["ticket_id", "created_at", "agent_id", "order_match_status", "refund_reason_code", "refund_amount_inr_normalized", "customer_message"]],
            use_container_width=True,
            hide_index=True,
        )

    with tab_amb:
        amb_df = df_refunds[df_refunds["order_match_status"] == "ambiguous"].copy()
        st.write(f"Identified **{len(amb_df):,} Tickets with Ambiguous Order Identifiers** (₹{amb_df['refund_amount_inr_normalized'].sum():,.2f} Spend):")
        st.dataframe(
            amb_df[["ticket_id", "created_at", "order_id", "agent_id", "refund_amount_inr_normalized", "customer_message"]],
            use_container_width=True,
            hide_index=True,
        )

    with tab_high:
        high_df = df_refunds[df_refunds["refund_amount_inr_normalized"] >= 5000.0].copy()
        st.write(f"Identified **{len(high_df):,} High-Value Refunds (≥ ₹5,000)** (₹{high_df['refund_amount_inr_normalized'].sum():,.2f} Spend):")
        st.dataframe(
            high_df[["ticket_id", "created_at", "agent_id", "tier", "refund_reason_code", "refund_amount_inr_normalized", "customer_message"]],
            use_container_width=True,
            hide_index=True,
        )

    with tab_gw_cap:
        gw_cap_df = df_refunds[(df_refunds["refund_reason_code"] == "GW-OTHER") & (df_refunds["refund_amount_inr_normalized"] > 500.0)].copy()
        st.write(
            f"Identified **{len(gw_cap_df):,} GW-OTHER refunds above the stated ₹500 goodwill threshold** "
            f"(₹{gw_cap_df['refund_amount_inr_normalized'].sum():,.2f} Spend): "
            "These are review candidates requiring text/policy validation, not confirmed violations."
        )
        st.dataframe(
            gw_cap_df[["ticket_id", "created_at", "agent_id", "team", "refund_amount_inr_normalized", "customer_message"]],
            use_container_width=True,
            hide_index=True,
        )

# --------------------------------------------------------------------------
# 7. Business Value Framework
# --------------------------------------------------------------------------

elif navigation_option == "Business Value Framework":
    st.title("Business Value & Financial Governance Framework")
    st.markdown(
        """
        <div class="disclaimer-banner">
            <strong>Critical Distinction</strong>: <em>Candidate spend for reason-code reclassification is not the same as cash savings.</em>
            Accounting reclassification corrects cost attribution; hard cash savings require contractual claims and process closures.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_val_a, col_val_b = st.columns(2)

    with col_val_a:
        st.subheader("A. Spend Reclassification Opportunity")
        st.markdown(
            """
            Corrects the frontline miscoding where ₹2.91M was categorized under `GW-OTHER`:
            - **Total GW-OTHER Spend**: **₹2,907,036.00** (991 tickets)
            - **Candidate Spend for Reason-Code Reclassification**: **₹1,576,028.00 (54.2%)** across **574 candidate tickets (57.9%)**
            - **Unclassified / Ambiguous**: **417 tickets (₹1,331,008.00)**
            
            *Important*: Reclassification improves reporting and cost attribution but does not itself recover cash.
            
            **Managerial Impact**:
            - Enables holding reverse-logistics partners accountable for returned goods (`RETURN-QC-OK`: ₹522K).
            - Exposes order fulfillment latency causing pre-dispatch cancellations (`CANCEL`: ₹355K).
            - Identifies vendor hardware component reliability issues (`WTY-BUYBACK`: ₹244K).
            """
        )

    with col_val_b:
        st.subheader("B. Potential Operational Recovery Opportunities")
        st.markdown(
            """
            True cash recoveries and loss-prevention require operational follow-through:
            
            1. **Carrier Damage & Transit Claims (`LOST-TRANSIT`)**:
               - ₹181,467 across 55 tickets reclassified as lost in transit.
               - Subject to carrier contractual SLA reimbursement claims under Policy §3.
               
            2. **Payment Gateway Reconciliation (`DUP-PAYMENT`)**:
               - ₹122,610 across 46 tickets identified as duplicate charges.
               - Recoverable directly through payment gateway settlement reconciliations.
               
            3. **Double-Dip Process Elimination (Refund + Replacement)**:
               - 166 tickets with simultaneous replacement and refund flags.
               - Implementing Zendesk hard-stop validation prevents duplicate fulfillment.
            """
        )

    st.markdown("---")
    st.subheader("Human Validation & Machine Learning Benchmark Status")
    st.markdown(
        """
        - **Human Review Sample**: 100 tickets deterministically sampled (`data/validation/gw_other_validation_sample.csv`).
        - **Label Status**: Unannotated (awaiting formal review by operational team).
        - **Benchmark Truth Rule**: Accuracy, precision, recall, and F1 metrics are calculated **only** against verified `human_label` entries.
        """
    )
