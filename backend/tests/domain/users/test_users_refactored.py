from uuid import uuid4
from bakerySpotGourmet.domain.users.entities import User, Role, RoleName

def test_user_deactivation():
    role = Role(id=1, name=RoleName.CUSTOMER)
    user = User(id=uuid4(), email="test@example.com", role=role)
    assert user.is_active is True
    user.deactivate()
    assert user.is_active is False

def test_role_creation():
    role = Role(id=1, name=RoleName.ADMIN)
    assert role.name == RoleName.ADMIN
