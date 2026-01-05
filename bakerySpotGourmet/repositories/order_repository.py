"""
Order repository for persistence operations.
"""
from typing import Dict, Optional, List
from bakerySpotGourmet.domain.orders.order import Order
from bakerySpotGourmet.domain.orders.status import OrderStatus


class OrderRepository:
    """In-memory order repository."""
    
    def __init__(self):
        self._orders: Dict[int, Order] = {}
        self._counter = 1

    def save(self, order: Order) -> Order:
        """
        Save a new order or update existing.
        
        Args:
            order: The order to save
            
        Returns:
            The saved order with ID assigned
        """
        if order.id is None:
            order.id = self._counter
            self._counter += 1
        self._orders[order.id] = order
        return order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieve an order by ID.
        
        Args:
            order_id: The order ID
            
        Returns:
            The order if found, None otherwise
        """
        return self._orders.get(order_id)
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """
        Retrieve all orders with optional filtering and pagination.
        
        Args:
            skip: Number of orders to skip
            limit: Maximum number of orders to return
            status: Optional status filter
            
        Returns:
            List of orders
        """
        orders = list(self._orders.values())
        
        # Filter by status if provided
        if status is not None:
            orders = [o for o in orders if o.status == status]
        
        # Sort by created_at descending (newest first)
        orders.sort(key=lambda o: o.created_at, reverse=True)
        
        # Apply pagination
        return orders[skip:skip + limit]
    
    def update(self, order: Order) -> Order:
        """
        Update an existing order.
        
        Args:
            order: The order to update
            
        Returns:
            The updated order
            
        Raises:
            ValueError: If order doesn't exist
        """
        if order.id is None or order.id not in self._orders:
            raise ValueError(f"Order {order.id} not found")
        
        self._orders[order.id] = order
        return order
