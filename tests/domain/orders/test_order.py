import pytest
from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.domain.orders.status import OrderStatus

def test_add_item_calculation():
    order = Order(customer_id=1)
    order.add_item(product_id=1, product_name="Test Product", price=10.0, quantity=2)
    
    assert len(order.items) == 1
    assert order.items[0].subtotal == 20.0
    assert order.total_amount == 20.0

def test_multiple_items_calculation():
    order = Order(customer_id=1)
    order.add_item(product_id=1, product_name="P1", price=10.0, quantity=1)
    order.add_item(product_id=2, product_name="P2", price=5.5, quantity=2)
    
    assert len(order.items) == 2
    assert order.total_amount == 21.0

def test_invalid_quantity():
    order = Order(customer_id=1)
    with pytest.raises(ValueError):
        order.add_item(product_id=1, product_name="P1", price=10.0, quantity=0)

def test_default_status():
    order = Order(customer_id=1)
    assert order.status == OrderStatus.PENDING
