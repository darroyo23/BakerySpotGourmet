"""
Order type enumeration.
Defines whether an order is for pick-up or delivery.
"""
from enum import Enum


class OrderType(str, Enum):
    """Types of fulfillment scenarios."""
    PICKUP = "pickup"
    DELIVERY = "delivery"
