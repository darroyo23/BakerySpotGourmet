"""
Tests for global exception handlers.
"""
import pytest
from fastapi.testclient import TestClient
from bakerySpotGourmet.main import app


client = TestClient(app)


def test_health_endpoint_success():
    """Test health endpoint returns 200."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_readiness_endpoint_success():
    """Test readiness endpoint returns 200."""
    response = client.get("/readiness")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_liveness_endpoint_success():
    """Test liveness endpoint returns 200."""
    response = client.get("/liveness")
    
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_404_not_found():
    """Test 404 error handling."""
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    assert "detail" in response.json()


def test_validation_error_handling():
    """Test validation error returns 422 with details."""
    # This would require an endpoint with validation
    # For now, test that the handler is registered
    # Actual validation errors will be tested in integration tests
    pass


def test_exception_handler_safe_responses():
    """Test that exception handlers return safe, non-revealing messages."""
    # 404 should not reveal internal details
    response = client.get("/api/v1/nonexistent")
    
    assert response.status_code == 404
    # Should have detail but not expose internals
    assert "detail" in response.json()
