"""Redis cache wrapper with graceful degradation."""

import json
import logging

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Thin Redis wrapper. Falls back to a no-op cache when unavailable."""

    def __init__(self):
        self.client = None
        self.enabled = False

    def init_app(self, app):
        self.app = app
        try:
            self.client = redis.from_url(
                app.config["REDIS_URL"],
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2,
            )
            self.client.ping()
            self.enabled = True
        except (redis.RedisError, OSError) as exc:
            logger.warning("Redis unavailable, cache disabled: %s", exc)

    def get_json(self, key):
        if not self.enabled:
            return None
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except (redis.RedisError, ValueError, TypeError):
            return None

    def set_json(self, key, value, ttl):
        if not self.enabled:
            return
        try:
            self.client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        except (redis.RedisError, ValueError, TypeError):
            logger.exception("Failed to write cache key %s", key)

    def delete_pattern(self, pattern):
        """Delete keys matching a pattern with SCAN to avoid blocking."""
        if not self.enabled:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    self.client.delete(*keys)
                if cursor == 0:
                    break
        except redis.RedisError:
            logger.exception("Failed to invalidate cache pattern %s", pattern)

