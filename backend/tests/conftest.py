from typing import Generator
import pytest
from fastapi.testclient import TestClient

from bakerySpotGourmet.main import app
from bakerySpotGourmet.api.v1 import dependencies as deps
from bakerySpotGourmet.repositories.user_repository import UserRepository
from bakerySpotGourmet.repositories.order_repository import OrderRepository
from bakerySpotGourmet.repositories.item_repository import ItemRepository
from bakerySpotGourmet.repositories.payment_repository import PaymentRepository


@pytest.fixture(scope="function")
def user_repo() -> UserRepository:
    return UserRepository()


@pytest.fixture(scope="function")
def order_repo() -> OrderRepository:
    return OrderRepository()


@pytest.fixture(scope="function")
def item_repo() -> ItemRepository:
    repo = ItemRepository()
    # Pre-populate with a test item for common use
    from bakerySpotGourmet.domain.catalog.product import Product
    repo.save(Product(id=1, name="Test Croissant", price=10.0, is_active=True))
    return repo


@pytest.fixture(scope="function")
def payment_repo() -> PaymentRepository:
    return PaymentRepository()


@pytest.fixture(scope="function")
def client(user_repo, order_repo, item_repo, payment_repo) -> Generator:
    # Set up dependency overrides
    app.dependency_overrides[deps.get_user_repository] = lambda: user_repo
    app.dependency_overrides[deps.get_order_repository] = lambda: order_repo
    app.dependency_overrides[deps.get_item_repository] = lambda: item_repo
    app.dependency_overrides[deps.get_payment_repository] = lambda: payment_repo
    
    with TestClient(app) as c:
        yield c
    
    # Clean up overrides
    app.dependency_overrides = {}
