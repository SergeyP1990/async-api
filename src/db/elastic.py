from typing import Optional, List, Any
from elasticsearch import AsyncElasticsearch

from core.abstractions import BaseSearchEngine
from core import config


class AsyncElasticEngine(BaseSearchEngine):
    def __init__(self):
        self.search_engine: Optional[AsyncElasticsearch] = None

    async def connect(self) -> None:
        self.search_engine = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
        if not await self.search_engine.ping():
            raise ValueError(f"Error connecting to {config.ELASTIC_HOST}:{config.ELASTIC_PORT}")

    async def close(self) -> None:
        await self.search_engine.close()

    async def get(self, record_id, scope) -> Optional[Any]:
        data = await self.search_engine.get(index=scope, id=record_id, ignore=[404])
        if data.get("_source") is None:
            return None
        return data["_source"]

    async def search(self, search_query, scope) -> Optional[List[Any]]:
        raw_data = await self.search_engine.search(index=scope, body=search_query)
        data = [src["_source"] for src in raw_data["hits"]["hits"]]
        return data
