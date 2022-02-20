from db.abstract_search_engine import BaseSearchEngine
from db.elastic import AsyncElasticEngine

search_engine: BaseSearchEngine = AsyncElasticEngine()


# Функция понадобится при внедрении зависимостей
async def get_search_engine() -> BaseSearchEngine:
    return search_engine
