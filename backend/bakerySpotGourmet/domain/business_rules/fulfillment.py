from enum import Enum
from dataclasses import dataclass
from datetime import time, date, datetime
from typing import Optional


class FulfillmentType(str, Enum):
    """Enumeration of fulfillment types."""
    PICKUP = "pickup"
    DELIVERY = "delivery"


@dataclass
class BusinessHours:
    """
    BusinessHours domain entity.
    Defines opening and closing times for a specific fulfillment type and day of the week.
    """
    fulfillment_type: FulfillmentType
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    is_active: bool = True

    def is_within_hours(self, current_time: time) -> bool:
        """
        Check if the given time is within the business hours.
        
        Args:
            current_time: The time to check.
            
        Returns:
            True if within hours and active, False otherwise.
        """
        if not self.is_active:
            return False
        
        # Simple comparison for within-day hours
        if self.start_time <= self.end_time:
            return self.start_time <= current_time <= self.end_time
        
        # Handle overnight hours (e.g., 22:00 to 02:00)
        return current_time >= self.start_time or current_time <= self.end_time


@dataclass
class ClosedDay:
    """
    ClosedDay domain entity.
    Defines a specific date when the business is closed.
    """
    day: date
    reason: Optional[str] = None
