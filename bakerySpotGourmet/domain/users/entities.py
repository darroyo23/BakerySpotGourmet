from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CUSTOMER = "customer"

@dataclass
class UserIdentity:
    """
    User Core Entity.
    Pure Python class, no ORM dependencies here.
    """
    id: Optional[int]
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: Role = Role.CUSTOMER
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
