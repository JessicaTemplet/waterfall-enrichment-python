import os
import redis

# Override via env var for a non-local Redis (auth, TLS via rediss://, etc.).
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

def get_redis_client() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)
