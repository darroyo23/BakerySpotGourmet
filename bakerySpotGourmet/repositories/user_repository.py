from typing import Optional
from bakerySpotGourmet.domain.users.entities import UserIdentity

class UserRepository:
    def __init__(self):
        self._users = {}

    def get_by_email(self, email: str) -> Optional[UserIdentity]:
        return next((u for u in self._users.values() if u.email == email), None)

    def get_by_id(self, user_id: int) -> Optional[UserIdentity]:
        return self._users.get(user_id)
    
    def save(self, user: UserIdentity) -> UserIdentity:
        """Save a user to the repository."""
        self._users[user.id] = user
        return user
