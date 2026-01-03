from fastapi.testclient import TestClient
from bakerySpotGourmet.main import app
from bakerySpotGourmet.core import security
from bakerySpotGourmet.api.v1.dependencies import get_user_repository
from bakerySpotGourmet.repositories.user_repository import UserRepository
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from typing import Optional

def test_create_order_endpoint(client: TestClient):
    # 1. Setup Auth Mock
    user = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    
    class MockUserRepo(UserRepository):
        def get_by_id(self, user_id: int) -> Optional[UserIdentity]:
            if user_id == 1:
                return user
            return None
            
    app.dependency_overrides[get_user_repository] = lambda: MockUserRepo()
    
    # Generate token
    token = security.create_access_token(subject=1)
    
    # 2. Call API (assuming product 1 exists in default in-memory repo)
    payload = {
        "items": [
            {"product_id": 1, "quantity": 2}, # Croissant 2.50 * 2 = 5.00
            {"product_id": 3, "quantity": 1}  # Espresso 3.00 * 1 = 3.00
        ]
    }
    
    response = client.post(
        "/api/v1/orders/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 3. Assert
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == 1
    assert data["total_amount"] == 8.0
    assert len(data["items"]) == 2
    
    app.dependency_overrides = {}
