from typing import Optional, List, Any
from elasticsearch import AsyncElasticsearch

from db.abstract_search_engine import BaseSearchEngine
from core import config


class AsyncElasticSearch(BaseSearchEngine):
    def __init__(self):
        self.search_engine: Optional[AsyncElasticsearch] = None

    async def connect(self) -> None:
        self.search_engine = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])

    async def close(self) -> None:
        await self.search_engine.close()

    async def search(self, query) -> Optional[List[Any]]:
        pass

    async def get(self, index, record_id) -> Optional[Any]:
        return None
