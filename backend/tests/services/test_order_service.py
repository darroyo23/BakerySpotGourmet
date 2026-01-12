import pytest
from fastapi import HTTPException
from unittest.mock import Mock

from bakerySpotGourmet.services.order_service import OrderService
from bakerySpotGourmet.schemas.order import OrderCreate, OrderItemCreate
from bakerySpotGourmet.domain.catalog.product import Product

def test_create_order_success():
    order_repo = Mock()
    payment_repo = Mock()
    item_repo = Mock()
    
    # Mock product lookup
    item_repo.get_by_id.return_value = Product(id=1, name="Croissant", price=2.0)
    
    # Mock save to return the order with an ID
    def save_side_effect(order):
        order.id = 123
        return order
    order_repo.save.side_effect = save_side_effect
    
    service = OrderService(order_repo, payment_repo, item_repo)
    
    order_in = OrderCreate(items=[OrderItemCreate(product_id=1, quantity=3)])
    created_order = service.create_order(customer_id=99, order_in=order_in)
    
    assert created_order.customer_id == 99
    assert created_order.total_amount == 6.0
    order_repo.save.assert_called_once()

def test_create_order_product_not_found():
    order_repo = Mock()
    payment_repo = Mock()
    item_repo = Mock()
    item_repo.get_by_id.return_value = None
    
    service = OrderService(order_repo, payment_repo, item_repo)
    order_in = OrderCreate(items=[OrderItemCreate(product_id=9, quantity=1)])
    
    with pytest.raises(HTTPException) as exc:
        service.create_order(customer_id=1, order_in=order_in)
    assert exc.value.status_code == 400

def test_create_order_product_inactive():
    order_repo = Mock()
    payment_repo = Mock()
    item_repo = Mock()
    item_repo.get_by_id.return_value = Product(id=1, name="Old", price=1.0, is_active=False)
    
    service = OrderService(order_repo, payment_repo, item_repo)
    order_in = OrderCreate(items=[OrderItemCreate(product_id=1, quantity=1)])
    
    with pytest.raises(HTTPException) as exc:
        service.create_order(customer_id=1, order_in=order_in)
    assert exc.value.status_code == 400
