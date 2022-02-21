from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from services.film import FilmService, get_film_service

from models.film import Film, FilmSmall
from api.v1.error_messages import APIErrors

router = APIRouter()


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}',
            response_model=Film,
            summary="Фильм по ID",
            description="Вывод фильма:"
                        "ID"
                        "::Название фильма"
                        "::Рейтинг IMDB"
                        "::Описание"
                        "::Жанры фильма"
                        "::Список актёров"
                        "::Список сценаристов"
                        "::Режисёры",
            response_description="Полная информация о фильме",
            tags=['Информация по ID']
            )
async def film_details(film_id: str,
                       film_service: FilmService = Depends(get_film_service)
                       ) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=APIErrors.FILM_NOT_FOUND
        )

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать
    return Film(uuid=film.uuid,
                title=film.title,
                imdb_rating=film.imdb_rating,
                description=film.description,
                genre=film.genre,
                actors=film.actors,
                writers=film.writers,
                directors=film.directors)


@router.get('/',
            response_model=List[FilmSmall],
            summary="Список кинопроизведений",
            description="Список всех произведений "
                        "(Пагинация по умолчанию - 50 элементов)",
            response_description="Название и рейтинг фильма",
            tags=['Список кинопроизведений']
            )
async def film_main(
        sort: str = "-imdb_rating",
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        filter_genre: str = Query(None, alias="filter[genre]"),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmSmall]:
    data = await film_service.get_film_pagination(sort,
                                                  page_size,
                                                  page_number,
                                                  filter_genre)
    if data:
        films = [FilmSmall(uuid=film.uuid,
                           title=film.title,
                           imdb_rating=film.imdb_rating
                           ) for film in data]
    else:
        films = None
    return films


@router.get('/search/',
            response_model=List[FilmSmall],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг фильма",
            tags=['Полнотекстовый поиск']
            )
async def film_search(
        query: str,
        page_size: int = Query(50, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_film_service)
) -> List[FilmSmall]:
    data = await film_service.get_film_search(query, page_size, page_number)
    if data:
        films = [FilmSmall(uuid=film.uuid,
                           title=film.title,
                           imdb_rating=film.imdb_rating
                           ) for film in data]
    else:
        films = None
    return films
