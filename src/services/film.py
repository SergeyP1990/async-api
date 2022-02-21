from functools import lru_cache
from typing import Optional, List, Dict

from fastapi import Depends

from core.abstractions import BaseCacheStorage, BaseSearchEngine, BaseService
from db.cache import get_cache
from db.search_engine import get_search_engine
from models.film import Film
from services.cache_key_generator import generate_key

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService(BaseService):

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
        doc = await self.search_data(body, Film, key)
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
        doc = await self.search_data(body, Film, key)
        return doc

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        key = generate_key("movies", {"by_id": film_id})
        return await self.get_by_id(film_id, Film, key=key)


@lru_cache()
def get_film_service(
        cache: BaseCacheStorage = Depends(get_cache),
        se: BaseSearchEngine = Depends(get_search_engine),
) -> FilmService:
    return FilmService(se, cache, expire=FILM_CACHE_EXPIRE_IN_SECONDS)
