from typing import List
from fastapi import HTTPException

from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.repositories.item_repository import ItemRepository
from bakerySpotGourmet.repositories.order_repository import OrderRepository
from bakerySpotGourmet.schemas.order import OrderCreate

class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        item_repository: ItemRepository
    ):
        self.order_repository = order_repository
        self.item_repository = item_repository

    def create_order(self, customer_id: int, order_in: OrderCreate) -> Order:
        """
        Create a new order.
        Validates products, creates domain entity, and saves it.
        """
        # 1. Create Order Aggregate
        order = Order(customer_id=customer_id)
        
        # 2. Add items to order (validating each)
        for item_in in order_in.items:
            product = self.item_repository.get_by_id(item_in.product_id)
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {item_in.product_id} not found")
            if not product.is_active:
                raise HTTPException(status_code=400, detail=f"Product {item_in.product_id} is not active")
            
            order.add_item(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=item_in.quantity
            )
            
        # 3. Persist (should be transactional)
        saved_order = self.order_repository.save(order)
        
        return saved_order
