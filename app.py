"""
Flask REST API with JWT Authentication
User registration and login endpoints
"""

from flask import Flask, request, jsonify
import jwt
import datetime
import hashlib
from functools import wraps

app = Flask(__name__)

# In-memory user store: {username: hashed_password}
users = {}

# JWT configuration
JWT_SECRET = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def hash_password(password: str) -> str:
    """SHA-256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(username: str) -> str:
    """Generate JWT token for authenticated user"""
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.username = payload["username"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "username and password required"}), 400

    username = data["username"]
    password = data["password"]

    if username in users:
        return jsonify({"error": "User already exists"}), 409

    users[username] = hash_password(password)
    return jsonify({"message": f"User '{username}' registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    """Login and receive JWT token"""
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "username and password required"}), 400

    username = data["username"]
    password = data["password"]

    if username not in users or users[username] != hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(username)
    return jsonify({"token": token}), 200


@app.route("/protected", methods=["GET"])
@token_required
def protected():
    """Example protected endpoint"""
    return jsonify({"message": f"Hello, {request.username}! You are authenticated."}), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
