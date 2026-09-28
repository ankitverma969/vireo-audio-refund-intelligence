"""Configuration and constants for Vireo Audio Refund Intelligence.

Handles dynamic, platform-independent path resolution and encodes
authoritative business policy constants from support-policy.pdf and README.txt.
"""

from pathlib import Path
from typing import Dict, List, Optional

# Base repository root directory
BASE_DIR: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = BASE_DIR / "data"
DATA_RAW_DIR: Path = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR: Path = BASE_DIR / "data" / "processed"
DATA_VALIDATION_DIR: Path = BASE_DIR / "data" / "validation"
REPORTS_DIR: Path = BASE_DIR / "reports"
DOCS_DIR: Path = BASE_DIR / "docs"

# Canonical processed data file paths
CANONICAL_TICKETS_PARQUET: Path = DATA_PROCESSED_DIR / "canonical_tickets.parquet"
CANONICAL_TICKETS_CSV: Path = DATA_PROCESSED_DIR / "canonical_tickets.csv"
CANONICAL_REFUNDS_CSV: Path = DATA_PROCESSED_DIR / "canonical_refunds.csv"

# Helper function to find a file in data/raw or workspace root
def resolve_file(filename: str, fallback_names: Optional[List[str]] = None) -> Path:
    candidates = [
        DATA_RAW_DIR / filename,
        BASE_DIR / filename,
    ]
    if fallback_names:
        for fb in fallback_names:
            candidates.append(DATA_RAW_DIR / fb)
            candidates.append(BASE_DIR / fb)
            
    for p in candidates:
        if p.is_file():
            return p
            
    # Default to data/raw path if not found
    return DATA_RAW_DIR / filename


# Authoritative file paths
AGENTS_FILE: Path = resolve_file("agents.csv")
CUSTOMERS_FILE: Path = resolve_file("customers.csv")
EMAIL_THREAD_FILE: Path = resolve_file("email-thread.txt")
ORDERS_FILE: Path = resolve_file("orders.csv")
PRODUCTS_FILE: Path = resolve_file("products.csv")
README_FILE: Path = resolve_file("README.txt")
SUPPORT_POLICY_FILE: Path = resolve_file("support-policy.pdf")
TICKETS_FILE: Path = resolve_file("tickets.csv", fallback_names=["tickets.csv.csv"])


# --------------------------------------------------------------------------
# Authoritative Support Policy Constants (support-policy.pdf v3.2)
# --------------------------------------------------------------------------

# Migration date when current helpdesk went live
HELPDESK_GO_LIVE_DATE: str = "2025-09-14"

# Legacy currency conversion factor (Freshdesk native unit: Paise -> INR Rupees)
LEGACY_CURRENCY_DIVISOR: float = 100.0

# First-response SLA targets in minutes
SLA_TARGET_MINUTES: Dict[str, int] = {
    "chat": 15,
    "voice": 120,   # 2 hours
    "social": 240,  # 4 hours
    "email": 480,   # 8 hours
}

# SLA breach compensation credit (credited automatically on breach)
SLA_BREACH_CREDIT_INR: float = 350.0

# Goodwill credit policy cap (per ticket, requires TL approval)
GOODWILL_CREDIT_CAP_INR: float = 500.0

# Planning replacement shipping & pickup cost
REPLACEMENT_SHIPPING_COST_INR: float = 340.0

# Channel contact costs (FY26 planning figures)
CONTACT_COST_INR: Dict[str, float] = {
    "chat": 210.0,
    "email": 260.0,
    "voice": 520.0,
    "social": 240.0,
    "blended": 290.0,
}

# Internal hand-off cost between teams
INTERNAL_TRANSFER_COST_INR: float = 305.0

# Agent hourly fully loaded rate and shift hours
AGENT_HOURLY_COST_INR: float = 165.0
SHIFT_HOURS: int = 8

# Authorized refund reason codes (policy §5)
VALID_REASON_CODES: List[str] = [
    "GW-OTHER",      # Goodwill / Other (dropdown default)
    "DOA-REPL",      # Dead on arrival, refund chosen
    "LOST-TRANSIT",  # Lost or undelivered
    "DUP-PAYMENT",   # Duplicate or failed payment
    "CANCEL",        # Cancellation before dispatch
    "PRICE-ADJ",     # Price or coupon adjustment
    "RETURN-QC-OK",  # Return received and passed QC
    "WTY-BUYBACK",   # Warranty buy-back
]

# Teams with authorized refund processing responsibility
DEFAULT_REFUND_TEAM: str = "Returns Desk"
TIER2_TEAM: str = "Escalations & Warranty"
