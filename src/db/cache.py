from db.abstract_cache import BaseCacheStorage
from db.redis import RedisCache

cache: BaseCacheStorage = RedisCache()


# Функция понадобится при внедрении зависимостей
async def get_cache() -> BaseCacheStorage:
    return cache
