"""
Tests for idempotency functionality.
"""
import pytest
from fastapi import HTTPException
from bakerySpotGourmet.utils.idempotency import (
    IdempotencyStore,
    validate_idempotency_key,
    compute_request_hash,
)


def test_idempotency_store_set_and_get():
    """Test basic set and get operations."""
    store = IdempotencyStore(ttl_seconds=60)
    
    test_data = {"order_id": 123, "status": "created"}
    store.set("key1", test_data)
    
    retrieved = store.get("key1")
    assert retrieved == test_data


def test_idempotency_store_get_nonexistent():
    """Test getting non-existent key returns None."""
    store = IdempotencyStore(ttl_seconds=60)
    
    result = store.get("nonexistent")
    assert result is None


def test_idempotency_store_exists():
    """Test exists method."""
    store = IdempotencyStore(ttl_seconds=60)
    
    assert store.exists("key1") is False
    
    store.set("key1", {"data": "value"})
    assert store.exists("key1") is True


def test_idempotency_store_ttl_expiration():
    """Test that entries expire after TTL."""
    import time
    
    store = IdempotencyStore(ttl_seconds=1)  # 1 second TTL
    
    store.set("key1", {"data": "value"})
    assert store.exists("key1") is True
    
    # Wait for expiration
    time.sleep(1.1)
    
    assert store.exists("key1") is False


def test_idempotency_store_cleanup():
    """Test that expired entries are cleaned up."""
    import time
    
    store = IdempotencyStore(ttl_seconds=1)
    
    # Add multiple entries
    store.set("key1", {"data": "value1"})
    store.set("key2", {"data": "value2"})
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Add new entry (triggers cleanup)
    store.set("key3", {"data": "value3"})
    
    # Old entries should be gone
    assert store.get("key1") is None
    assert store.get("key2") is None
    # New entry should exist
    assert store.get("key3") is not None


def test_validate_idempotency_key_valid():
    """Test validation of valid idempotency keys."""
    # Should not raise exception
    validate_idempotency_key("valid-key-123")
    validate_idempotency_key("a" * 255)  # Max length


def test_validate_idempotency_key_empty():
    """Test validation rejects empty keys."""
    with pytest.raises(HTTPException) as exc_info:
        validate_idempotency_key("")
    
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail


def test_validate_idempotency_key_too_long():
    """Test validation rejects keys that are too long."""
    with pytest.raises(HTTPException) as exc_info:
        validate_idempotency_key("a" * 256)  # Over max length
    
    assert exc_info.value.status_code == 400
    assert "between 1 and 255" in exc_info.value.detail


def test_compute_request_hash():
    """Test request hash computation."""
    body1 = b'{"order": "test"}'
    body2 = b'{"order": "test"}'
    body3 = b'{"order": "different"}'
    
    hash1 = compute_request_hash(body1)
    hash2 = compute_request_hash(body2)
    hash3 = compute_request_hash(body3)
    
    # Same body should produce same hash
    assert hash1 == hash2
    
    # Different body should produce different hash
    assert hash1 != hash3
    
    # Hash should be hex string
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA256 produces 64 character hex string


def test_idempotency_store_multiple_keys():
    """Test storing multiple different keys."""
    store = IdempotencyStore(ttl_seconds=60)
    
    store.set("key1", {"order_id": 1})
    store.set("key2", {"order_id": 2})
    store.set("key3", {"order_id": 3})
    
    assert store.get("key1")["order_id"] == 1
    assert store.get("key2")["order_id"] == 2
    assert store.get("key3")["order_id"] == 3
