"""
Payment domain exceptions.
"""


class PaymentException(Exception):
    """Base exception for payment domain."""
    pass


class InvalidPaymentStatusTransitionException(PaymentException):
    """Raised when an invalid payment status transition is attempted."""
    def __init__(self, current_status: str, new_status: str):
        self.current_status = current_status
        self.new_status = new_status
        message = f"Cannot transition payment from {current_status} to {new_status}"
        super().__init__(message)
