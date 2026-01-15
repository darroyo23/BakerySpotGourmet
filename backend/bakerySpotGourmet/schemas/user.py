"""
User Pydantic schemas.
Request and response DTOs for user operations.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from bakerySpotGourmet.domain.users.entities import RoleName

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    role: RoleName = RoleName.CUSTOMER

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None
    role: Optional[RoleName] = None

class UserInDBBase(UserBase):
    id: int | None = None
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenPayload(BaseModel):
    sub: int | None = None
