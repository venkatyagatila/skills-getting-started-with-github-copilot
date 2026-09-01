"""Shared pytest fixtures and configuration."""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_student_email():
    """Provide a sample student email for testing."""
    return "test.student@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provide a sample activity name for testing."""
    return "Chess Club"
