"""
Tests for middleware functionality.
"""
import pytest
from fastapi.testclient import TestClient
from bakerySpotGourmet.main import app
from bakerySpotGourmet.core.constants import REQUEST_ID_HEADER


client = TestClient(app)


def test_request_id_generation():
    """Test that request ID is generated when not provided."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert REQUEST_ID_HEADER in response.headers
    assert len(response.headers[REQUEST_ID_HEADER]) > 0


def test_request_id_propagation():
    """Test that provided request ID is propagated."""
    custom_request_id = "test-request-123"
    
    response = client.get(
        "/health",
        headers={REQUEST_ID_HEADER: custom_request_id}
    )
    
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == custom_request_id


def test_request_timing_middleware():
    """Test that request timing middleware logs properly."""
    # This test verifies the middleware doesn't break requests
    # Actual timing logs would be verified in log output
    response = client.get("/health")
    
    assert response.status_code == 200


def test_multiple_requests_different_ids():
    """Test that different requests get different IDs."""
    response1 = client.get("/health")
    response2 = client.get("/health")
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    id1 = response1.headers[REQUEST_ID_HEADER]
    id2 = response2.headers[REQUEST_ID_HEADER]
    
    assert id1 != id2
