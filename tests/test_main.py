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


def test_version_endpoint(client):
    """Test the version endpoint returns expected fields."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "wraiths-core"
    assert data["version"] == "1.0.0"
    # commit/branch may be None in CI; ensure keys exist
    assert "commit" in data
    assert "branch" in data
    assert "build_time" in data
    assert "environment" in data


def test_correlation_id_header_propagation(client):
    """Middleware should propagate x-correlation-id header back in response."""
    corr = "test-corr-123"
    response = client.get("/health", headers={"x-correlation-id": corr})
    assert response.status_code == 200
    assert response.headers.get("x-correlation-id") == corr


def test_readiness_endpoint(client):
    """Readiness should return JSON and status 200 in base state."""
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "ready" in data
    assert "dependencies" in data


def test_security_headers_present(client):
    """Basic security headers should be present on responses."""
    response = client.get("/health")
    # Non-breaking presence (some may be absent in dev)
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
