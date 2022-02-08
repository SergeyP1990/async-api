from functools import lru_cache
from typing import Optional, List, Dict

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import FilmSmall

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

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
        key = f"person_search:{query}:{str(page_size)}:{str(page_number)}"
        persons = await self._person_search_from_cache(key)
        if not persons:
            persons = await self._search_person_from_elastic(body)
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
        key = f"films_by_person:{person_id}"
        films = await self._films_by_person_from_cache(key)
        if not films:
            films = await self._get_films_from_elastic(body)
            await self._put_films_by_person_to_cache(key, films)
        return films

    async def _get_person_from_elastic(self, person_id):
        doc = await self.elastic.get(index="persons", id=person_id)
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id):
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _person_search_from_cache(self, key):
        data = await self.redis.get(key)
        if not data:
            return None
        persons = [Person.parse_raw(_data) for _data in orjson.loads(data)]
        return persons

    async def _films_by_person_from_cache(self, key):
        data = await self.redis.get(key)
        if not data:
            return None
        films = [FilmSmall.parse_raw(_data) for _data in orjson.loads(data)]
        return films

    async def _put_person_to_cache(self, person):
        await self.redis.set(person.uuid, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_search_person_to_cache(self, key, persons):
        await self.redis.set(key, orjson.dumps(persons, default=Person.json), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_by_person_to_cache(self, key, films):
        await self.redis.set(key, orjson.dumps(films, default=FilmSmall.json), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _search_person_from_elastic(self, body: Dict):
        doc = await self.elastic.search(index="persons", body=body)
        persons = [Person(**x['_source']) for x in doc['hits']['hits']]
        return persons

    async def _get_films_from_elastic(self, body):
        doc = await self.elastic.search(index='movies', body=body)
        films = [FilmSmall(**x['_source']) for x in doc['hits']['hits']]
        return films


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
