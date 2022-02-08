from functools import lru_cache
from typing import Optional, List, Dict

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from models.base import orjson_dumps
from orjson import loads as orjson_loads
from services.cache_key_generator import generate_key

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # Функция подготовки body для поиска по фильмам с пагинацией
    async def get_film_search(
            self,
            query: str,
            page_size: int,
            page_number: int) -> List[Film]:
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'query': {
                'simple_query_string': {
                    "query": query,
                    "fields": ["title^3", "description"],
                    "default_operator": "or"
                }
            }
        }
        # Здесь формируется ключ для кеширования запроса в Redis
        params = {
            "method": "films_search",
            "query": query,
            "page_size": page_size,
            "page_number": page_number,
        }
        key = generate_key("movies", params)
        doc = await self._get_films_through_cache(key, body)
        return doc

    async def _get_films_through_cache(self, key, body):
        doc = await self._films_from_cache(key)
        if not doc:
            doc = await self._search_films_from_elastic(body)
            if not doc:
                return None
            await self._put_films_to_cache(key, doc)
        return doc

    # Функция подготовки body для получения отсортированных фильмов
    #        по рейтингу с возможностью фильтрации по жанрам (с пагинацией)
    async def get_film_pagination(self,
                                  sort: str,
                                  page_size: int,
                                  page_number: int,
                                  filter_genre: str
                                  ) -> List[Film]:
        order_value = 'asc'
        if sort.startswith('-'):
            sort = sort[1:]
            order_value = 'desc'
        body = {
            'size': page_size,
            'from': (page_number - 1) * page_size,
            'sort': {
                sort: {
                    'order': order_value
                }
            }
        }
        if filter_genre:
            body['query'] = {
                'bool': {
                    'filter': {
                        'nested': {
                            'path': 'genre',
                            'query': {
                                'bool': {
                                    'must': {
                                        'match': {'genre.name': filter_genre}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        # Здесь формируется ключ для кеширования запроса в Redis
        params = {
            "method": "films",
            "sort_by": sort,
            "order": order_value,
            "page_size": page_size,
            "page_number": page_number,
            "filter_by": filter_genre
        }
        key = generate_key("movies", params)
        doc = await self._get_films_through_cache(key, body)
        return doc

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        key = generate_key("movies", {"by_id": film_id})
        film = await self._film_from_cache(key)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(key, film)

        return film

    # Функция возвращает список фильмов по переданному body
    async def _search_films_from_elastic(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body)
        list_films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return list_films

    # Функция возвращает фильм по переданному ИД
    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get('movies', film_id, ignore=[404])
        if doc.get('_source') is None:
            return None
        return Film(**doc['_source'])

    # Функция возвращает фильм из кэша
    async def _film_from_cache(self, key: str) -> Optional[Film]:
        data = await self.redis.get(key)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    # Функция возвращает список фильмов из кэша
    async def _films_from_cache(self, redis_key) -> Optional[Film]:
        data = await self.redis.get(redis_key)
        if not data:
            return None
        obj = [Film.parse_raw(_data) for _data in orjson_loads(data)]
        return obj

    # Функция добавляет фильм в кэш Редис
    async def _put_film_to_cache(self, redis_key, film: Film):
        await self.redis.set(
            redis_key,
            film.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    # Функция добавляет список фильмов в кэш Редис
    async def _put_films_to_cache(self, redis_key, doc):
        await self.redis.set(
            redis_key,
            orjson_dumps(doc, default=Film.json),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
