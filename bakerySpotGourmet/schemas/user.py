"""
User Pydantic schemas.
Request and response DTOs for user operations.
"""

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None

class UserInDBBase(UserBase):
    id: int | None = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
