"""
Core constants for BakerySpotGourmet.
Defines enums, roles, limits, and standard values.
"""
from enum import Enum


class Role(str, Enum):
    """User roles."""
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"


class OrderStatus(str, Enum):
    """Order status values."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# HTTP Headers
REQUEST_ID_HEADER = "X-Request-ID"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

# Rate Limiting Defaults
DEFAULT_RATE_LIMIT_PER_MINUTE = 100
DEFAULT_RATE_LIMIT_BURST = 20

# Idempotency
IDEMPOTENCY_TTL_SECONDS = 86400  # 24 hours

# Timeouts (in seconds)
DEFAULT_HTTP_TIMEOUT = 30
DEFAULT_DB_TIMEOUT = 10
DEFAULT_EXTERNAL_SERVICE_TIMEOUT = 15

# Circuit Breaker Defaults
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT_SECONDS = 60
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 30
