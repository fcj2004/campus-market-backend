"""Shared pytest fixtures."""

import os
import pytest

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite://",
)
os.environ.setdefault(
    "JWT_SECRET",
    "test-secret-that-is-long-enough-for-hs256-signing",
)

from app import create_app
from app.extensions import db, redis_client


class NoOpRedisCache:
    """Disable Redis during tests without changing app code."""

    enabled = False

    def init_app(self, app):
        pass

    def get_json(self, key):
        return None

    def set_json(self, key, value, ttl):
        pass

    def delete_pattern(self, pattern):
        pass


@pytest.fixture()
def app():
    # Swap the Redis implementation before create_app calls init_app.
    original_class = redis_client.__class__
    redis_client.__class__ = NoOpRedisCache
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        JWT_SECRET="test-secret-that-is-long-enough-for-hs256-signing",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    redis_client.__class__ = original_class


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    """Register two users and return tokens/ids for each."""
    client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "password123"},
    )
    client.post(
        "/api/auth/register",
        json={"username": "bob", "password": "password456"},
    )

    alice = client.post(
        "/api/auth/login",
        json={"username": "alice", "password": "password123"},
    ).get_json()["data"]
    bob = client.post(
        "/api/auth/login",
        json={"username": "bob", "password": "password456"},
    ).get_json()["data"]

    return {
        "alice": {
            "user_id": alice["user"]["id"],
            "headers": {"Authorization": f"Bearer {alice['token']}"},
        },
        "bob": {
            "user_id": bob["user"]["id"],
            "headers": {"Authorization": f"Bearer {bob['token']}"},
        },
    }
