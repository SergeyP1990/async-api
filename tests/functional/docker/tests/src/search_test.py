import asyncio
import pytest
import re
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


# ==============
# Проверка film
# ==============
# Наличие искомого слова в выдаче
async def test_film_search_word_inclusion(make_get_request, expected_json_response):
    film_query_word = "star"
    response = await make_get_request(f'film/search/?query={film_query_word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1
    assert response.body == expected_json_response


# Проверка правильной пагинации
async def test_film_pagination(make_get_request):
    film_query_word = "star"
    response = await make_get_request(f'film/search/?query={film_query_word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 50

    penultimate_uuid = response.body[24]['uuid']
    last_uuid = response.body[25]['uuid']

    first_half_pages = await make_get_request(f'film/search/?query={film_query_word}&page[size]=25&page[number]=1')
    second_half_pages = await make_get_request(f'film/search/?query={film_query_word}&page[size]=25&page[number]=2')

    assert len(first_half_pages.body) == 25
    assert len(second_half_pages.body) >= 1
    assert first_half_pages.body[-1]['uuid'] == penultimate_uuid
    assert second_half_pages.body[0]['uuid'] == last_uuid


# Проверка full text search
async def test_film_full_text_search(make_get_request):
    word = 'Knights'
    damaged_word = 'Knighfs'

    response = await make_get_request(f'film/search/?query={word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['title'], re.IGNORECASE)

    response = await make_get_request(f'film/search/?query={damaged_word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['title'], re.IGNORECASE)


# ==============
# Проверка person
# ==============
# Наличие искомого слова в выдаче
async def test_person_search_word_inclusion(make_get_request, expected_json_response):
    response = await make_get_request('person/search/?query=george&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body == expected_json_response


# Проверка full text search
async def test_person_full_text_search(make_get_request):
    word = 'david'
    damaged_word = 'dfdvid'

    response = await make_get_request(f'person/search/?query={word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert re.search(word, response.body[0]['full_name'], re.IGNORECASE)

    response = await make_get_request(f'person/search/?query={damaged_word}&page[size]=50&page[number]=1')
    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert re.search(word, response.body[0]['full_name'], re.IGNORECASE)
