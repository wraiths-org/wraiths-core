"""Smoke test for FastAPI lifespan startup/shutdown."""

from fastapi.testclient import TestClient
from src.main import app


def test_lifespan_smoke():
    """Ensure the app sets and clears state during lifespan."""
    with TestClient(app) as client:
        # Within context, startup should have run
        assert getattr(app.state, "started", False) is True
        r = client.get("/health")
        assert r.status_code == 200
    # After exiting context, shutdown should have run
    assert getattr(app.state, "started", False) is False
