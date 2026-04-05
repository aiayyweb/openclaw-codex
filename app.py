from datetime import datetime, timedelta, timezone
import os

import jwt
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me-to-32-bytes",
    )
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_EXPIRATION_SECONDS"] = 3600
    app.config["USERS"] = {}

    def build_token(username: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "iat": now,
            "exp": now + timedelta(seconds=app.config["JWT_EXPIRATION_SECONDS"]),
        }
        return jwt.encode(
            payload,
            app.config["SECRET_KEY"],
            algorithm=app.config["JWT_ALGORITHM"],
        )

    def decode_token(token: str) -> dict:
        return jwt.decode(
            token,
            app.config["SECRET_KEY"],
            algorithms=[app.config["JWT_ALGORITHM"]],
        )

    def get_bearer_token() -> str | None:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ", 1)[1].strip()
        return token or None

    @app.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    @app.post("/register")
    def register() -> tuple:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        users = app.config["USERS"]
        if username in users:
            return jsonify({"error": "user already exists"}), 409

        users[username] = generate_password_hash(password)
        return jsonify({"message": "user registered successfully"}), 201

    @app.post("/login")
    def login() -> tuple:
        data = request.get_json(silent=True) or {}
        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        users = app.config["USERS"]
        stored_password = users.get(username)
        if stored_password is None or not check_password_hash(stored_password, password):
            return jsonify({"error": "invalid credentials"}), 401

        token = build_token(username)
        return jsonify({"access_token": token, "token_type": "Bearer"}), 200

    @app.get("/protected")
    def protected() -> tuple:
        token = get_bearer_token()
        if token is None:
            return jsonify({"error": "missing or invalid authorization header"}), 401

        try:
            payload = decode_token(token)
        except jwt.PyJWTError:
            return jsonify({"error": "invalid or expired token"}), 401

        return jsonify({"message": "access granted", "user": payload["sub"]}), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
