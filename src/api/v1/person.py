from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import Person
from services.person import PersonService, get_person_service, FilmSmall
from api.v1.error_messages import APIErrors

router = APIRouter()


@router.get("/{person_id}",
            response_model=Person,
            summary="Персонаж по ID",
            description="Информация о персонаже:"
                        "ID"
                        "::Полное имя"
                        "::Список ролей в различных кинопроизведениях"
                        "::Список ID фильмов с участием персонажа",
            response_description="Полная информация о персонаже",
            tags=['Информация по ID'])
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)
                         ) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=APIErrors.PERSON_NOT_FOUND
        )
    return person


@router.get('/search/',
            response_model=List[Person],
            summary="Поиск персонажей",
            description="Полнотекстовый поиск по персонажам"
                        " (Пагинация по умолчанию - 50 элементов)",
            response_description="Информация о персонажах",
            tags=['Полнотекстовый поиск']
            )
async def person_search(query: str,
                        page_size: int = Query(50, alias="page[size]"),
                        page_number: int = Query(1, alias="page[number]"),
                        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.get_person_search(
        query,
        page_size,
        page_number
    )
    return persons


@router.get('/{person_id}/film',
            response_model=List[FilmSmall],
            summary="Список кинопроизведений по ID персонажа",
            description="Список кинопроизведений определённого персонажа",
            response_description="Полный список фильмов персонажа",
            tags=['Информация по ID']
            )
async def person_search(person_id: str,
                        persons_service: PersonService = Depends(get_person_service)) -> List[FilmSmall]:
    data = await persons_service.get_films_by_person(person_id)
    if not data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=APIErrors.PERSON_NOT_FOUND
        )
    return data
