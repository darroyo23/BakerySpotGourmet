"""
Circuit breaker implementation for resilient external service calls.
Generic implementation with no domain coupling.
"""
import time
from enum import Enum
from typing import Callable, Any, TypeVar
import structlog

from bakerySpotGourmet.infrastructure.payments.exceptions import CircuitBreakerOpenException


logger = structlog.get_logger()

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Generic circuit breaker for protecting against cascading failures.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are rejected immediately
    - HALF_OPEN: Testing recovery, limited requests allowed
    
    No domain coupling - can be used with any external service.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        recovery_timeout: int = 30,
        name: str = "default",
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before attempting recovery
            recovery_timeout: Time to wait in half-open state
            name: Name for logging purposes
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._last_success_time: float | None = None
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        
        time_since_failure = time.time() - self._last_failure_time
        return time_since_failure >= self.timeout_seconds
    
    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func execution
            
        Raises:
            CircuitBreakerOpenException: If circuit is open
            Exception: Any exception raised by func
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(
                    "circuit_breaker_half_open",
                    name=self.name,
                    failure_count=self._failure_count,
                )
                self._state = CircuitState.HALF_OPEN
            else:
                logger.warning(
                    "circuit_breaker_open",
                    name=self.name,
                    failure_count=self._failure_count,
                )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is open"
                )
        
        try:
            # Execute the function
            result = func(*args, **kwargs)
            
            # Success - reset failure count
            self._on_success()
            return result
            
        except Exception as e:
            # Failure - increment count and potentially open circuit
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self._failure_count = 0
        self._last_success_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            logger.info(
                "circuit_breaker_closed",
                name=self.name,
                message="Circuit recovered",
            )
            self._state = CircuitState.CLOSED
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                logger.error(
                    "circuit_breaker_opened",
                    name=self.name,
                    failure_count=self._failure_count,
                    threshold=self.failure_threshold,
                )
                self._state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        logger.info("circuit_breaker_reset", name=self.name)
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        self._last_success_time = None
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with current state and metrics
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self._last_failure_time,
            "last_success_time": self._last_success_time,
        }
