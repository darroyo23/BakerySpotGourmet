"""
Item/Product Pydantic schemas.
Request and response DTOs for item operations.
"""

from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str | None = None
    price: float = 0.0
    is_active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: Optional[str] = None
    price: Optional[float] = None

class ItemInDBBase(ItemBase):
    id: int
    
    class Config:
        from_attributes = True

class Item(ItemInDBBase):
    pass
