"""Pytest configuration and fixtures for Activities API tests.

Fixtures follow AAA (Arrange-Act-Assert) pattern by providing:
- Arrange: Fresh app instance with isolated test data
- Act: TestClient for making requests (used in tests)
- Assert: Tests validate responses and state changes
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Arrange: Create a TestClient with a fresh app instance.
    
    This fixture provides an isolated test environment with the app's
    original in-memory activities. Each test function gets its own client
    instance, but they share the same app instance.
    
    Note: Activity data is preserved across tests since the app's activities
    dict is a module-level global. For true isolation, tests should verify
    or manipulate data as needed.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Arrange: Provide a consistent test email address."""
    return "test.student@mergington.edu"


@pytest.fixture
def test_activity_name():
    """Arrange: Provide a known test activity name."""
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """Arrange: Provide a name for an activity that doesn't exist."""
    return "Nonexistent Activity"
