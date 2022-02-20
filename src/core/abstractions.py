import abc
from typing import Optional, Any, List


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
