"""
User API Endpoints.
"""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from bakerySpotGourmet.api.v1 import dependencies as deps
from bakerySpotGourmet.domain.users.entities import UserIdentity
from bakerySpotGourmet.schemas.user import Token, User
from bakerySpotGourmet.services.auth_service import AuthService

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(deps.get_auth_service)],
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return auth_service.create_tokens(user)

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    # TODO: Implement refresh token logic (validate refresh token)
    # For now reusing login logic pattern or just creating new tokens for current user
    current_user: Annotated[UserIdentity, Depends(deps.get_current_user)],
    auth_service: Annotated[AuthService, Depends(deps.get_auth_service)],
) -> Any:
    """
    Refresh tokens. 
    Note: Real implementation should validate the refresh token specifically.
    For this scope, we return new tokens for the authenticated user.
    """
    return auth_service.create_tokens(current_user)

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[UserIdentity, Depends(deps.get_current_user)],
) -> Any:
    """
    Get current user.
    """
    return current_user
