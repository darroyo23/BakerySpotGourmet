"""
Integration tests for retry policy.
"""
import pytest
from bakerySpotGourmet.infrastructure.payments.retry_policy import RetryPolicy


def test_retry_policy_success_first_try():
    """Test successful execution on first try."""
    policy = RetryPolicy(max_retries=3)
    
    def successful_func():
        return "success"
    
    result = policy.execute(successful_func)
    assert result == "success"


def test_retry_policy_success_after_retries():
    """Test successful execution after some retries."""
    policy = RetryPolicy(max_retries=3, base_delay=0.1)
    
    call_count = [0]
    
    def sometimes_failing_func():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("Temporary failure")
        return "success"
    
    result = policy.execute(sometimes_failing_func)
    assert result == "success"
    assert call_count[0] == 3


def test_retry_policy_exhausts_retries():
    """Test that all retries are exhausted before giving up."""
    policy = RetryPolicy(max_retries=2, base_delay=0.1)
    
    call_count = [0]
    
    def always_failing_func():
        call_count[0] += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError):
        policy.execute(always_failing_func)
    
    # Should have tried: initial + 2 retries = 3 times
    assert call_count[0] == 3


def test_retry_policy_exponential_backoff():
    """Test exponential backoff calculation."""
    policy = RetryPolicy(max_retries=3, base_delay=1.0, backoff_multiplier=2.0)
    
    # Test delay calculation
    assert policy._calculate_delay(0) == 1.0  # 1.0 * 2^0
    assert policy._calculate_delay(1) == 2.0  # 1.0 * 2^1
    assert policy._calculate_delay(2) == 4.0  # 1.0 * 2^2


def test_retry_policy_max_delay():
    """Test that delay is capped at max_delay."""
    policy = RetryPolicy(max_retries=5, base_delay=10.0, max_delay=20.0, backoff_multiplier=2.0)
    
    # Even with high multiplier, should not exceed max_delay
    assert policy._calculate_delay(10) <= 20.0


def test_retry_policy_retryable_exceptions():
    """Test that only retryable exceptions are retried."""
    policy = RetryPolicy(
        max_retries=2,
        base_delay=0.1,
        retryable_exceptions=(ValueError,)
    )
    
    # ValueError should be retried
    call_count = [0]
    
    def value_error_func():
        call_count[0] += 1
        raise ValueError("Retryable")
    
    with pytest.raises(ValueError):
        policy.execute(value_error_func)
    
    assert call_count[0] == 3  # Initial + 2 retries
    
    # TypeError should not be retried
    call_count[0] = 0
    
    def type_error_func():
        call_count[0] += 1
        raise TypeError("Not retryable")
    
    with pytest.raises(TypeError):
        policy.execute(type_error_func)
    
    assert call_count[0] == 1  # Only initial attempt, no retries
