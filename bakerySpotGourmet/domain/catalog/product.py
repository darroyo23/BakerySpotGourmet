from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    """
    Product Domain Entity.
    """
    id: int
    name: str
    price: float
    description: Optional[str] = None
    is_active: bool = True
