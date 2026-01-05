from fastapi.testclient import TestClient
from bakerySpotGourmet.main import app
from bakerySpotGourmet.core import security
from bakerySpotGourmet.core.constants import IDEMPOTENCY_KEY_HEADER
from bakerySpotGourmet.api.v1.dependencies import get_user_repository
from bakerySpotGourmet.repositories.user_repository import UserRepository
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from typing import Optional

def test_create_order_endpoint(client, user_repo):
    """Given a customer, creating an order returns 201 and correct totals."""
    # 1. Setup
    user = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(user)
    token = security.create_access_token(subject=1)
    
    payload = {
        "items": [
            {"product_id": 1, "quantity": 2}, # 10.0 * 2 = 20.0
        ],
        "order_type": "pickup"
    }
    
    # 2. Act
    response = client.post(
        "/api/v1/orders/",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            IDEMPOTENCY_KEY_HEADER: "create-order-test"
        }
    )
    
    # 3. Assert
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == 1
    assert data["total_amount"] == 20.0
    assert data["order_type"] == "pickup"
    assert data["status"] == "pending"


def test_create_order_idempotency(client, user_repo):
    """Test that duplicate requests with same idempotency key return cached response."""
    user = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(user)
    token = security.create_access_token(subject=1)
    
    payload = {"items": [{"product_id": 1, "quantity": 1}]}
    idempotency_key = "idemp-test-123"
    
    # First request
    response1 = client.post(
        "/api/v1/orders/",
        json=payload,
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: idempotency_key}
    )
    assert response1.status_code == 201
    order_id = response1.json()["id"]
    
    # Second request
    response2 = client.post(
        "/api/v1/orders/",
        json=payload,
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: idempotency_key}
    )
    assert response2.status_code == 201
    assert response2.json()["id"] == order_id


def test_create_delivery_order(client, user_repo):
    """Test creating an order with delivery type."""
    user = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(user)
    token = security.create_access_token(subject=1)
    
    payload = {
        "items": [{"product_id": 1, "quantity": 1}],
        "order_type": "delivery"
    }
    
    response = client.post(
        "/api/v1/orders/",
        json=payload,
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "delivery-test"}
    )
    
    assert response.status_code == 201
    assert response.json()["order_type"] == "delivery"
