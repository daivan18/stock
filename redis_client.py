# redis_client.py

import redis
import os

# Redis 預設為本機開發環境 redis://localhost:6379
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_cache(key: str, value: str, ttl: int = 300):
    r.set(key, value, ex=ttl)

def get_cache(key: str):
    return r.get(key)
