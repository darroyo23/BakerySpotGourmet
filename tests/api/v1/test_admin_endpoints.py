"""
Integration tests for admin endpoints.
"""
import pytest
from bakerySpotGourmet.core import security
from bakerySpotGourmet.core.constants import IDEMPOTENCY_KEY_HEADER
from bakerySpotGourmet.domain.users.entities import UserIdentity, Role
from bakerySpotGourmet.domain.orders.status import OrderStatus


def test_list_orders_as_admin(client, user_repo):
    """Test listing orders as ADMIN user."""
    # Given: A test order and an admin user
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)  # Customer
    
    create_res = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 2}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "admin-list-test"}
    )
    assert create_res.status_code == 201
    
    admin = UserIdentity(id=10, email="admin@test.com", hashed_password="pw", role=Role.ADMIN)
    user_repo.save(admin)
    admin_token = security.create_access_token(subject=10)
    
    # When: Admin lists orders
    response = client.get(
        "/api/v1/admin/orders",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then: Order is present in the list
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(o["customer_id"] == 1 for o in data)


def test_list_orders_as_staff(client, user_repo):
    """Test listing orders as STAFF user."""
    staff = UserIdentity(id=11, email="staff@test.com", hashed_password="pw", role=Role.STAFF)
    user_repo.save(staff)
    staff_token = security.create_access_token(subject=11)
    
    response = client.get(
        "/api/v1/admin/orders",
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_orders_as_customer_denied(client, user_repo):
    """Test that CUSTOMER cannot list orders."""
    # Given: A customer user
    customer = UserIdentity(id=1, email="customer@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    # When: Customer tries to access admin endpoint
    response = client.get(
        "/api/v1/admin/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Then: Access is forbidden (403)
    assert response.status_code == 403


def test_list_orders_with_status_filter(client, user_repo):
    """Test listing orders with status filter."""
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "filter-test"}
    )
    
    admin = UserIdentity(id=10, email="admin@test.com", hashed_password="pw", role=Role.ADMIN)
    user_repo.save(admin)
    admin_token = security.create_access_token(subject=10)
    
    # Filter by PENDING
    response = client.get(
        "/api/v1/admin/orders?status=pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert all(o["status"] == "pending" for o in data)


def test_get_order_by_id_as_admin(client, user_repo):
    """Test retrieving order by ID as ADMIN."""
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    create_res = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "get-test"}
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]
    
    admin = UserIdentity(id=10, email="admin@test.com", hashed_password="pw", role=Role.ADMIN)
    user_repo.save(admin)
    admin_token = security.create_access_token(subject=10)
    
    response = client.get(
        f"/api/v1/admin/orders/{order_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_update_order_status_as_admin(client, user_repo):
    """Test updating order status as ADMIN."""
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    create_res = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "update-test"}
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]
    
    admin = UserIdentity(id=10, email="admin@test.com", hashed_password="pw", role=Role.ADMIN)
    user_repo.save(admin)
    admin_token = security.create_access_token(subject=10)
    
    # Update to CONFIRMED
    response = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_staff_cannot_cancel_order(client, user_repo):
    """Test STAFF cannot cancel orders."""
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    create_res = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "staff-cancel-test"}
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]
    
    staff = UserIdentity(id=11, email="staff@test.com", hashed_password="pw", role=Role.STAFF)
    user_repo.save(staff)
    staff_token = security.create_access_token(subject=11)
    
    # STAFF cannot cancel
    response = client.patch(
        f"/api/v1/admin/orders/{order_id}/status",
        json={"status": "cancelled"},
        headers={"Authorization": f"Bearer {staff_token}"}
    )
    
    assert response.status_code == 403
    assert "STAFF users cannot cancel" in response.json()["detail"]


def test_full_order_workflow(client, user_repo):
    """Test complete order workflow from creation to delivery."""
    customer = UserIdentity(id=1, email="c@test.com", hashed_password="pw", role=Role.CUSTOMER)
    user_repo.save(customer)
    token = security.create_access_token(subject=1)
    
    create_res = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"Authorization": f"Bearer {token}", IDEMPOTENCY_KEY_HEADER: "workflow-test"}
    )
    assert create_res.status_code == 201
    order_id = create_res.json()["id"]
    
    admin = UserIdentity(id=10, email="admin@test.com", hashed_password="pw", role=Role.ADMIN)
    user_repo.save(admin)
    admin_token = security.create_access_token(subject=10)
    
    # Workflow transitions
    for status in ["confirmed", "preparing", "ready", "delivered"]:
        res = client.patch(
            f"/api/v1/admin/orders/{order_id}/status",
            json={"status": status},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        assert res.json()["status"] == status
