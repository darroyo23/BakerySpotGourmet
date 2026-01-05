"""
Payment service layer.
Handles financial transactions and lifecycle.
"""
import structlog
from typing import List, Optional
from bakerySpotGourmet.domain.payments.payment import Payment
from bakerySpotGourmet.domain.payments.status import PaymentStatus
from bakerySpotGourmet.repositories.payment_repository import PaymentRepository
from bakerySpotGourmet.core.exceptions import EntityNotFoundException


logger = structlog.get_logger()


class PaymentService:
    """Service for payment operations."""
    
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def create_payment(self, order_id: int, amount: float, method: str) -> Payment:
        """
        Create a new payment for an order.
        """
        payment = Payment(order_id=order_id, amount=amount, payment_method=method)
        saved_payment = self.payment_repository.save(payment)
        
        logger.info(
            "payment_created",
            payment_id=saved_payment.id,
            order_id=order_id,
            amount=amount,
            status=saved_payment.status.value
        )
        return saved_payment

    def complete_payment(self, payment_id: int) -> Payment:
        """
        Mark a payment as completed.
        """
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise EntityNotFoundException("Payment", str(payment_id))
        
        payment.complete()
        updated_payment = self.payment_repository.save(payment)
        
        logger.info(
            "payment_completed",
            payment_id=payment_id,
            order_id=payment.order_id
        )
        return updated_payment

    def fail_payment(self, payment_id: int) -> Payment:
        """
        Mark a payment as failed.
        """
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise EntityNotFoundException("Payment", str(payment_id))
        
        payment.fail()
        updated_payment = self.payment_repository.save(payment)
        
        logger.info(
            "payment_failed",
            payment_id=payment_id,
            order_id=payment.order_id
        )
        return updated_payment

    def get_payments_for_order(self, order_id: int) -> List[Payment]:
        """
        List all payments for a given order.
        """
        return self.payment_repository.get_by_order_id(order_id)
