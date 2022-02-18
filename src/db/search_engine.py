from db.abstract_search_engine import BaseSearchEngine
from db.elastic import ...

search_engine: BaseSearchEngine = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es
