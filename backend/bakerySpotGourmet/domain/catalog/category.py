from dataclasses import dataclass
from uuid import UUID


@dataclass
class Category:
    """
    Category domain entity.
    Represents a group of products.
    """
    id: UUID
    name: str
    is_active: bool = True
