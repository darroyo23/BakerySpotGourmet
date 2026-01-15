from datetime import time, date
from bakerySpotGourmet.domain.business_rules.fulfillment import FulfillmentType, BusinessHours, ClosedDay

def test_business_hours_within_range():
    hours = BusinessHours(
        fulfillment_type=FulfillmentType.PICKUP,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(18, 0)
    )
    assert hours.is_within_hours(time(10, 0)) is True
    assert hours.is_within_hours(time(8, 0)) is False
    assert hours.is_within_hours(time(18, 0)) is True

def test_business_hours_overnight():
    hours = BusinessHours(
        fulfillment_type=FulfillmentType.DELIVERY,
        day_of_week=5,
        start_time=time(22, 0),
        end_time=time(2, 0)
    )
    assert hours.is_within_hours(time(23, 0)) is True
    assert hours.is_within_hours(time(1, 0)) is True
    assert hours.is_within_hours(time(10, 0)) is False

def test_business_hours_inactive():
    hours = BusinessHours(
        fulfillment_type=FulfillmentType.PICKUP,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(18, 0),
        is_active=False
    )
    assert hours.is_within_hours(time(10, 0)) is False

def test_closed_day():
    closed = ClosedDay(day=date(2026, 1, 1), reason="New Year")
    assert closed.day == date(2026, 1, 1)
    assert closed.reason == "New Year"
