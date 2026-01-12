"""
Unit tests for order state transitions.
"""
import pytest
from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.exceptions import InvalidOrderStatusTransitionException


def test_order_starts_in_pending_status():
    """Test that new orders start in PENDING status."""
    order = Order(customer_id=1)
    assert order.status == OrderStatus.PENDING


def test_valid_transition_pending_to_confirmed():
    """Test valid transition from PENDING to CONFIRMED."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    assert order.status == OrderStatus.CONFIRMED


def test_valid_transition_confirmed_to_preparing():
    """Test valid transition from CONFIRMED to PREPARING."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    assert order.status == OrderStatus.PREPARING


def test_valid_transition_preparing_to_ready():
    """Test valid transition from PREPARING to READY."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    order.change_status(OrderStatus.READY)
    assert order.status == OrderStatus.READY


def test_valid_transition_ready_to_delivered():
    """Test valid transition from READY to DELIVERED."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    order.change_status(OrderStatus.READY)
    order.change_status(OrderStatus.DELIVERED)
    assert order.status == OrderStatus.DELIVERED


def test_valid_transition_pending_to_cancelled():
    """Test valid transition from PENDING to CANCELLED (Operational)."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CANCELLED)
    assert order.status == OrderStatus.CANCELLED


def test_valid_transition_confirmed_to_cancelled():
    """Test valid transition from CONFIRMED to CANCELLED."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.CANCELLED)
    assert order.status == OrderStatus.CANCELLED


def test_valid_transition_preparing_to_cancelled():
    """Test valid transition from PREPARING to CANCELLED."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    order.change_status(OrderStatus.CANCELLED)
    assert order.status == OrderStatus.CANCELLED


def test_valid_transition_ready_to_cancelled():
    """Test valid transition from READY to CANCELLED."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    order.change_status(OrderStatus.READY)
    order.change_status(OrderStatus.CANCELLED)
    assert order.status == OrderStatus.CANCELLED


def test_invalid_transition_pending_to_preparing():
    """Test invalid transition from PENDING to PREPARING."""
    order = Order(customer_id=1)
    
    with pytest.raises(InvalidOrderStatusTransitionException) as exc_info:
        order.change_status(OrderStatus.PREPARING)
    
    assert "pending" in str(exc_info.value).lower()
    assert "preparing" in str(exc_info.value).lower()


def test_invalid_transition_pending_to_delivered():
    """Test invalid transition from PENDING to DELIVERED."""
    order = Order(customer_id=1)
    
    with pytest.raises(InvalidOrderStatusTransitionException):
        order.change_status(OrderStatus.DELIVERED)


def test_invalid_transition_from_delivered():
    """Test that DELIVERED is a terminal state."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CONFIRMED)
    order.change_status(OrderStatus.PREPARING)
    order.change_status(OrderStatus.READY)
    order.change_status(OrderStatus.DELIVERED)
    
    # Cannot transition from DELIVERED
    with pytest.raises(InvalidOrderStatusTransitionException):
        order.change_status(OrderStatus.PENDING)


def test_invalid_transition_from_cancelled():
    """Test that CANCELLED is a terminal state."""
    order = Order(customer_id=1)
    order.change_status(OrderStatus.CANCELLED)
    
    # Cannot transition from CANCELLED
    with pytest.raises(InvalidOrderStatusTransitionException):
        order.change_status(OrderStatus.CONFIRMED)


def test_can_transition_to_method():
    """Test can_transition_to method."""
    order = Order(customer_id=1)
    
    # From PENDING
    assert order.can_transition_to(OrderStatus.CONFIRMED) is True
    assert order.can_transition_to(OrderStatus.CANCELLED) is True
    assert order.can_transition_to(OrderStatus.PREPARING) is False
    assert order.can_transition_to(OrderStatus.DELIVERED) is False


def test_updated_at_changes_on_status_change():
    """Test that updated_at is updated when status changes."""
    import time
    
    order = Order(customer_id=1)
    original_updated_at = order.updated_at
    
    time.sleep(0.01)  # Small delay to ensure timestamp difference
    order.change_status(OrderStatus.CONFIRMED)
    
    assert order.updated_at > original_updated_at
