from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext

from bakerySpotGourmet.core.config import settings
from bakerySpotGourmet.utils.datetime import get_now

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hash for a plain password.
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    """
    if expires_delta:
        expire = get_now() + expires_delta
    else:
        expire = get_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token.
    """
    if expires_delta:
        expire = get_now() + expires_delta
    else:
        expire = get_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode a JWT token. Returns None if invalid.
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token if isinstance(decoded_token, dict) else None
    except JWTError:
        return None


# Rate Limiting

from collections import defaultdict, deque
import time
from typing import Dict, Deque, Tuple
import structlog

from bakerySpotGourmet.core.exceptions import RateLimitExceededException


rate_limit_logger = structlog.get_logger()


class RateLimiter:
    """
    Sliding window rate limiter.
    Tracks requests per identifier (e.g., user ID, IP address) per endpoint.
    """
    
    def __init__(self, requests_per_minute: int = 100, burst: int = 20):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
            burst: Additional burst capacity
        """
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.window_seconds = 60
        # Store: {identifier: deque of timestamps}
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
    
    def _cleanup_old_requests(self, identifier: str, current_time: float) -> None:
        """Remove requests outside the current time window."""
        cutoff_time = current_time - self.window_seconds
        while self._requests[identifier] and self._requests[identifier][0] < cutoff_time:
            self._requests[identifier].popleft()
    
    def check_rate_limit(self, identifier: str, endpoint: str = "default") -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            endpoint: Endpoint identifier for per-endpoint limiting
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, 0
        
        current_time = time.time()
        key = f"{identifier}:{endpoint}"
        
        # Clean up old requests
        self._cleanup_old_requests(key, current_time)
        
        # Check if limit exceeded
        request_count = len(self._requests[key])
        max_requests = self.requests_per_minute + self.burst
        
        if request_count >= max_requests:
            # Calculate retry after time
            oldest_request = self._requests[key][0]
            retry_after = int(self.window_seconds - (current_time - oldest_request)) + 1
            
            rate_limit_logger.warning(
                "rate_limit_exceeded",
                identifier=identifier,
                endpoint=endpoint,
                request_count=request_count,
                max_requests=max_requests,
            )
            
            return False, retry_after
        
        # Record this request
        self._requests[key].append(current_time)
        return True, 0
    
    def reset(self, identifier: str, endpoint: str = "default") -> None:
        """Reset rate limit for an identifier."""
        key = f"{identifier}:{endpoint}"
        if key in self._requests:
            del self._requests[key]


# Global rate limiter instance
_rate_limiter = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    burst=settings.RATE_LIMIT_BURST,
)


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter


def check_rate_limit(identifier: str, endpoint: str = "default") -> None:
    """
    Check rate limit and raise exception if exceeded.
    
    Args:
        identifier: Unique identifier for rate limiting
        endpoint: Endpoint identifier
        
    Raises:
        RateLimitExceededException: If rate limit is exceeded
    """
    limiter = get_rate_limiter()
    is_allowed, retry_after = limiter.check_rate_limit(identifier, endpoint)
    
    if not is_allowed:
        raise RateLimitExceededException(retry_after)
