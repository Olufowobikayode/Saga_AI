import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SimpleTTLCache:
    """
    A simple in-memory cache with a Time-To-Live (TTL) for each entry.
    This is used to store the results of expensive scraping operations to
    reduce the risk of IP blocks and improve application performance.
    """
    _cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves an item from the cache if it exists and has not expired.

        Args:
            key: The key for the cached item.

        Returns:
            The cached data if valid, otherwise None.
        """
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires_at']:
                logger.info(f"CACHE HIT for key: {key[:100]}...")
                return entry['value']
            else:
                # Entry has expired, remove it
                logger.info(f"CACHE EXPIRED for key: {key[:100]}...")
                del self._cache[key]
        
        logger.info(f"CACHE MISS for key: {key[:100]}...")
        return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        """
        Adds an item to the cache with a specific Time-To-Live.

        Args:
            key: The key for the item to be cached.
            value: The data to be cached.
            ttl_seconds: The number of seconds the cache entry should be valid for.
        """
        if not isinstance(ttl_seconds, int) or ttl_seconds <= 0:
            logger.warning("Cache TTL must be a positive integer. Caching skipped.")
            return
            
        expires_at = time.time() + ttl_seconds
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        logger.info(f"CACHE SET for key: {key[:100]}... (TTL: {ttl_seconds}s)")

# --- Global Cache Instance ---
# We create a single, global instance of the cache that can be imported
# and used by any of the "Seer" modules throughout the application.
seer_cache = SimpleTTLCache()

def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """
    Creates a consistent, unique cache key from function arguments.
    This ensures that the same function call with the same arguments
    will always produce the same cache key.
    """
    # Sort kwargs to ensure consistent key order
    sorted_kwargs = sorted(kwargs.items())
    return f"{args}:{sorted_kwargs}"