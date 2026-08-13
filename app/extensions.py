"""Shared extension instances."""

from flask_sqlalchemy import SQLAlchemy

from app.cache import RedisCache

db = SQLAlchemy()
redis_client = RedisCache()

