import abc
from typing import Optional, Any, List, Callable, Type

import pydantic

from models.base import BaseOrjsonModel

from fastapi import Depends


class BaseCacheStorage:
    @abc.abstractmethod
    async def connect(self) -> None:
        """Подключиться к кэшу"""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Закрыть подключение к кэшу"""
        pass

    @abc.abstractmethod
    async def read(self, key: str) -> Optional[Any]:
        """Получить данные из кэша по ключу"""
        pass

    @abc.abstractmethod
    async def write(self, key: str, data: Any, expire: int) -> None:
        """Записать данные по ключу"""
        pass


class BaseSearchEngine:
    @abc.abstractmethod
    async def connect(self) -> None:
        """Открывает подключение к поисковому движку"""
        pass

    @abc.abstractmethod
    async def close(self) -> None:
        """Закрывает подключение к поисковому движку"""
        pass

    @abc.abstractmethod
    async def get(self, record_id: str, scope: str) -> Optional[Any]:
        """Выполнить запрос к движку по конкретному id"""
        pass

    @abc.abstractmethod
    async def search(self, search_query: Any, scope: str) -> Optional[List[Any]]:
        """Выполнить запрос на поиск элементов к движку"""
        pass


class CacheServicePipeLine:
    def __init__(self, cache: BaseCacheStorage, db_search):
        self.cache_service = cache

    async def get_data_from_cache(self, key):
        data = await self.cache_service.read(key)
        if not data:
            return None
        return data

    # async def put_data_to_cache(self):


class BaseService:
    def __init__(self, se: BaseSearchEngine, cache: Optional[BaseCacheStorage] = None, expire: int = 60 * 5):
        self.se = se
        self.cache_service = cache
        self.expire_time = expire

    async def get_by_id(self, data_id: str, model: Type[BaseOrjsonModel], key: str = None) -> Optional[BaseOrjsonModel]:
        if self.cache_service is not None:
            from_cache = await self._get_data_from_cache(key)
            if from_cache is not None:
                return model.parse_raw(from_cache)
        from_db = await self._get_by_id_from_db(data_id, model)
        if from_db is None:
            return None
        if self.cache_service is not None:
            await self._put_data_to_cache(key, from_db)
        return from_db

    async def _get_by_id_from_db(self, data_id: str, model) -> Optional[BaseOrjsonModel]:
        print(f"===== _GET FROM DB")
        doc = await self.se.get(scope=model.table_name, record_id=data_id)
        if doc is None:
            return None
        return model(**doc)

    async def _get_data_from_cache(self, key):
        print(f"===== _GET FROM CACHE")
        data = await self.cache_service.read(key)
        if not data:
            return None
        return data

    async def _put_data_to_cache(self, key, data: BaseOrjsonModel) -> None:
        obj = data.json()
        await self.cache_service.write(key, data.json(), expire=self.expire_time)

    async def search_data(self, query: Any, model: Type[BaseOrjsonModel], key: str = None) -> List[BaseOrjsonModel]:
        if self.cache_service is not None:
            from_cache = await self._get_data_from_cache(key)
            if from_cache is not None:
                return [model.parse_raw(_data) for _data in model.__config__.json_loads(from_cache)]
        print(f"========= SEARCH DATA CALL WITH CACHE")
        from_db = await self._get_object_from_db(query, model)
        if self.cache_service is not None:
            await self._put_objects_to_cache(key, from_db, model)
        return from_db

    async def _get_object_from_db(self, query, model):
        print(f"========= _GET OBJECT_S FROM DB")
        doc = await self.se.search(scope=model.table_name, search_query=query)
        list_object = [model(**x) for x in doc]
        return list_object

    async def _put_objects_to_cache(self, key, data, model):
        # obj = data.json()
        print(f"========= DATA TYPE AFTER JSON {type(data)}")
        await self.cache_service.write(key, model.__config__.json_dumps(data, default=model.json), expire=self.expire_time)

