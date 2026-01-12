from fastapi.testclient import TestClient
from bakerySpotGourmet.core.config import settings


def test_health_check(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_liveness_check(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
