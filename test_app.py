"""
pytest unit tests for Flask JWT REST API
"""

import pytest
from app import app, hash_password, users


@pytest.fixture
def client():
    """Create test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
        users.clear()


class TestHealth:
    """Health check endpoint tests"""

    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestRegister:
    """User registration endpoint tests"""

    def test_register_success(self, client):
        response = client.post("/register", json={
            "username": "alice",
            "password": "secret123"
        })
        assert response.status_code == 201
        assert "registered successfully" in response.get_json()["message"]

    def test_register_missing_fields(self, client):
        response = client.post("/register", json={"username": "alice"})
        assert response.status_code == 400

    def test_register_duplicate_user(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/register", json={"username": "alice", "password": "secret456"})
        assert response.status_code == 409


class TestLogin:
    """User login endpoint tests"""

    def test_login_success(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/login", json={"username": "alice", "password": "secret123"})
        assert response.status_code == 200
        assert "token" in response.get_json()

    def test_login_wrong_password(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        response = client.post("/login", json={"username": "alice", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/login", json={"username": "bob", "password": "secret123"})
        assert response.status_code == 401


class TestProtected:
    """Protected endpoint tests"""

    def test_protected_with_valid_token(self, client):
        client.post("/register", json={"username": "alice", "password": "secret123"})
        login_response = client.post("/login", json={"username": "alice", "password": "secret123"})
        token = login_response.get_json()["token"]

        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "authenticated" in response.get_json()["message"]

    def test_protected_without_token(self, client):
        response = client.get("/protected")
        assert response.status_code == 401

    def test_protected_with_invalid_token(self, client):
        response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401


class TestHashPassword:
    """Password hashing utility tests"""

    def test_hash_password_consistency(self):
        hashed = hash_password("secret123")
        assert hash_password("secret123") == hashed

    def test_hash_password_different_inputs(self):
        assert hash_password("password1") != hash_password("password2")
