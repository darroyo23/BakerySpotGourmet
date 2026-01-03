"""
Order Pydantic schemas.
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict
from bakerySpotGourmet.domain.orders.status import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

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
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
