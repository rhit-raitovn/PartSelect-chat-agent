"""
Cache Service using in-memory cache (can be extended to Redis)
"""
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib


class CacheService:
    """Simple in-memory cache service"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = {}  # Time-to-live tracking
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check if key exists and hasn't expired
        if key in self.cache:
            if key in self.ttl and datetime.now() > self.ttl[key]:
                # Expired, delete it
                del self.cache[key]
                del self.ttl[key]
                return None
            return self.cache[key]
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 3600
    ):
        """Set value in cache with TTL"""
        self.cache[key] = value
        if ttl_seconds:
            self.ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.ttl:
            del self.ttl[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.ttl.clear()
    
    def cache_response(self, prefix: str):
        """Decorator for caching function responses"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Generate cache key from function args
                cache_key = self._generate_key(prefix, (args, kwargs))
                
                # Try to get from cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Call function and cache result
                result = await func(*args, **kwargs)
                self.set(cache_key, result)
                return result
            return wrapper
        return decorator


# Singleton instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get or create Cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service