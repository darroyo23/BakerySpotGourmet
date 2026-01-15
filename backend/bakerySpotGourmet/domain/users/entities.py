from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


class RoleName(str, Enum):
    """Enumeration of user roles."""
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"


@dataclass
class Role:
    """Role domain entity."""
    id: int
    name: RoleName


@dataclass
class User:
    """
    User domain entity.
    Pure Python class, no framework dependencies.
    """
    id: UUID
    email: str
    role: Role
    is_active: bool = True

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False


# Temporary alias for backward compatibility
UserIdentity = User
