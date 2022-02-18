import abc
from typing import Optional, Any, List


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
    async def get(self, *args, **kwargs) -> Optional[Any]:
        """Выполнить запрос к движку по конкретному id"""
        pass

    @abc.abstractmethod
    async def search(self, *args, **kwargs) -> Optional[List[Any]]:
        """Выполнить запрос на поиск элементов к движку"""
        pass



#
# a = AsyncElasticSearch()
# a.get('index', 'data')
