from functools import lru_cache
from typing import Optional, List, Dict
from uuid import UUID

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person = await self._person_from_cache(person_id)
        if not person:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            person = await self._get_person_from_elastic(person_id)
            if not person:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
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
        doc = await self._search_person_from_elastic(body)
        return doc

    async def get_films_by_person(self, person_id):
        body = {
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
        doc = await self._get_films_from_elastic(body)
        return doc

    async def _get_person_from_elastic(self, person_id):
        doc = await self.elastic.get(index="persons", id=person_id)
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id):
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person):
        await self.redis.set(person.uuid, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _search_person_from_elastic(self, body: Dict):
        doc = await self.elastic.search(index="persons", body=body)
        persons = [Person(**x['_source']) for x in doc['hits']['hits']]
        return persons

    async def _get_films_from_elastic(self, body):
        doc = await self.elastic.search(index='movies', body=body)
        films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return films


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
