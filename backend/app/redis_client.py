import redis.asyncio as aioredis
from app.config import get_settings
from functools import lru_cache

_redis_client = None

async def get_redis():
    global _redis_client
    if not _redis_client:
        settings = get_settings()
        _redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    return _redis_client
