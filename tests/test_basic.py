"""Basic tests."""
import sys


def test_python_version():
    """Test Python version is 3.10+."""
    assert sys.version_info >= (3, 10)


def test_basic_math():
    """Test basic operations."""
    assert 1 + 1 == 2
    assert 10 - 5 == 5
    assert 3 * 4 == 12


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


def test_info_endpoint(client):
    """Test info endpoint."""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
