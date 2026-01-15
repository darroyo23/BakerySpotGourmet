import pytest
from uuid import uuid4
from bakerySpotGourmet.domain.orders.order import Order, OrderItem
from bakerySpotGourmet.domain.orders.status import OrderStatus
from bakerySpotGourmet.domain.business_rules.fulfillment import FulfillmentType

def test_order_total_calculation():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.PICKUP)
    order.add_item(product_id=uuid4(), quantity=2, unit_price=10.0)
    order.add_item(product_id=uuid4(), quantity=1, unit_price=5.0)
    assert order.total == 25.0

def test_order_item_subtotal():
    item = OrderItem(product_id=uuid4(), quantity=3, unit_price=4.0)
    assert item.subtotal() == 12.0

def test_order_state_transitions():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.DELIVERY)
    order.add_item(product_id=uuid4(), quantity=1, unit_price=10.0)
    
    # Valid transitions
    order.transition_to(OrderStatus.CONFIRMED)
    assert order.status == OrderStatus.CONFIRMED
    
    order.transition_to(OrderStatus.PREPARING)
    assert order.status == OrderStatus.PREPARING
    
    order.transition_to(OrderStatus.ON_THE_WAY)
    assert order.status == OrderStatus.ON_THE_WAY
    
    order.transition_to(OrderStatus.DELIVERED)
    assert order.status == OrderStatus.DELIVERED

def test_invalid_order_state_transition():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.PICKUP)
    with pytest.raises(ValueError, match="Can only start preparing from CONFIRMED status"):
         order.transition_to(OrderStatus.PREPARING)

def test_confirm_empty_order():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.PICKUP)
    with pytest.raises(ValueError, match="Order must contain at least one item to be confirmed"):
        order.transition_to(OrderStatus.CONFIRMED)

def test_add_item_not_pending():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.PICKUP)
    order.add_item(product_id=uuid4(), quantity=1, unit_price=10.0)
    order.transition_to(OrderStatus.CONFIRMED)
    with pytest.raises(ValueError, match="Items can only be added when order is in PENDING status"):
        order.add_item(product_id=uuid4(), quantity=1, unit_price=5.0)

def test_on_the_way_only_for_delivery():
    order = Order(id=uuid4(), user_id=uuid4(), fulfillment_type=FulfillmentType.PICKUP)
    order.add_item(product_id=uuid4(), quantity=1, unit_price=10.0)
    order.transition_to(OrderStatus.CONFIRMED)
    order.transition_to(OrderStatus.PREPARING)
    with pytest.raises(ValueError, match="Only delivery orders can be ON_THE_WAY"):
        order.transition_to(OrderStatus.ON_THE_WAY)
