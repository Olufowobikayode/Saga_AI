# --- START OF REFACTORED FILE backend/cache.py ---
import redis
import logging
import json
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisTTLCache:
    """
    A robust, shared cache using Redis with a Time-To-Live (TTL) for each entry.
    This ensures that all Celery workers and web server instances share the same
    cache, which is essential for a scalable architecture.
    """
    _instance: Optional[redis.Redis] = None

    def _get_client(self) -> redis.Redis:
        """Establishes a connection to Redis, reusing it as a singleton."""
        if self._instance is None:
            try:
                # Use the same environment variable as Celery for consistency.
                redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
                # decode_responses=True makes the client return strings instead of bytes
                self._instance = redis.from_url(redis_url, decode_responses=True)
                self._instance.ping() # Verify connection
                logger.info(f"Redis cache client connected successfully to {redis_url}.")
            except Exception as e:
                logger.critical(f"Could not connect to Redis for caching. Caching will be disabled. Error: {e}")
                # Return a dummy object that does nothing if connection fails
                # This makes the app resilient even if Redis is down.
                class DummyRedis:
                    def get(self, *args, **kwargs): return None
                    def setex(self, *args, **kwargs): return None
                self._instance = DummyRedis()
        return self._instance

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the Redis cache if it exists.
        The value is deserialized from JSON.
        """
        client = self._get_client()
        try:
            cached_value = client.get(key)
            if cached_value:
                logger.info(f"CACHE HIT for key: {key[:100]}...")
                return json.loads(cached_value)
            else:
                logger.info(f"CACHE MISS for key: {key[:100]}...")
                return None
        except Exception as e:
            logger.error(f"Error getting key '{key[:100]}...' from Redis cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """
        Adds a JSON-serializable item to the Redis cache with a specific TTL.
        """
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            logger.warning("Cache TTL must be a positive integer. Caching skipped.")
            return
            
        client = self._get_client()
        try:
            # Serialize the value to a JSON string before storing
            serialized_value = json.dumps(value, default=str)
            client.setex(name=key, time=ttl_seconds, value=serialized_value)
            logger.info(f"CACHE SET for key: {key[:100]}... (TTL: {ttl_seconds}s)")
        except TypeError as e:
            logger.error(f"Failed to serialize value for caching. Ensure the object is JSON-serializable. Error: {e}")
        except Exception as e:
            logger.error(f"Error setting key '{key[:100]}...' in Redis cache: {e}")


# --- Global Cache Instance ---
# This single, global instance will be imported by any module needing caching.
seer_cache = RedisTTLCache()

def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """
    Creates a consistent, unique cache key from function arguments.
    (This function remains unchanged as its logic is sound).
    """
    # Sort kwargs to ensure consistent key order
    sorted_kwargs = sorted(kwargs.items())
    return f"{args}:{sorted_kwargs}"
# --- END OF REFACTORED FILE backend/cache.py ---