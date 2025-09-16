"""
Tests for the main application endpoints.
"""

def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "wraiths-core"
    assert data["version"] == "1.0.0"


def test_docs_endpoint(client):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint(client):
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200
