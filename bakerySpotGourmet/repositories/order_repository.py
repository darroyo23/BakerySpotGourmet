from typing import Dict, Optional
from bakerySpotGourmet.domain.orders.order import Order

class OrderRepository:
    def __init__(self):
        self._orders: Dict[int, Order] = {}
        self._counter = 1

    def save(self, order: Order) -> Order:
        if order.id is None:
            order.id = self._counter
            self._counter += 1
        self._orders[order.id] = order
        return order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)
