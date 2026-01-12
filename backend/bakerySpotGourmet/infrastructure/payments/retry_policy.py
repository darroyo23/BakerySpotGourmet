"""
Retry policy with exponential backoff for resilient external service calls.
"""
import time
from typing import Callable, Any, TypeVar, Type
import structlog


logger = structlog.get_logger()

T = TypeVar('T')


class RetryPolicy:
    """
    Exponential backoff retry policy.
    Retries failed operations with increasing delays.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_multiplier: Multiplier for exponential backoff
            retryable_exceptions: Tuple of exception types to retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.retryable_exceptions = retryable_exceptions
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        delay = self.base_delay * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)
    
    def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of func execution
            
        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception: Exception | None = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(
                        "retry_succeeded",
                        attempt=attempt,
                        function=func.__name__,
                    )
                
                return result
                
            except self.retryable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    
                    logger.warning(
                        "retry_attempt",
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay_seconds=delay,
                        function=func.__name__,
                        exception=str(e),
                    )
                    
                    time.sleep(delay)
                else:
                    logger.error(
                        "retry_exhausted",
                        attempts=attempt + 1,
                        function=func.__name__,
                        exception=str(e),
                    )
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        # Should never reach here
        raise RuntimeError("Retry logic error")
