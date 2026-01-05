"""
Payment status enumeration.
Defines the financial lifecycle of a payment.
"""
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "pending"      # Payment initiated but not yet finalized
    AUTHORIZED = "authorized" # Payment approved but not yet captured (optional)
    COMPLETED = "completed"   # Payment successfully processed
    FAILED = "failed"         # Payment attempt failed
    REFUNDED = "refunded"     # Payment has been refunded
