from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from bakerySpotGourmet.domain.orders.status import OrderStatus

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
        return self.quantity * self.unit_price

@dataclass
class Order:
    """
    Order Aggregate Root.
    """
    customer_id: int
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None
    
    @property
    def total_amount(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    def add_item(self, product_id: int, product_name: str, price: float, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        item = OrderItem(
            product_id=product_id,
            product_name=product_name,
            unit_price=price,
            quantity=quantity
        )
        self.items.append(item)
