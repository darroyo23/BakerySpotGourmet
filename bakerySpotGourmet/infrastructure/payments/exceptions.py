"""
Payment infrastructure exceptions.
"""


class PaymentGatewayException(Exception):
    """Raised when payment gateway encounters an error."""
    pass


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is open and requests are being rejected."""
    def __init__(self, message: str = "Circuit breaker is open"):
        super().__init__(message)
