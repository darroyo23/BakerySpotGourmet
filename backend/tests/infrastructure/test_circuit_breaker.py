"""
Tests for circuit breaker functionality.
"""
import pytest
from bakerySpotGourmet.infrastructure.payments.circuit_breaker import CircuitBreaker, CircuitState
from bakerySpotGourmet.infrastructure.payments.exceptions import CircuitBreakerOpenException


def test_circuit_breaker_closed_state():
    """Test circuit breaker starts in closed state."""
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
    
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_successful_calls():
    """Test successful calls keep circuit closed."""
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
    
    def successful_func():
        return "success"
    
    for _ in range(5):
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_opens_after_failures():
    """Test circuit opens after threshold failures."""
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test failure")
    
    # Fail 3 times to reach threshold
    for _ in range(3):
        with pytest.raises(ValueError):
            cb.call(failing_func)
    
    # Circuit should now be open
    assert cb.state == CircuitState.OPEN


def test_circuit_breaker_rejects_when_open():
    """Test circuit rejects calls when open."""
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test failure")
    
    # Open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            cb.call(failing_func)
    
    assert cb.state == CircuitState.OPEN
    
    # Should reject with CircuitBreakerOpenException
    with pytest.raises(CircuitBreakerOpenException):
        cb.call(failing_func)


def test_circuit_breaker_half_open_after_timeout():
    """Test circuit transitions to half-open after timeout."""
    import time
    
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
    
    def failing_func():
        raise ValueError("Test failure")
    
    # Open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            cb.call(failing_func)
    
    assert cb.state == CircuitState.OPEN
    
    # Wait for timeout
    time.sleep(1.1)
    
    # Next call should transition to half-open
    # (will still fail, but state changes)
    with pytest.raises(ValueError):
        cb.call(failing_func)
    
    # Note: After failure in half-open, it goes back to open
    # This is expected behavior


def test_circuit_breaker_closes_after_success_in_half_open():
    """Test circuit closes after successful call in half-open state."""
    import time
    
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=1)
    
    call_count = [0]
    
    def sometimes_failing_func():
        call_count[0] += 1
        if call_count[0] <= 2:
            raise ValueError("Test failure")
        return "success"
    
    # Open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            cb.call(sometimes_failing_func)
    
    assert cb.state == CircuitState.OPEN
    
    # Wait for timeout
    time.sleep(1.1)
    
    # Successful call should close circuit
    result = cb.call(sometimes_failing_func)
    assert result == "success"
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_reset():
    """Test manual circuit reset."""
    cb = CircuitBreaker(failure_threshold=2, timeout_seconds=60)
    
    def failing_func():
        raise ValueError("Test failure")
    
    # Open the circuit
    for _ in range(2):
        with pytest.raises(ValueError):
            cb.call(failing_func)
    
    assert cb.state == CircuitState.OPEN
    
    # Reset
    cb.reset()
    
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_get_stats():
    """Test getting circuit breaker statistics."""
    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60, name="test_circuit")
    
    stats = cb.get_stats()
    
    assert stats["name"] == "test_circuit"
    assert stats["state"] == CircuitState.CLOSED.value
    assert stats["failure_count"] == 0
    assert stats["failure_threshold"] == 5


def test_circuit_breaker_with_arguments():
    """Test circuit breaker with function arguments."""
    cb = CircuitBreaker(failure_threshold=3, timeout_seconds=60)
    
    def add(a, b):
        return a + b
    
    result = cb.call(add, 2, 3)
    assert result == 5
    
    result = cb.call(add, a=5, b=7)
    assert result == 12
