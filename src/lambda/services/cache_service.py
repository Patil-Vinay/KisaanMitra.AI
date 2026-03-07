"""
Cache Service - In-memory caching for frequently accessed data
Reduces API calls and improves response times
"""
import time
import json
from datetime import datetime, timedelta


class CacheService:
    """In-memory cache with TTL support for Lambda functions"""
    
    _cache = {}
    _cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    @classmethod
    def get(cls, key, default=None):
        """Get value from cache with TTL check"""
        if not key:
            return default
            
        try:
            if key in cls._cache:
                entry = cls._cache[key]
                
                # Check if expired
                if entry["expires_at"] > time.time():
                    cls._cache_stats["hits"] += 1
                    print(f"[CACHE] HIT: {key}")
                    return entry["value"]
                else:
                    # Expired, remove from cache
                    del cls._cache[key]
                    cls._cache_stats["evictions"] += 1
                    print(f"[CACHE] EXPIRED: {key}")
            
            cls._cache_stats["misses"] += 1
            print(f"[CACHE] MISS: {key}")
            return default
            
        except Exception as e:
            print(f"[CACHE ERROR] Get failed for {key}: {e}")
            return default
    
    @classmethod
    def set(cls, key, value, ttl_seconds=300):
        """Set value in cache with TTL (default 5 minutes)"""
        if not key:
            return False
            
        try:
            # Prevent cache from growing too large (memory management)
            if len(cls._cache) > 100:
                cls._cleanup_expired()
                
                # If still too large, remove oldest entries
                if len(cls._cache) > 100:
                    oldest_keys = sorted(
                        cls._cache.keys(), 
                        key=lambda k: cls._cache[k]["created_at"]
                    )[:20]
                    
                    for old_key in oldest_keys:
                        del cls._cache[old_key]
                        cls._cache_stats["evictions"] += 1
            
            cls._cache[key] = {
                "value": value,
                "created_at": time.time(),
                "expires_at": time.time() + ttl_seconds
            }
            
            print(f"[CACHE] SET: {key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            print(f"[CACHE ERROR] Set failed for {key}: {e}")
            return False
    
    @classmethod
    def delete(cls, key):
        """Delete specific key from cache"""
        try:
            if key in cls._cache:
                del cls._cache[key]
                print(f"[CACHE] DELETED: {key}")
                return True
            return False
        except Exception as e:
            print(f"[CACHE ERROR] Delete failed for {key}: {e}")
            return False
    
    @classmethod
    def clear(cls):
        """Clear entire cache"""
        try:
            cls._cache.clear()
            cls._cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
            print(f"[CACHE] CLEARED")
        except Exception as e:
            print(f"[CACHE ERROR] Clear failed: {e}")
    
    @classmethod
    def _cleanup_expired(cls):
        """Remove expired entries from cache"""
        try:
            current_time = time.time()
            expired_keys = [
                key for key, entry in cls._cache.items()
                if entry["expires_at"] <= current_time
            ]
            
            for key in expired_keys:
                del cls._cache[key]
                cls._cache_stats["evictions"] += 1
            
            if expired_keys:
                print(f"[CACHE] Cleaned up {len(expired_keys)} expired entries")
                
        except Exception as e:
            print(f"[CACHE ERROR] Cleanup failed: {e}")
    
    @classmethod
    def get_stats(cls):
        """Get cache statistics"""
        total_requests = cls._cache_stats["hits"] + cls._cache_stats["misses"]
        hit_rate = (cls._cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "entries": len(cls._cache),
            "hits": cls._cache_stats["hits"],
            "misses": cls._cache_stats["misses"],
            "evictions": cls._cache_stats["evictions"],
            "hit_rate": round(hit_rate, 2)
        }
    
    @classmethod
    def get_market_data_key(cls, crop_name, state):
        """Generate cache key for market data"""
        return f"market_data:{crop_name.lower()}:{state.lower()}"
    
    @classmethod
    def get_ai_response_key(cls, prompt_hash):
        """Generate cache key for AI responses"""
        return f"ai_response:{prompt_hash}"
    
    @classmethod
    def get_forecast_key(cls, crop_name, state):
        """Generate cache key for price forecasts"""
        return f"forecast:{crop_name.lower()}:{state.lower()}"


class RateLimiter:
    """Rate limiting for API calls and user requests"""
    
    _rate_limits = {}
    
    @classmethod
    def is_allowed(cls, key, max_requests=10, window_seconds=60):
        """Check if request is allowed within rate limit"""
        try:
            current_time = time.time()
            
            if key not in cls._rate_limits:
                cls._rate_limits[key] = []
            
            # Clean up old requests outside the window
            cls._rate_limits[key] = [
                req_time for req_time in cls._rate_limits[key]
                if current_time - req_time < window_seconds
            ]
            
            # Check if under limit
            if len(cls._rate_limits[key]) < max_requests:
                cls._rate_limits[key].append(current_time)
                return True
            else:
                print(f"[RATE LIMIT] Blocked: {key} ({len(cls._rate_limits[key])}/{max_requests})")
                return False
                
        except Exception as e:
            print(f"[RATE LIMIT ERROR] {e}")
            return True  # Allow on error to avoid blocking users
    
    @classmethod
    def get_user_key(cls, user_id, action="general"):
        """Generate rate limit key for user actions"""
        return f"user:{user_id}:{action}"
    
    @classmethod
    def get_api_key(cls, api_name):
        """Generate rate limit key for API calls"""
        return f"api:{api_name}"