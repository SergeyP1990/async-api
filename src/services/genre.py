from functools import lru_cache
from typing import Optional, List

from fastapi import Depends

from core.abstractions import BaseCacheStorage, BaseSearchEngine, BaseService
from db.cache import get_cache
from db.search_engine import get_search_engine
from models.genre import Genre
from services.cache_key_generator import generate_key

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService(BaseService):

    async def get_genres(self) -> List[Genre]:
        body = {
            "size": 50,
            "query": {
                "match_all": {},
            }
        }
        params = {
            "method": "all_genres",
        }
        key = generate_key("genres", params)
        return await self.search_data(body, Genre, key=key)

    async def get_genre_by_id(self, genre_id: str) -> Optional[Genre]:
        key = generate_key("genres", {"by_id": genre_id})
        return await self.get_by_id(genre_id, Genre, key=key)


@lru_cache()
def get_genre_service(
        cache: BaseCacheStorage = Depends(get_cache),
        search_engine: BaseSearchEngine = Depends(get_search_engine),
) -> GenreService:
    return GenreService(search_engine, cache, expire=GENRE_CACHE_EXPIRE_IN_SECONDS)
