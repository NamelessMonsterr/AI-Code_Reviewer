import pytest
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory"""
    test_dir = Path("tests/data")
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    # Cleanup after tests
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture
def sample_code():
    """Sample code for testing"""
    return """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(result)
"""

@pytest.fixture
def sample_issue():
    """Sample code issue"""
    return {
        'type': 'security',
        'severity': 'high',
        'message': 'Potential SQL injection',
        'line': 42
    }

@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Set up environment variables for tests"""
    monkeypatch.setenv("JWT_SECRET", "test_secret_key_at_least_32_chars_long_12345")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("CLAUDE_API_KEY", "test_key")
