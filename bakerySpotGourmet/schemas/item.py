"""
Item Pydantic schemas.
Request and response DTOs for item operations.
"""

from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDBBase(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class Item(ItemInDBBase):
    pass
