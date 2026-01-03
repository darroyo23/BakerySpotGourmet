from unittest.mock import Mock
from bakerySpotGourmet.services.auth_service import AuthService
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from bakerySpotGourmet.core import security

def test_authenticate_user_success():
    mock_repo = Mock()
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    user = UserIdentity(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        role=Role.CUSTOMER
    )
    mock_repo.get_by_email.return_value = user
    
    service = AuthService(mock_repo)
    authenticated_user = service.authenticate_user("test@example.com", password)
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"

def test_authenticate_user_wrong_password():
    mock_repo = Mock()
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    user = UserIdentity(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        role=Role.CUSTOMER
    )
    mock_repo.get_by_email.return_value = user
    
    service = AuthService(mock_repo)
    authenticated_user = service.authenticate_user("test@example.com", "wrongpassword")
    assert authenticated_user is None
