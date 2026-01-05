"""
Unit tests for admin order service operations.
"""
import pytest
from bakerySpotGourmet.core.exceptions import EntityNotFoundException
from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.orders.exceptions import InvalidOrderStatusTransitionException
from bakerySpotGourmet.repositories.order_repository import OrderRepository
from bakerySpotGourmet.repositories.item_repository import ItemRepository
from bakerySpotGourmet.repositories.payment_repository import PaymentRepository
from bakerySpotGourmet.services.order_service import OrderService


@pytest.fixture
def order_service():
    """Create an order service with repositories."""
    order_repo = OrderRepository()
    payment_repo = PaymentRepository()
    item_repo = ItemRepository()
    return OrderService(order_repo, payment_repo, item_repo)


@pytest.fixture
def sample_order(order_service):
    """Create a sample order for testing."""
    order = Order(customer_id=1)
    order.add_item(product_id=1, product_name="Croissant", price=2.50, quantity=2)
    saved_order = order_service.order_repository.save(order)
    return saved_order


def test_list_orders_empty(order_service):
    """Test listing orders when repository is empty."""
    orders = order_service.list_orders()
    assert orders == []


def test_list_orders_with_data(order_service, sample_order):
    """Test listing orders with data."""
    orders = order_service.list_orders()
    assert len(orders) == 1
    assert orders[0].id == sample_order.id


def test_list_orders_with_pagination(order_service):
    """Test listing orders with pagination."""
    # Create multiple orders
    for i in range(5):
        order = Order(customer_id=i)
        order.add_item(product_id=1, product_name="Item", price=1.0, quantity=1)
        order_service.order_repository.save(order)
    
    # Test skip and limit
    orders = order_service.list_orders(skip=0, limit=2)
    assert len(orders) == 2
    
    orders = order_service.list_orders(skip=2, limit=2)
    assert len(orders) == 2
    
    orders = order_service.list_orders(skip=4, limit=10)
    assert len(orders) == 1


def test_list_orders_with_status_filter(order_service):
    """Test listing orders with status filter."""
    # Create orders with different statuses
    order1 = Order(customer_id=1)
    order1.add_item(product_id=1, product_name="Item", price=1.0, quantity=1)
    order_service.order_repository.save(order1)
    
    order2 = Order(customer_id=2)
    order2.add_item(product_id=1, product_name="Item", price=1.0, quantity=1)
    order2.change_status(OrderStatus.CONFIRMED)
    order_service.order_repository.save(order2)
    
    order3 = Order(customer_id=3)
    order3.add_item(product_id=1, product_name="Item", price=1.0, quantity=1)
    order3.change_status(OrderStatus.CONFIRMED)
    order_service.order_repository.save(order3)
    
    # Filter by PENDING
    pending_orders = order_service.list_orders(status_filter=OrderStatus.PENDING)
    assert len(pending_orders) == 1
    assert pending_orders[0].status == OrderStatus.PENDING
    
    # Filter by CONFIRMED
    confirmed_orders = order_service.list_orders(status_filter=OrderStatus.CONFIRMED)
    assert len(confirmed_orders) == 2
    assert all(o.status == OrderStatus.CONFIRMED for o in confirmed_orders)


def test_get_order_by_id_success(order_service, sample_order):
    """Test retrieving order by ID successfully."""
    order = order_service.get_order_by_id(sample_order.id)
    assert order.id == sample_order.id
    assert order.customer_id == sample_order.customer_id


def test_get_order_by_id_not_found(order_service):
    """Test retrieving non-existent order raises exception."""
    with pytest.raises(EntityNotFoundException) as exc_info:
        order_service.get_order_by_id(999)
    
    assert "Order" in str(exc_info.value)
    assert "999" in str(exc_info.value)


def test_update_order_status_valid_transition(order_service, sample_order):
    """Test updating order status with valid transition."""
    updated_order = order_service.update_order_status(
        order_id=sample_order.id,
        new_status=OrderStatus.CONFIRMED,
        admin_user_id=10
    )
    
    assert updated_order.status == OrderStatus.CONFIRMED
    assert updated_order.id == sample_order.id


def test_update_order_status_invalid_transition(order_service, sample_order):
    """Test updating order status with invalid transition raises exception."""
    with pytest.raises(InvalidOrderStatusTransitionException):
        order_service.update_order_status(
            order_id=sample_order.id,
            new_status=OrderStatus.DELIVERED,  # Cannot go from PENDING to DELIVERED
            admin_user_id=10
        )


def test_update_order_status_order_not_found(order_service):
    """Test updating status of non-existent order."""
    with pytest.raises(EntityNotFoundException):
        order_service.update_order_status(
            order_id=999,
            new_status=OrderStatus.CONFIRMED,
            admin_user_id=10
        )


def test_update_order_status_full_workflow(order_service, sample_order):
    """Test complete order status workflow."""
    # PENDING -> CONFIRMED
    order = order_service.update_order_status(
        sample_order.id, OrderStatus.CONFIRMED, admin_user_id=10
    )
    assert order.status == OrderStatus.CONFIRMED
    
    # CONFIRMED -> PREPARING
    order = order_service.update_order_status(
        sample_order.id, OrderStatus.PREPARING, admin_user_id=10
    )
    assert order.status == OrderStatus.PREPARING
    
    # PREPARING -> READY
    order = order_service.update_order_status(
        sample_order.id, OrderStatus.READY, admin_user_id=10
    )
    assert order.status == OrderStatus.READY
    
    # READY -> DELIVERED
    order = order_service.update_order_status(
        sample_order.id, OrderStatus.DELIVERED, admin_user_id=10
    )
    assert order.status == OrderStatus.DELIVERED


def test_update_order_status_cancellation_workflow(order_service, sample_order):
    """Test order cancellation from different states."""
    # Cancel from PENDING
    order = order_service.update_order_status(
        sample_order.id, OrderStatus.CANCELLED, admin_user_id=10
    )
    assert order.status == OrderStatus.CANCELLED
    
    # Create new order and cancel from CONFIRMED
    order2 = Order(customer_id=2)
    order2.add_item(product_id=1, product_name="Item", price=1.0, quantity=1)
    order2.change_status(OrderStatus.CONFIRMED)
    saved_order2 = order_service.order_repository.save(order2)
    
    order = order_service.update_order_status(
        saved_order2.id, OrderStatus.CANCELLED, admin_user_id=10
    )
    assert order.status == OrderStatus.CANCELLED
