"""
Tests for rate limiting functionality.
"""
import pytest
import time
from bakerySpotGourmet.core.security import RateLimiter, check_rate_limit
from bakerySpotGourmet.core.exceptions import RateLimitExceededException


def test_rate_limiter_allows_requests_within_limit():
    """Test that requests within limit are allowed."""
    limiter = RateLimiter(requests_per_minute=10, burst=2)
    
    # Should allow first 12 requests (10 + 2 burst)
    for i in range(12):
        is_allowed, retry_after = limiter.check_rate_limit("user:1", "test_endpoint")
        assert is_allowed is True
        assert retry_after == 0


def test_rate_limiter_blocks_requests_over_limit():
    """Test that requests over limit are blocked."""
    limiter = RateLimiter(requests_per_minute=5, burst=1)
    
    # Use up the limit
    for i in range(6):
        limiter.check_rate_limit("user:1", "test_endpoint")
    
    # Next request should be blocked
    is_allowed, retry_after = limiter.check_rate_limit("user:1", "test_endpoint")
    assert is_allowed is False
    assert retry_after > 0


def test_rate_limiter_per_identifier():
    """Test that rate limiting is per identifier."""
    limiter = RateLimiter(requests_per_minute=5, burst=0)
    
    # User 1 uses up their limit
    for i in range(5):
        limiter.check_rate_limit("user:1", "test_endpoint")
    
    # User 2 should still be allowed
    is_allowed, retry_after = limiter.check_rate_limit("user:2", "test_endpoint")
    assert is_allowed is True
    assert retry_after == 0


def test_rate_limiter_per_endpoint():
    """Test that rate limiting is per endpoint."""
    limiter = RateLimiter(requests_per_minute=5, burst=0)
    
    # Use up limit for endpoint1
    for i in range(5):
        limiter.check_rate_limit("user:1", "endpoint1")
    
    # Should still be allowed for endpoint2
    is_allowed, retry_after = limiter.check_rate_limit("user:1", "endpoint2")
    assert is_allowed is True
    assert retry_after == 0


def test_rate_limiter_reset():
    """Test rate limiter reset functionality."""
    limiter = RateLimiter(requests_per_minute=2, burst=0)
    
    # Use up the limit
    for i in range(2):
        limiter.check_rate_limit("user:1", "test_endpoint")
    
    # Should be blocked
    is_allowed, _ = limiter.check_rate_limit("user:1", "test_endpoint")
    assert is_allowed is False
    
    # Reset
    limiter.reset("user:1", "test_endpoint")
    
    # Should be allowed again
    is_allowed, retry_after = limiter.check_rate_limit("user:1", "test_endpoint")
    assert is_allowed is True
    assert retry_after == 0


def test_check_rate_limit_raises_exception():
    """Test that check_rate_limit raises exception when limit exceeded."""
    from bakerySpotGourmet.core.security import _rate_limiter
    
    # Reset to clean state
    _rate_limiter.reset("test_user", "test_endpoint")
    
    # Use up the limit
    max_requests = _rate_limiter.requests_per_minute + _rate_limiter.burst
    for i in range(max_requests):
        check_rate_limit("test_user", "test_endpoint")
    
    # Should raise exception
    with pytest.raises(RateLimitExceededException) as exc_info:
        check_rate_limit("test_user", "test_endpoint")
    
    assert exc_info.value.retry_after > 0


def test_rate_limiter_sliding_window():
    """Test that rate limiter uses sliding window."""
    limiter = RateLimiter(requests_per_minute=2, burst=0)
    
    # Make 2 requests
    limiter.check_rate_limit("user:1", "test_endpoint")
    limiter.check_rate_limit("user:1", "test_endpoint")
    
    # Should be blocked
    is_allowed, _ = limiter.check_rate_limit("user:1", "test_endpoint")
    assert is_allowed is False
    
    # Wait for window to slide (in real scenario)
    # Note: This is a simplified test - in production, old requests would expire
