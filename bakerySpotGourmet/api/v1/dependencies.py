"""
API Dependencies.
Common dependency injection.
"""
from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError

from bakerySpotGourmet.core import security
from bakerySpotGourmet.core.config import settings
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from bakerySpotGourmet.repositories.user_repository import UserRepository
from bakerySpotGourmet.schemas.user import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login/access-token"
)

def get_user_repository() -> UserRepository:
    return UserRepository()

def get_item_repository() -> "ItemRepository": # type: ignore
    from bakerySpotGourmet.repositories.item_repository import ItemRepository
    return ItemRepository()

def get_order_repository() -> "OrderRepository": # type: ignore
    from bakerySpotGourmet.repositories.order_repository import OrderRepository
    return OrderRepository()

def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> "AuthService": # type: ignore
    from bakerySpotGourmet.services.auth_service import AuthService
    return AuthService(user_repo)

def get_order_service(
    order_repo: Annotated["OrderRepository", Depends(get_order_repository)],
    item_repo: Annotated["ItemRepository", Depends(get_item_repository)],
) -> "OrderService": # type: ignore
    from bakerySpotGourmet.services.order_service import OrderService
    return OrderService(order_repo, item_repo)

async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserIdentity:
    try:
        payload = security.decode_token(token)
        if payload is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Assuming sub is user_id (int)
    if token_data.sub is None:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    user = user_repo.get_by_id(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_superuser(
    current_user: Annotated[UserIdentity, Depends(get_current_user)],
) -> UserIdentity:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[UserIdentity, Depends(get_current_user)]) -> UserIdentity:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges"
            )
        return user
