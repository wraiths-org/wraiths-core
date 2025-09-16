"""
Pytest configuration and fixtures for WRAITHS Core tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_event():
    """Sample event data for testing."""
    return {
        "eventId": "123e4567-e89b-12d3-a456-426614174000",
        "correlationId": "123e4567-e89b-12d3-a456-426614174001",
        "timestamp": "2025-09-14T10:30:00Z",
        "source": {
            "service": "test-service",
            "version": "1.0.0"
        },
        "subject": "tool.invoke.test.example",
        "eventType": "invoke",
        "payload": {
            "test": "data"
        }
    }
