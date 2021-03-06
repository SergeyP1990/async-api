from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from services.genre import GenreService, get_genre_service
from models.genre import Genre
from api.v1.error_messages import APIErrors

router = APIRouter()


# Внедряем GenreService с помощью Depends(get_genre_service)
@router.get("/{genre_id}",
            response_model=Genre,
            summary="Жанр по ID",
            description="Вывод жанра:"
                        "ID"
                        "::Наименование жанра",
            response_description="Информация по жанру",
            tags=['Информация по ID']
            )
async def genre_details(genre_id: str,
                        genre_service: GenreService = Depends(get_genre_service)
                        ) -> Genre:
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=APIErrors.GENRE_NOT_FOUND
        )
    return genre


@router.get('/',
            response_model=List[Genre],
            summary="Список жанров",
            description="Список всех жанров",
            response_description="Название и рейтинг жанра",
            tags=['Список жанров']
            )
async def genres(genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres_data = await genre_service.get_genres()
    return genres_data

