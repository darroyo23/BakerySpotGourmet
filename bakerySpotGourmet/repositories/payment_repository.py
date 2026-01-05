"""
Payment repository for persistence operations.
"""
from typing import Dict, Optional, List
from bakerySpotGourmet.domain.payments.payment import Payment
from bakerySpotGourmet.domain.payments.status import PaymentStatus


class PaymentRepository:
    """In-memory payment repository."""
    
    def __init__(self):
        self._payments: Dict[int, Payment] = {}
        self._counter = 1

    def save(self, payment: Payment) -> Payment:
        """
        Save a new payment or update existing.
        """
        if payment.id is None:
            payment.id = self._counter
            self._counter += 1
        self._payments[payment.id] = payment
        return payment

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Retrieve a payment by ID.
        """
        return self._payments.get(payment_id)
    
    def get_by_order_id(self, order_id: int) -> List[Payment]:
        """
        Retrieve all payments associated with an order.
        """
        return [p for p in self._payments.values() if p.order_id == order_id]
