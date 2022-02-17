from functools import lru_cache
from typing import Optional, List, Dict

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_cache
from models.genre import Genre
from services.cache_key_generator import generate_key

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(self) -> List[Genre]:
        body = {
            "query": {
                "match_all": {},
            }
        }
        params = {
            "method": "all_genres",
        }
        key = generate_key("genres", params)
        genres = await self._genres_from_cache(key)
        if not genres:
            genres = await self._get_genres_from_elastic(body)
            await self._put_genres_to_cache(key, genres)
        return genres

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        key = generate_key("genres", {"by_id": genre_id})
        genre = await self._genre_from_cache(key)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(key, genre)

        return genre

    # Функция возвращает список жанров по переданному body
    async def _get_genres_from_elastic(self, body: Dict) -> List[Genre]:
        doc = await self.elastic.search(index='genres', body=body)
        list_genres = [Genre(**x['_source']) for x in doc['hits']['hits']]
        return list_genres

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get(index="genres", id=genre_id, ignore=[404])
        if doc.get('_source') is None:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, key: str) -> Optional[Genre]:
        data = await self.redis.get(key)
        if not data:
            return None
        # pydantic предоставляет удобное API для создания объекта моделей из json
        genre = Genre.parse_raw(data)
        return genre

    async def _genres_from_cache(self, key: str) -> Optional[List[Genre]]:
        data = await self.redis.get(key)
        if not data:
            return None
        genres = [Genre.parse_raw(_data) for _data in orjson.loads(data)]
        return genres

    async def _put_genre_to_cache(self, key, genre: Genre) -> None:
        await self.redis.set(key, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genres_to_cache(self, key, genres) -> None:
        await self.redis.set(key, orjson.dumps(genres, default=Genre.json), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_cache),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
