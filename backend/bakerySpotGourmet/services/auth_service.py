from typing import Optional
from datetime import timedelta

from bakerySpotGourmet.core import security
from bakerySpotGourmet.repositories.user_repository import UserRepository
from bakerySpotGourmet.schemas.user import Token
from bakerySpotGourmet.domain.users.entities import UserIdentity

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def authenticate_user(self, email: str, password: str) -> Optional[UserIdentity]:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user: UserIdentity) -> Token:
        access_token_expires = timedelta(minutes=security.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        refresh_token = security.create_refresh_token(subject=user.id)
        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token,
        )
