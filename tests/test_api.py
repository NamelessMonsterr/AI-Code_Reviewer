import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_code_review_endpoint(client: TestClient):
    code_sample = {
        "code": "def hello(): print('world')",
        "language": "python"
    }
    response = client.post("/api/v1/review", json=code_sample)
    assert response.status_code == 200
    assert "review" in response.json()

@pytest.mark.asyncio
async def test_async_review():
    # Add async tests here
    pass
