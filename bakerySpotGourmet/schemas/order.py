"""
Order Pydantic schemas.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.order_type import OrderType
from bakerySpotGourmet.domain.payments.status import PaymentStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    order_type: OrderType = OrderType.PICKUP

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    
    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: OrderStatus
    order_type: OrderType
    payment_status: PaymentStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


# Admin schemas

class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus
