"""
DateTime utilities.
Standardized datetime operations.
"""

from datetime import datetime
import zoneinfo
from bakerySpotGourmet.core.config import settings

def get_now() -> datetime:
    """
    Get current datetime in the configured timezone (Costa Rica).
    """
    return datetime.now(zoneinfo.ZoneInfo(settings.TIMEZONE))
