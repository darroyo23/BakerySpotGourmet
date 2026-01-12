"""
Idempotency handling for API endpoints.
Ensures POST requests with the same idempotency key return the same response.
"""
import hashlib
import json
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

import structlog
from fastapi import Header, HTTPException, Request, status

from bakerySpotGourmet.core.config import settings
from bakerySpotGourmet.core.constants import IDEMPOTENCY_KEY_HEADER


logger = structlog.get_logger()


class IdempotencyStore:
    """
    In-memory idempotency store with TTL support.
    For production multi-instance deployments, replace with Redis or database.
    """
    
    def __init__(self, ttl_seconds: int = 86400):
        """
        Initialize the idempotency store.
        
        Args:
            ttl_seconds: Time-to-live for stored entries in seconds
        """
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored response by idempotency key.
        
        Args:
            key: The idempotency key
            
        Returns:
            Stored response data or None if not found or expired
        """
        if key not in self._store:
            return None
        
        entry = self._store[key]
        
        # Check if expired
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        
        return entry["response"]
    
    def set(self, key: str, response: Dict[str, Any]) -> None:
        """
        Store a response with the given idempotency key.
        
        Args:
            key: The idempotency key
            response: The response data to store
        """
        self._store[key] = {
            "response": response,
            "expires_at": time.time() + self._ttl_seconds,
            "created_at": time.time(),
        }
        
        # Cleanup expired entries (simple approach)
        self._cleanup_expired()
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from the store."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._store.items()
            if current_time > entry["expires_at"]
        ]
        for key in expired_keys:
            del self._store[key]
    
    def exists(self, key: str) -> bool:
        """
        Check if an idempotency key exists and is not expired.
        
        Args:
            key: The idempotency key
            
        Returns:
            True if key exists and is valid, False otherwise
        """
        return self.get(key) is not None


# Global idempotency store instance
_idempotency_store = IdempotencyStore(ttl_seconds=settings.IDEMPOTENCY_TTL_SECONDS)


def get_idempotency_store() -> IdempotencyStore:
    """
    Get the global idempotency store instance.
    
    Returns:
        The idempotency store
    """
    return _idempotency_store


def validate_idempotency_key(key: str) -> None:
    """
    Validate an idempotency key format.
    
    Args:
        key: The idempotency key to validate
        
    Raises:
        HTTPException: If the key is invalid
    """
    if not key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency key cannot be empty"
        )
    
    if len(key) < 1 or len(key) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency key must be between 1 and 255 characters"
        )


def compute_request_hash(request_body: bytes) -> str:
    """
    Compute a hash of the request body for idempotency verification.
    
    Args:
        request_body: The raw request body
        
    Returns:
        SHA256 hash of the request body
    """
    return hashlib.sha256(request_body).hexdigest()


async def get_idempotency_key(
    idempotency_key: Optional[str] = Header(None, alias=IDEMPOTENCY_KEY_HEADER)
) -> Optional[str]:
    """
    Dependency to extract and validate idempotency key from headers.
    
    Args:
        idempotency_key: The idempotency key from request header
        
    Returns:
        The validated idempotency key or None
    """
    if idempotency_key:
        validate_idempotency_key(idempotency_key)
    return idempotency_key


async def require_idempotency_key(
    idempotency_key: Optional[str] = Header(None, alias=IDEMPOTENCY_KEY_HEADER)
) -> str:
    """
    Dependency that requires an idempotency key to be present.
    
    Args:
        idempotency_key: The idempotency key from request header
        
    Returns:
        The validated idempotency key
        
    Raises:
        HTTPException: If idempotency key is missing or invalid
    """
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{IDEMPOTENCY_KEY_HEADER} header is required for this endpoint"
        )
    
    validate_idempotency_key(idempotency_key)
    return idempotency_key
