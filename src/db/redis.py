from typing import Optional, Any
from aioredis import Redis, create_redis_pool
from abstract_cache import BaseCacheStorage
from core import config


class RedisCache(BaseCacheStorage):
    def __init__(self):
        self.storage: Optional[Redis] = None

    async def connect(self) -> None:
        self.storage = await create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)

    async def read(self, key: str) -> Optional[Any]:
        return await self.storage.get(key)

    async def write(self, key: str, data: Any, expire: int = 60*5) -> None:
        await self.storage.set(key=key, value=data, expire=expire)

