"""Application configuration."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration loaded from environment variables."""

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/campus_market",
    )
    # Flask-SQLAlchemy reads this key when initializing the engine.
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET = os.getenv(
        "JWT_SECRET",
        "dev-secret-change-me-please-use-a-long-random-value",
    )
    JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Product list hot cache TTL in seconds.
    PRODUCT_CACHE_TTL = 300
