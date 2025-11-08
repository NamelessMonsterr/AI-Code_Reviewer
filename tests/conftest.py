"""Pytest configuration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.fixture
def client():
    """Test client fixture."""
    from fastapi.testclient import TestClient
    from src.api.server import app
    return TestClient(app)
