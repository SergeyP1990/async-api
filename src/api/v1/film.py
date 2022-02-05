from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float = None


class FilmDetail(Film):
    description: str = None
    genre: List[dict] = None
    actors: List[dict] = None
    writers: List[dict] = None
    directors: List[dict] = None


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=FilmDetail)
async def film_details(film_id: str,
                       film_service: FilmService = Depends(get_film_service)
                       ) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
        # Которое отсутствует в модели ответа API.
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны
        # и, возможно, данные, которые опасно возвращать
    return FilmDetail(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating, description=film.description,
                      genre=film.genre, actors=film.actors, writers=film.writers, directors=film.directors)


@router.get('/')
async def film_main(
        sort: str = "-imdb_rating",
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        filter_genre: str = Query(None, alias="filter[genre]"),
        film_service: FilmService = Depends(get_film_service)
        ) -> List[Film]:
    data = await film_service.get_film_pagination(sort, page_size, page_number, filter_genre)
    films = [Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in data]
    return films


@router.get('/search/')
async def film_search(
        query: str,
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_film_service)
        ) -> List[Film]:
    data = await film_service.get_film_search(query, page_size, page_number)
    films = [Film(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in data]
    return films
