from typing import Optional
from bakerySpotGourmet.domain.users.entities import UserIdentity

class UserRepository:

    def get_by_email(self, email: str) -> Optional[UserIdentity]:
        # TODO: Implement actual DB access
        return None

    def get_by_id(self, user_id: int) -> Optional[UserIdentity]:
        # TODO: Implement actual DB access
        return None
