import asyncio
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_get_genre_data_default(make_get_request, expected_json_response):
    response = await make_get_request('genre/')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 26
    assert response.body == expected_json_response


async def test_get_genre_data_by_id_1(make_get_request, expected_json_response):
    response = await make_get_request('genre/f39d7b6d-aef2-40b1-aaf0-cf05e7048011')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2
    assert response.body == expected_json_response


async def test_get_genre_data_by_id_2(make_get_request, expected_json_response):
    response = await make_get_request('genre/63c24835-34d3-4279-8d81-3c5f4ddb0cdc')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2
    assert response.body == expected_json_response


async def test_get_genre_data_by_unknown_id(make_get_request):
    response = await make_get_request('genre/f39d7b6d-aef2-40b1-aaf0-cf05432gv43g4')
    assert response.status == HTTPStatus.NOT_FOUND
    assert len(response.body) == 1
    assert response.body['detail'] == 'Genre not found'

