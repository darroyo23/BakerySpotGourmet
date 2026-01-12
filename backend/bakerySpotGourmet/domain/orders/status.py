"""
Order status enumeration.
Defines the lifecycle states of an order in the backoffice workflow.
"""
from enum import Enum


class OrderStatus(str, Enum):
    """Order status values for operational workflow."""
    PENDING = "pending"      # Received, waiting for confirmation
    CONFIRMED = "confirmed"  # Accepted by the bakery
    PREPARING = "preparing"  # Being baked/prepared
    READY = "ready"          # Ready for pickup or ready to be dispatched for delivery
    DELIVERED = "delivered"  # Handed to the customer (terminal operational state)
    CANCELLED = "cancelled"  # Operational cancellation
