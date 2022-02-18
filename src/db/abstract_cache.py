import abc
from typing import Any, Optional


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
