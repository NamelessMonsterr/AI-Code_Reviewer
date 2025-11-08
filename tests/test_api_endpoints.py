import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

class TestAPIEndpoints:
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()
    
    def test_health_check(self):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_review_endpoint_unauthorized(self):
        """Test review endpoint without auth"""
        response = client.post("/api/review", json={
            "code": "test",
            "language": "python"
        })
        assert response.status_code == 403
    
    # Add more endpoint tests...
