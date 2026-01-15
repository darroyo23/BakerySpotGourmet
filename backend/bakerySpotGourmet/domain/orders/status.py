"""
Order status enumeration.
Defines the lifecycle states of an order in the backoffice workflow.
"""
from enum import Enum


class OrderStatus(str, Enum):
    """Order status values for operational workflow."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
