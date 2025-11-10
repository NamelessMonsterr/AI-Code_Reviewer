"""Pytest configuration and fixtures."""

import pytest
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["TESTING"] = "True"


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from src.api.server import app

    return TestClient(app)


@pytest.fixture
def test_settings():
    """Test settings."""
    from src.core.config import settings

    return settings
