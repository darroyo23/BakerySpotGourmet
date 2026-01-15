from dataclasses import dataclass, field
from datetime import time
from typing import List
from uuid import UUID


@dataclass
class ComboItem:
    """
    ComboItem domain entity.
    """
    product_id: UUID
    quantity: int


@dataclass
class Combo:
    """
    Combo domain entity.
    A bundle of products sold as a single item.
    """
    id: UUID
    name: str
    price: float
    is_active: bool = True
    items: List[ComboItem] = field(default_factory=list)


@dataclass
class ComboAvailability:
    """
    ComboAvailability domain entity.
    Defines when a combo is available for purchase.
    """
    combo_id: UUID
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
