import asyncio
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_get_person_data_by_id(make_get_request, expected_json_response):
    response = await make_get_request('person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a')
    assert response.status == HTTPStatus.OK
    assert response.body == expected_json_response


async def test_get_person_films_data_by_id(make_get_request, expected_json_response):
    response = await make_get_request('person/26e83050-29ef-4163-a99d-b546cac208f8/film')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 7
    assert response.body == expected_json_response


async def test_get_person_data_by_unknown_id(make_get_request):
    response = await make_get_request('person/a5a8f573-3cee-4ccc-8a2b-91cb9aaaaaaa')
    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body['detail'] == 'Person not found'


