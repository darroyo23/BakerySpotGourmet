"""
DateTime utilities.
Standardized datetime operations.
"""

from datetime import datetime, timezone

def utc_now() -> datetime:
    """
    Get current UTC datetime.
    """
    return datetime.now(timezone.utc)
