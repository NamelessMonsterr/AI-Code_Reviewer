"""Basic tests."""
import sys


def test_python_version():
    """Test Python version is 3.10+."""
    assert sys.version_info >= (3, 10)


def test_basic():
    """Basic sanity test."""
    assert True


def test_math():
    """Test basic math."""
    assert 1 + 1 == 2
    assert 10 - 5 == 5


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["name"] == "AI Code Reviewer"


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
