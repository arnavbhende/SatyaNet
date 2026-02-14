"""
Cache Manager for API responses and model outputs
"""
import time
import hashlib
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl  # TTL in seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            item = self.cache[key]
            if time.time() < item['expires']:
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return item['value']
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:8]}...")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set item in cache"""
        # Remove oldest items if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                          key=lambda k: self.cache[k]['created'])
            del self.cache[oldest_key]
            logger.debug(f"Cache full, removed oldest key: {oldest_key[:8]}...")
        
        expires = time.time() + (ttl or self.default_ttl)
        self.cache[key] = {
            'value': value,
            'expires': expires,
            'created': time.time()
        }
        logger.debug(f"Cached value for key: {key[:8]}...")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        expired_count = sum(1 for item in self.cache.values() 
                           if current_time >= item['expires'])
        
        return {
            "total_items": len(self.cache),
            "expired_items": expired_count,
            "max_size": self.max_size,
            "utilization": len(self.cache) / self.max_size * 100
        }

# Global cache instance
cache_manager = CacheManager()
