from functools import lru_cache
from typing import Optional, List, Dict

from fastapi import Depends
from orjson import loads as orjson_loads

from db.abstract_cache import BaseCacheStorage
from db.abstract_search_engine import BaseSearchEngine
from db.cache import get_cache
from db.search_engine import get_search_engine
from models.base import orjson_dumps
from models.film import Film
from services.cache_key_generator import generate_key

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, cache: BaseCacheStorage, se: BaseSearchEngine):
        self.cache_service = cache
        self.se = se

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
        # Здесь формируется ключ для кеширования запроса в AbstractCache
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
            doc = await self._search_films_from_db(body)
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
            # Если фильма нет в кеше, то ищем его в БД
            film = await self._get_film_from_db(film_id)
            if not film:
                # Если он отсутствует в БД, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(key, film)

        return film

    # Функция возвращает список фильмов по переданному body
    async def _search_films_from_db(self, body: Dict):
        doc = await self.se.search(scope='movies', search_query=body)
        print(doc)
        list_films = [Film(**x) for x in doc]
        return list_films

    # Функция возвращает фильм по переданному ИД
    async def _get_film_from_db(self, film_id: str) -> Optional[Film]:
        doc = await self.se.get(scope='movies', record_id=film_id)
        if doc is None:
            return None
        return Film(**doc)

    # Функция возвращает фильм из кэша
    async def _film_from_cache(self, key: str) -> Optional[Film]:
        data = await self.cache_service.read(key)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    # Функция возвращает список фильмов из кэша
    async def _films_from_cache(self, cache_key) -> Optional[Film]:
        data = await self.cache_service.read(cache_key)
        if not data:
            return None
        obj = [Film.parse_raw(_data) for _data in orjson_loads(data)]
        return obj

    # Функция добавляет фильм в кэш Редис
    async def _put_film_to_cache(self, cache_key, film: Film):
        await self.cache_service.write(
            cache_key,
            film.json(),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )

    # Функция добавляет список фильмов в кэш Редис
    async def _put_films_to_cache(self, cache_key, doc):
        await self.cache_service.write(
            cache_key,
            orjson_dumps(doc, default=Film.json),
            expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        cache: BaseCacheStorage = Depends(get_cache),
        se: BaseSearchEngine = Depends(get_search_engine),
) -> FilmService:
    return FilmService(cache, se)
