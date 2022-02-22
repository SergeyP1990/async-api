from functools import lru_cache
from typing import Optional, List

from fastapi import Depends

from core.abstractions import BaseCacheStorage, BaseSearchEngine, BaseService
from db.cache import get_cache
from db.search_engine import get_search_engine
from models.film import FilmSmall
from models.person import Person
from services.cache_key_generator import generate_key

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService(BaseService):

    async def get_person_by_id(self, person_id: str) -> Optional[Person]:
        key = generate_key("persons", {"by_id": person_id})
        return await self.get_by_id(person_id, Person, key=key)

    async def get_person_search(self, query: str, page_size: int, page_number: int) -> List[Person]:
        body = {
            "size": page_size,
            "from": (page_number - 1) * page_size,
            "query": {
                "match": {
                    "full_name": {
                        "query": query,
                        "fuzziness": "auto"
                    }
                }
            }
        }
        params = {
            "method": "person_search",
            "query": query,
            "page_size": page_size,
            "page_number": page_number,
        }
        key = generate_key("persons", params)
        persons = await self.search_data(body, Person, key=key)
        return persons

    async def get_films_by_person(self, person_id):
        body = {
            "size": 100,
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "bool": {
                                        "filter": [{"term": {"actors.uuid": person_id}}]
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "bool": {
                                        "filter": [{"term": {"writers.uuid": person_id}}]
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "directors",
                                "query": {
                                    "bool": {
                                        "filter": [
                                            {"term": {"directors.uuid": person_id}}]
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
        params = {
            "method": "films_by_person",
            "person_id": person_id,
        }
        key = generate_key("persons", params)

        films = await self.search_data(body, FilmSmall, key=key)
        return films


@lru_cache()
def get_person_service(
        cache: BaseCacheStorage = Depends(get_cache),
        search_engine: BaseSearchEngine = Depends(get_search_engine),
) -> PersonService:
    return PersonService(search_engine, cache, expire=PERSON_CACHE_EXPIRE_IN_SECONDS)
