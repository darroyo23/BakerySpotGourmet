"""
Payment Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from bakerySpotGourmet.domain.payments.status import PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema."""
    order_id: int
    amount: float
    payment_method: str


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    pass


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: int
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
