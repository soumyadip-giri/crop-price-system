# backend/auth_routes.py
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, current_app

from . import config
from .persistence import user_repository

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


# ---------------- JWT helpers ----------------

def create_token(user_id: str) -> str:
    """Create a short-lived JWT for API auth."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=4),
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGO)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_token(token: str):
    """Return user_id (sub) if token is valid, else None."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGO])
        return payload.get("sub")
    except Exception:
        return None


def auth_required(fn):
    """Decorator for protecting API routes with Bearer token."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth_header.split(" ", 1)[1]
        user_id = decode_token(token)

        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user_id = user_id
        return fn(*args, **kwargs)

    return wrapper


# ---------------- Auth endpoints ----------------

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json() or {}
        required = ["name", "email", "userid", "password", "dob"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing fields"}), 400

        user, err = user_repository.create_user(
            data["name"],
            data["email"],
            data["userid"],
            data["password"],
            data["dob"],
        )

        if err == "USERID_EXISTS":
            return jsonify({"error": "User id already exists"}), 409
        if err == "EMAIL_EXISTS":
            return jsonify({"error": "Email already registered"}), 409

        return jsonify({"message": "Registered successfully"}), 201

    except Exception:
        current_app.logger.exception("Error in /api/auth/register")
        return jsonify({"error": "Server error while registering user"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json() or {}
        if "userid" not in data or "password" not in data:
            return jsonify({"error": "Missing userid or password"}), 400

        user = user_repository.verify_user(data["userid"], data["password"])
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_token(str(user["_id"]))
        return jsonify(
            {
                "token": token,
                "user": {
                    "name": user["name"],
                    "email": user["email"],
                    "userid": user["userid"],
                },
            }
        )

    except Exception:
        current_app.logger.exception("Error in /api/auth/login")
        return jsonify({"error": "Server error while logging in"}), 500
