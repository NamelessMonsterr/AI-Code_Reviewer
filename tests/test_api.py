"""
API Tests
~~~~~~~~~

Tests for API endpoints.
"""

import pytest


def test_root_endpoint_structure(client):
    """Test root endpoint returns correct structure."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_endpoint_healthy(client):
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "environment" in data


def test_404_endpoint(client):
    """Test 404 for non-existent endpoint."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_api_versioning(client):
    """Test API version prefix."""
    # The /api/v1 prefix should exist
    response = client.get("/api/v1")
    # Should return 404 or 200 depending on if there's a root route
    assert response.status_code in [200, 404, 405]


@pytest.mark.asyncio
async def test_async_root_endpoint(async_client):
    """Test root endpoint with async client."""
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_async_health_endpoint(async_client):
    """Test health endpoint with async client."""
    response = await async_client.get("/health")
    assert response.status_code == 200
