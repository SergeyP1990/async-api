from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from models.person import Person
from services.person import PersonService, get_person_service, FilmSmall

router = APIRouter()


@router.get("/{person_id}", response_model=Person)
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)
                         ) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return person


@router.get('/search/')
async def person_search(query: str,
                        page_size: int = Query(50, alias="page[size]"),
                        page_number: int = Query(1, alias="page[number]"),
                        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.get_person_search(query, page_size, page_number)
    return persons


@router.get('/{person_id}/film')
async def person_search(person_id: str,
                        persons_service: PersonService = Depends(get_person_service)) -> List[FilmSmall]:
    data = await persons_service.get_films_by_person(person_id)
    if not data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return data
