from dataclasses import dataclass
from uuid import UUID


@dataclass
class Product:
    """
    Product domain entity.
    Represents an item for sale in the bakery.
    """
    id: UUID
    category_id: UUID
    name: str
    cost_price: float
    sale_price: float
    is_active: bool = True

    def margin_percentage(self) -> float:
        """
        Calculate the margin percentage of the product.
        
        Returns:
            The margin percentage as a decimal (e.g., 0.5 for 50%).
            
        Raises:
            ZeroDivisionError: If sale_price is zero.
        """
        if self.sale_price == 0:
            return 0.0
        return (self.sale_price - self.cost_price) / self.sale_price
