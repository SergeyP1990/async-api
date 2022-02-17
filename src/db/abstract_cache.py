import abc
from typing import Any, Optional, Callable
from core import config

import aioredis


class BaseCacheStorage:
    # def __init__(self):
    #     self.storage = self.connect()
    #
    # @abc.abstractmethod
    # async def connect(self) -> Callable:
    #     """Подключиться к кэшу"""
    #     pass

    @abc.abstractmethod
    async def read(self, key: str) -> Optional[Any]:
        """Получить данные из кэша по ключу"""
        pass

    @abc.abstractmethod
    async def write(self, key: str, data: Any) -> None:
        """Записать данные по ключу"""
        pass


class RedisCache(BaseCacheStorage):
    def __init__(self):
        self.storage = None

    async def connect(self) -> None:
        self.storage = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)

    async def read(self, key: str) -> Optional[Any]:
        return await self.storage.get(key)

    async def write(self, key: str, data: Any, expire: int = 60*5) -> None:
        await self.storage.set(key, data, expire)

