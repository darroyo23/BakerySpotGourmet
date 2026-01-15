from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.business_rules.fulfillment import FulfillmentType


@dataclass
class OrderItem:
    """
    OrderItem domain entity.
    """
    product_id: UUID
    quantity: int
    unit_price: float

    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """
    Order Aggregate Root.
    Contains business rules for order lifecycle and state transitions.
    """
    id: UUID
    user_id: UUID
    fulfillment_type: FulfillmentType
    status: OrderStatus = OrderStatus.PENDING
    payment_confirmed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    items: List[OrderItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        """Calculate total amount for the order."""
        return sum(item.subtotal() for item in self.items)

    def add_item(self, product_id: UUID, quantity: int, unit_price: float) -> None:
        """
        Add an item to the order.
        
        Items can only be added while status is PENDING.
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError("Items can only be added when order is in PENDING status")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        self.items.append(item)

    def transition_to(self, new_status: OrderStatus) -> None:
        """
        Transition the order to a new status following strict business rules.
        """
        if new_status == self.status:
            return

        if new_status == OrderStatus.CONFIRMED:
            if self.status != OrderStatus.PENDING:
                raise ValueError("Can only confirm a PENDING order")
            if not self.items:
                raise ValueError("Order must contain at least one item to be confirmed")
        
        elif new_status == OrderStatus.PREPARING:
            if self.status != OrderStatus.CONFIRMED:
                raise ValueError("Can only start preparing from CONFIRMED status")
        
        elif new_status == OrderStatus.READY:
            if self.status != OrderStatus.PREPARING:
                raise ValueError("Only PREPARING orders can be marked as READY")
        
        elif new_status == OrderStatus.ON_THE_WAY:
            if self.status != OrderStatus.PREPARING:
                # Based on rules: preparing -> ready | on_the_way
                raise ValueError("Order must be PREPARING to go ON_THE_WAY")
            if self.fulfillment_type != FulfillmentType.DELIVERY:
                raise ValueError("Only delivery orders can be ON_THE_WAY")
        
        elif new_status == OrderStatus.DELIVERED:
            if self.status not in (OrderStatus.READY, OrderStatus.ON_THE_WAY):
                raise ValueError("Order must be READY or ON_THE_WAY to be DELIVERED")
        
        elif new_status == OrderStatus.CANCELLED:
            if self.status in (OrderStatus.DELIVERED, OrderStatus.ON_THE_WAY):
                 raise ValueError("Cannot cancel a delivered or in-transit order")
        
        else:
            raise ValueError(f"Invalid state transition to {new_status}")

        self.status = new_status
