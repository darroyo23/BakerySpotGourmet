from typing import List, Optional
from bakerySpotGourmet.domain.catalog.product import Product

class ItemRepository:
    def __init__(self):
        # Dummy in-memory data
        self._items = {
            1: Product(id=1, name="Croissant", price=2.50, description="Buttery flaky pastry"),
            2: Product(id=2, name="Baguette", price=1.50, description="French bread"),
            3: Product(id=3, name="Espresso", price=3.00, description="Strong coffee"),
        }

    def get_by_id(self, item_id: int) -> Optional[Product]:
        return self._items.get(item_id)
    
    def save(self, product: Product) -> Product:
        """
        Save a product to the repository.
        """
        self._items[product.id] = product
        return product
