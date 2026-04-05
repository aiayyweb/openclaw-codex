from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import create_app


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-with-32-bytes-min",
    )
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def register_user(client, username="alice", password="wonderland"):
    return client.post(
        "/register",
        json={"username": username, "password": password},
    )


def login_user(client, username="alice", password="wonderland"):
    return client.post(
        "/login",
        json={"username": username, "password": password},
    )


def make_token(app, username="alice", expired=False):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now - timedelta(seconds=1) if expired else now + timedelta(minutes=5),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def test_register_success(client):
    response = register_user(client)

    assert response.status_code == 201
    assert response.get_json()["message"] == "user registered successfully"


def test_register_duplicate_user(client):
    register_user(client)

    response = register_user(client)

    assert response.status_code == 409
    assert response.get_json()["error"] == "user already exists"


def test_register_requires_username_and_password(client):
    response = client.post("/register", json={"username": "", "password": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "username and password are required"


def test_login_success_returns_jwt(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    body = response.get_json()
    assert body["token_type"] == "Bearer"
    payload = jwt.decode(
        body["access_token"],
        "test-secret-key-with-32-bytes-min",
        algorithms=["HS256"],
    )
    assert payload["sub"] == "alice"


def test_login_rejects_invalid_password(client):
    register_user(client)

    response = login_user(client, password="wrong-password")

    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid credentials"


def test_login_requires_username_and_password(client):
    response = client.post("/login", json={"username": "", "password": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "username and password are required"


def test_protected_allows_valid_bearer_token(client, app):
    token = make_token(app)

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.get_json()["user"] == "alice"


def test_protected_requires_authorization_header(client):
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.get_json()["error"] == "missing or invalid authorization header"


def test_protected_rejects_expired_token(client, app):
    token = make_token(app, expired=True)

    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid or expired token"


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_allows_repeated_requests(client):
    first = client.get("/health")
    second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200
