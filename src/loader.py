"""Data loader and schema validation module for Vireo Audio.

Loads raw CSV datasets, validates expected schemas and columns, parses
types appropriately, and preserves raw values while exposing normalization helpers.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from src.config import (
    AGENTS_FILE,
    CUSTOMERS_FILE,
    LEGACY_CURRENCY_DIVISOR,
    ORDERS_FILE,
    PRODUCTS_FILE,
    TICKETS_FILE,
)

# Expected schemas for all datasets
EXPECTED_SCHEMAS: Dict[str, List[str]] = {
    "agents": [
        "agent_id", "name", "site", "team", "shift", "tier", "from_date", "to_date"
    ],
    "customers": [
        "customer_id", "name", "city", "state", "signup_date", "care_plus"
    ],
    "orders": [
        "order_id", "customer_id", "sku", "order_date", "channel",
        "qty", "order_value_inr", "lot_code"
    ],
    "products": [
        "sku", "product_name", "family", "launch_date",
        "unit_cost_inr", "retail_price_inr", "warranty_months"
    ],
    "tickets": [
        "ticket_id", "created_at", "first_response_at", "resolved_at", "status",
        "channel", "customer_id", "order_id", "product_sku", "category",
        "priority", "assigned_team", "agent_id", "transfers", "csat_score",
        "refund_amount_inr", "refund_reason_code", "replacement_issued",
        "customer_message", "agent_notes", "source_system"
    ]
}


def validate_columns(df: pd.DataFrame, dataset_name: str) -> None:
    """Validate that required columns are present in DataFrame."""
    expected = EXPECTED_SCHEMAS.get(dataset_name)
    if not expected:
        raise ValueError(f"Unknown dataset name: {dataset_name}")
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"Schema validation failed for {dataset_name}. Missing columns: {missing}"
        )


def load_agents(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load agents roster and validate schema."""
    path = file_path or AGENTS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Agents file not found: {path}")
    df = pd.read_csv(path)
    validate_columns(df, "agents")
    return df


def load_customers(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load customers dataset and validate schema."""
    path = file_path or CUSTOMERS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Customers file not found: {path}")
    df = pd.read_csv(path)
    validate_columns(df, "customers")
    return df


def load_orders(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load orders dataset and validate schema."""
    path = file_path or ORDERS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Orders file not found: {path}")
    df = pd.read_csv(path)
    validate_columns(df, "orders")
    return df


def load_products(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load products catalog and validate schema."""
    path = file_path or PRODUCTS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Products file not found: {path}")
    df = pd.read_csv(path)
    validate_columns(df, "products")
    return df


def load_tickets(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Load tickets dataset and validate schema.
    
    Preserves raw refund values in refund_amount_inr without modification.
    """
    path = file_path or TICKETS_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Tickets file not found: {path}")
    df = pd.read_csv(path)
    validate_columns(df, "tickets")
    return df


def normalize_refund_value(raw_amount: Optional[float], source_system: str) -> Optional[float]:
    """Calculate normalized refund value in INR Rupees.
    
    Legacy Freshdesk records store values in Paise (native unit),
    which must be divided by 100 to yield INR Rupees.
    Helpdesk records are already denominated in INR Rupees.
    """
    if pd.isna(raw_amount):
        return None
    if source_system == "legacy_fd":
        return raw_amount / LEGACY_CURRENCY_DIVISOR
    return float(raw_amount)


def add_normalized_refund_column(df_tickets: pd.DataFrame) -> pd.DataFrame:
    """Add a separate normalized refund column while preserving raw values."""
    df = df_tickets.copy()
    df["refund_amount_norm_inr"] = df.apply(
        lambda row: normalize_refund_value(row["refund_amount_inr"], row["source_system"]),
        axis=1
    )
    return df
