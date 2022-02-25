import asyncio
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_get_films_data_default(make_get_request, expected_json_response):
    response = await make_get_request('film/')
    assert response.status == HTTPStatus.OK
    assert response.body == expected_json_response


async def test_get_all_films_data(make_get_request, expected_json_response):
    response = await make_get_request('film/?page[size]=1000')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 100
    assert response.body == expected_json_response


async def test_get_films_data_by_filter_comedy_and_sort_asc(make_get_request, expected_json_response):
    response = await make_get_request('film/?sort=imdb_rating&filter[genre]=comedy')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 18
    assert response.body == expected_json_response


async def test_get_film_data_by_id_1(make_get_request, expected_json_response):
    response = await make_get_request('film/2a090dde-f688-46fe-a9f4-b781a985275e')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 8
    assert response.body == expected_json_response


async def test_get_film_data_by_id_2(make_get_request, expected_json_response):
    response = await make_get_request('film/935e418d-09f3-4de4-8ce3-c31f31580b12')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 8
    assert response.body == expected_json_response


async def test_get_film_data_by_unknown_id(make_get_request):
    response = await make_get_request('film/ead9b449-734b-4878-86f1-1e4c96a28bba')
    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body['detail'] == 'Film not found'
