from datetime import datetime, timedelta
from typing import Dict, Optional
import redis
import hashlib
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter with multiple strategies"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
    def check_rate_limit(
        self, 
        identifier: str, 
        max_requests: int, 
        window_seconds: int,
        key_prefix: str = "rate_limit"
    ) -> Dict:
        """
        Check if request is within rate limit
        
        Returns:
            dict with 'allowed', 'remaining', 'reset_at'
        """
        key = f"{key_prefix}:{identifier}"
        current_time = datetime.now()
        window_start = current_time - timedelta(seconds=window_seconds)
        
        try:
            # Remove old entries
            self.redis_client.zremrangebyscore(
                key, 
                '-inf', 
                window_start.timestamp()
            )
            
            # Count current requests
            current_count = self.redis_client.zcard(key)
            
            if current_count < max_requests:
                # Add current request
                self.redis_client.zadd(
                    key, 
                    {str(current_time.timestamp()): current_time.timestamp()}
                )
                self.redis_client.expire(key, window_seconds)
                
                return {
                    'allowed': True,
                    'remaining': max_requests - current_count - 1,
                    'reset_at': (current_time + timedelta(seconds=window_seconds)).isoformat(),
                    'limit': max_requests
                }
            else:
                # Get oldest request time for reset calculation
                oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_time = datetime.fromtimestamp(oldest[0][1]) + timedelta(seconds=window_seconds)
                else:
                    reset_time = current_time + timedelta(seconds=window_seconds)
                
                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset_at': reset_time.isoformat(),
                    'limit': max_requests
                }
                
        except redis.RedisError as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return {
                'allowed': True,
                'remaining': max_requests,
                'reset_at': current_time.isoformat(),
                'limit': max_requests,
                'error': 'Rate limiter unavailable'
            }
    
    def check_user_rate_limit(self, user_id: str, max_requests: int = 60, window: int = 60) -> Dict:
        """Check rate limit for specific user"""
        return self.check_rate_limit(user_id, max_requests, window, "user_limit")
    
    def check_ip_rate_limit(self, ip_address: str, max_requests: int = 100, window: int = 60) -> Dict:
        """Check rate limit for IP address"""
        # Hash IP for privacy
        ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
        return self.check_rate_limit(ip_hash, max_requests, window, "ip_limit")
    
    def check_api_key_rate_limit(self, api_key: str, max_requests: int = 1000, window: int = 3600) -> Dict:
        """Check rate limit for API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return self.check_rate_limit(key_hash, max_requests, window, "api_key_limit")
