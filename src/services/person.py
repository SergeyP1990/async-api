from functools import lru_cache
from typing import Optional, List, Dict

import orjson
from fastapi import Depends

from db.abstract_cache import BaseCacheStorage
from db.abstract_search_engine import BaseSearchEngine
from db.cache import get_cache
from db.search_engine import get_search_engine
from models.film import FilmSmall
from models.person import Person
from services.cache_key_generator import generate_key

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, cache: BaseCacheStorage, se: BaseSearchEngine):
        self.cache_service = cache
        self.se = se

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        key = generate_key("movies", {"by_id": person_id})
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_db(person_id)
            if not person:
                return None
            await self._put_person_to_cache(key, person)

        return person

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
        persons = await self._person_search_from_cache(key)
        if not persons:
            persons = await self._search_person_from_db(body)
            await self._put_search_person_to_cache(key, persons)
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
        films = await self._films_by_person_from_cache(key)
        if not films:
            films = await self._get_films_from_db(body)
            await self._put_films_by_person_to_cache(key, films)
        return films

    async def _get_person_from_db(self, person_id):
        doc = await self.se.get(scope="persons", record_id=person_id)
        if doc is None:
            return None
        return Person(**doc)

    async def _person_from_cache(self, person_id):
        data = await self.cache_service.read(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _person_search_from_cache(self, key):
        data = await self.cache_service.read(key)
        if not data:
            return None
        persons = [Person.parse_raw(_data) for _data in orjson.loads(data)]
        return persons

    async def _films_by_person_from_cache(self, key):
        data = await self.cache_service.read(key)
        if not data:
            return None
        films = [FilmSmall.parse_raw(_data) for _data in orjson.loads(data)]
        return films

    async def _put_person_to_cache(self, key, person):
        await self.cache_service.write(key, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_search_person_to_cache(self, key, persons):
        await self.cache_service.write(key, orjson.dumps(persons, default=Person.json), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_by_person_to_cache(self, key, films):
        await self.cache_service.write(key, orjson.dumps(films, default=FilmSmall.json), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _search_person_from_db(self, body: Dict):
        doc = await self.se.search(scope="persons", search_query=body)
        persons = [Person(**x) for x in doc]
        return persons

    async def _get_films_from_db(self, body):
        doc = await self.se.search(scope='movies', search_query=body)
        films = [FilmSmall(**x) for x in doc]
        return films


@lru_cache()
def get_person_service(
        cache: BaseCacheStorage = Depends(get_cache),
        search_engine: BaseSearchEngine = Depends(get_search_engine),
) -> PersonService:
    return PersonService(cache, search_engine)
