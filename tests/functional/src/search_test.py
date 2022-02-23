import pytest
import re


# ==============
# Проверка film
# ==============
# Наличие искомого слова в выдаче
@pytest.mark.asyncio
async def test_film_search_word_inclusion(make_get_request):
    film_query_word = "star"
    response = await make_get_request(f'film/search/?query={film_query_word}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1

    assert response.body[0].get("uuid")
    assert response.body[0].get("title")
    assert re.search('star', response.body[0]['title'], re.IGNORECASE)


# Проверка правильной пагинации
@pytest.mark.asyncio
async def test_film_pagination(make_get_request):
    film_query_word = "star"
    response = await make_get_request(f'film/search/?query={film_query_word}&page[size]=50&page[number]=1')
    assert response.status == 200
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
@pytest.mark.asyncio
async def test_film_full_text_search(make_get_request):
    word = 'Captain'
    damaged_word = 'captrn'

    response = await make_get_request(f'film/search/?query={word}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['title'], re.IGNORECASE)

    response = await make_get_request(f'film/search/?query={damaged_word}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['title'], re.IGNORECASE)


# ==============
# Проверка person
# ==============
# Наличие искомого слова в выдаче
@pytest.mark.asyncio
async def test_person_search_word_inclusion(make_get_request):
    response = await make_get_request('person/search/?query=george&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1

    assert response.body[0].get("uuid")
    assert response.body[0].get("full_name")
    assert response.body[0].get("film_ids")
    assert response.body[0].get("role")
    assert re.search('george', response.body[0]['full_name'], re.IGNORECASE)


# Проверка правильной пагинации
@pytest.mark.asyncio
async def test_person_pagination(make_get_request):
    person_name = 'david'
    response = await make_get_request(f'person/search/?query={person_name}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) == 50

    penultimate_uuid = response.body[24]['uuid']
    last_uuid = response.body[25]['uuid']

    first_half_pages = await make_get_request(f'person/search/?query={person_name}&page[size]=25&page[number]=1')
    second_half_pages = await make_get_request(f'person/search/?query={person_name}&page[size]=25&page[number]=2')

    assert len(first_half_pages.body) == 25
    assert len(second_half_pages.body) >= 1
    assert first_half_pages.body[-1]['uuid'] == penultimate_uuid
    assert second_half_pages.body[0]['uuid'] == last_uuid


# Проверка full text search
@pytest.mark.asyncio
async def test_person_full_text_search(make_get_request):
    word = 'david'
    damaged_word = 'dfdvid'

    response = await make_get_request(f'person/search/?query={word}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['full_name'], re.IGNORECASE)

    response = await make_get_request(f'person/search/?query={damaged_word}&page[size]=50&page[number]=1')
    assert response.status == 200
    assert len(response.body) > 1
    assert re.search(word, response.body[0]['full_name'], re.IGNORECASE)
