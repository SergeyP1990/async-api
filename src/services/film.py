from functools import lru_cache
from typing import Optional, List, Dict

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # Функция подготовки body для поиска по фильмам с пагинацией
    async def get_film_search(self, query: str, page_size: int, page_number: int) -> List[Film]:
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
        doc = await self._search_films_from_elastic(body)
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
        doc = await self._search_films_from_elastic(body)
        return doc

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    # Функция возвращает список фильмов по переданному body
    async def _search_films_from_elastic(self, body: Dict):
        doc = await self.elastic.search(index='movies', body=body)
        list_films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return list_films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get('movies', film_id)
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.uuid, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
