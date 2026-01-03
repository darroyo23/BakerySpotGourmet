from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    PREPARING = "preparing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
