"""Authentication endpoints."""

import datetime

import jwt
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def generate_token(user_id):
    """Create a signed JWT for the given user."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now
        + datetime.timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"]),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET"],
        algorithm="HS256",
    )


def decode_token(token):
    """Validate a JWT and return its subject, or None when invalid."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None


def get_current_user_id():
    """Extract authenticated user id from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return decode_token(auth_header[7:])


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()

    if not username or len(password) < 6:
        return jsonify({"code": 400, "message": "invalid username or password"}), 400

    user = User(username=username, nickname=nickname)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"code": 409, "message": "username already exists"}), 409

    return jsonify({"code": 0, "data": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"code": 401, "message": "invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify({"code": 0, "data": {"token": token, "user": user.to_dict()}})
