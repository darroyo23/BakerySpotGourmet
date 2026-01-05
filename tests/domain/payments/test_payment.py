"""
Unit tests for Payment domain entity.
"""
import pytest
from bakerySpotGourmet.domain.payments.payment import Payment
from bakerySpotGourmet.domain.payments.status import PaymentStatus


def test_payment_initial_state():
    """Given an order id and amount, payment starts as PENDING."""
    payment = Payment(order_id=1, amount=10.0, payment_method="credit_card")
    assert payment.status == PaymentStatus.PENDING
    assert payment.amount == 10.0
    assert payment.order_id == 1


def test_payment_completion():
    """When a payment is completed, status updates and updated_at changes."""
    payment = Payment(order_id=1, amount=10.0, payment_method="credit_card")
    original_updated_at = payment.updated_at
    
    payment.complete()
    
    assert payment.status == PaymentStatus.COMPLETED
    assert payment.updated_at >= original_updated_at


def test_payment_failure():
    """When a payment fails, status updates."""
    payment = Payment(order_id=1, amount=10.0, payment_method="credit_card")
    payment.fail()
    assert payment.status == PaymentStatus.FAILED


def test_payment_refund_success():
    """A completed payment can be refunded."""
    payment = Payment(order_id=1, amount=10.0, payment_method="credit_card")
    payment.complete()
    payment.refund()
    assert payment.status == PaymentStatus.REFUNDED


def test_payment_refund_fail_if_not_completed():
    """A payment that is not completed cannot be refunded."""
    payment = Payment(order_id=1, amount=10.0, payment_method="credit_card")
    with pytest.raises(ValueError, match="Only completed payments can be refunded"):
        payment.refund()
