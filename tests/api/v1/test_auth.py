from fastapi.testclient import TestClient
from bakerySpotGourmet.main import app
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from bakerySpotGourmet.core import security
from bakerySpotGourmet.api.v1.dependencies import get_user_repository
from bakerySpotGourmet.repositories.user_repository import UserRepository
from typing import Optional

def test_login_access_token(client: TestClient):
    # Setup mock
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    user = UserIdentity(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        role=Role.CUSTOMER
    )
    
    class MockRepo(UserRepository):
        def get_by_email(self, email: str) -> Optional[UserIdentity]:
            if email == "test@example.com":
                return user
            return None
        def get_by_id(self, user_id: int) -> Optional[UserIdentity]:
             if user_id == 1:
                 return user
             return None

    app.dependency_overrides[get_user_repository] = lambda: MockRepo()

    response = client.post(
        "/api/v1/users/login/access-token",
        data={"username": "test@example.com", "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Clean up
    app.dependency_overrides = {}

def test_login_wrong_password(client: TestClient):
     # Setup mock
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    user = UserIdentity(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        role=Role.CUSTOMER
    )
    
    class MockRepo(UserRepository):
        def get_by_email(self, email: str) -> Optional[UserIdentity]:
            if email == "test@example.com":
                return user
            return None

    app.dependency_overrides[get_user_repository] = lambda: MockRepo()
    
    response = client.post(
        "/api/v1/users/login/access-token",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    
    # Clean up
    app.dependency_overrides = {}

def test_read_users_me(client: TestClient):
    # Setup mock
    password = "secretpassword"
    hashed = security.get_password_hash(password)
    user = UserIdentity(
        id=1,
        email="test@example.com",
        hashed_password=hashed,
        role=Role.CUSTOMER
    )
    
    class MockRepo(UserRepository):
        def get_by_id(self, user_id: int) -> Optional[UserIdentity]:
             if user_id == 1:
                 return user
             return None

    app.dependency_overrides[get_user_repository] = lambda: MockRepo()
    
    # Create valid token
    token = security.create_access_token(subject=1)
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == Role.CUSTOMER
    
    # Clean up
    app.dependency_overrides = {}
