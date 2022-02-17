from abstract_cache import BaseCacheStorage
from redis import RedisCache

cache = RedisCache()


# Функция понадобится при внедрении зависимостей
async def get_cache() -> BaseCacheStorage:
    return cache
