"""
Order domain exceptions.
"""


class OrderException(Exception):
    """Base exception for order domain."""
    pass


class InvalidOrderStatusTransitionException(OrderException):
    """Raised when an invalid order status transition is attempted."""
    def __init__(self, current_status: str, new_status: str):
        self.current_status = current_status
        self.new_status = new_status
        message = f"Cannot transition order from {current_status} to {new_status}"
        super().__init__(message)
