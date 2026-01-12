"""
Order domain entity.
Contains business rules for order lifecycle and state transitions.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Set

from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.order_type import OrderType
from bakerySpotGourmet.domain.payments.status import PaymentStatus
from bakerySpotGourmet.domain.orders.exceptions import InvalidOrderStatusTransitionException


# Valid state transitions map (strictly operational)
VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),  # Terminal state
    OrderStatus.CANCELLED: set(),  # Terminal state
}


@dataclass
class OrderItem:
    """
    OrderItem Value Object / Entity.
    """
    product_id: int
    quantity: int
    unit_price: float
    product_name: str  # Snapshot of product name at time of order

    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.quantity * self.unit_price


@dataclass
class Order:
    """
    Order Aggregate Root.
    Contains business rules for order lifecycle and state transitions.
    """
    customer_id: int
    order_type: OrderType = field(default=OrderType.PICKUP)
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = field(default=OrderStatus.PENDING)
    payment_status: PaymentStatus = field(default=PaymentStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = field(default=None)
    
    @property
    def total_amount(self) -> float:
        """Calculate total amount for the order."""
        return sum(item.subtotal for item in self.items)
    
    def add_item(self, product_id: int, product_name: str, price: float, quantity: int) -> None:
        """
        Add an item to the order.
        
        Args:
            product_id: ID of the product
            product_name: Name of the product (snapshot)
            price: Unit price
            quantity: Quantity ordered
            
        Raises:
            ValueError: If quantity is not positive
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        item = OrderItem(
            product_id=product_id,
            product_name=product_name,
            unit_price=price,
            quantity=quantity
        )
        self.items.append(item)
    
    def can_transition_to(self, new_status: OrderStatus) -> bool:
        """
        Check if the order can transition to the given status.
        
        Args:
            new_status: The target status
            
        Returns:
            True if transition is valid, False otherwise
        """
        return new_status in VALID_TRANSITIONS.get(self.status, set())
    
    def change_status(self, new_status: OrderStatus) -> None:
        """
        Change the order status with validation.
        
        Args:
            new_status: The new status to transition to
            
        Raises:
            InvalidOrderStatusTransitionException: If transition is not valid
        """
        if not self.can_transition_to(new_status):
            raise InvalidOrderStatusTransitionException(
                current_status=self.status.value,
                new_status=new_status.value
            )
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
