# analysis-engine/services/redis_manager.py
import redis
import json
import os
from urllib.parse import urlparse

class RedisManager:
    def __init__(self):
        # Fallback order: 
        # 1. Environment variable 'REDIS_URL' (from docker-compose)
        # 2. Internal docker DNS 'redis'
        # 3. Localhost (for local testing)
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        
        try:
            self.client = redis.from_url(
                redis_url, 
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Test connection immediately
            self.client.ping()
            print(f"✅ RedisManager: Successfully connected to {redis_url}")
        except Exception as e:
            print(f"❌ RedisManager: Connection FAILED to {redis_url}. Error: {e}")
            self.client = None

    def save_job(self, job_id, data):
        if not self.client:
            print(f"⚠️ Cannot save job {job_id}: No Redis connection")
            return
        # Set expiry for 24 hours
        self.client.setex(f"job:{job_id}", 86400, json.dumps(data, default=str))

    def get_job(self, job_id):
        if not self.client:
            return None
        data = self.client.get(f"job:{job_id}")
        return json.loads(data) if data else None