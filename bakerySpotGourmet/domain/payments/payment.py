"""
Payment domain entity.
Represents the financial aspect of an order.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from bakerySpotGourmet.domain.payments.status import PaymentStatus


@dataclass
class Payment:
    """
    Payment Entity.
    Tracks the financial lifecycle independently of the order's operational state.
    """
    order_id: int
    amount: float
    payment_method: str
    status: PaymentStatus = field(default=PaymentStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = field(default=None)

    def complete(self) -> None:
        """Mark the payment as completed."""
        self.status = PaymentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def fail(self) -> None:
        """Mark the payment as failed."""
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.utcnow()

    def refund(self) -> None:
        """Mark the payment as refunded."""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")
        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.utcnow()
