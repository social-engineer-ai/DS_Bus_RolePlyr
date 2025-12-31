"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test basic health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "stakeholder_sim"


def test_mock_users_endpoint():
    """Test mock users listing in development mode."""
    response = client.get("/api/v1/auth/mock-users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) > 0
    # Verify expected users exist
    user_keys = [u["key"] for u in data["users"]]
    assert "student1" in user_keys
    assert "instructor" in user_keys


def test_mock_login():
    """Test mock login endpoint."""
    response = client.post(
        "/api/v1/auth/mock-login",
        json={"user_key": "student1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "student"


def test_mock_login_invalid_user():
    """Test mock login with invalid user key."""
    response = client.post(
        "/api/v1/auth/mock-login",
        json={"user_key": "nonexistent"},
    )
    assert response.status_code == 400
