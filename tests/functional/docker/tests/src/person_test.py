import pytest


@pytest.mark.asyncio
async def test_get_person_data_by_id(make_get_request):
    response = await make_get_request('person/a5a8f573-3cee-4ccc-8a2b-91cb9f55250a')
    assert response.status == 200
    assert len(response.body) == 4
    assert response.body['uuid'] == 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    assert response.body['full_name'] == 'George Lucas'
    assert len(response.body['role']) == 51
    assert response.body['role'][0] == {
        "role": "actor",
        "uuid": "19babc93-62f5-481a-b6fe-9ebfef689cbc"
    }
    assert response.body['role'][50] == {
      "role": "writer",
      "uuid": "f553752e-71c7-4ea0-b780-41408516d0f4"
    }
    assert len(response.body['film_ids']) == 46


@pytest.mark.asyncio
async def test_get_person_films_data_by_id(make_get_request):
    response = await make_get_request('person/26e83050-29ef-4163-a99d-b546cac208f8/film')
    assert response.status == 200
    assert len(response.body) == 14
    assert response.body[0] == {
        "uuid": "3d825f60-9fff-4dfe-b294-1a45fa1e115d",
        "title": "Star Wars: Episode IV - A New Hope",
        "imdb_rating": 8.6
      }
    assert response.body[13] == {
        "uuid": "943946ed-4a2b-4c71-8e0b-a58a11bd1323",
        "title": "Star Wars: Evolution of the Lightsaber Duel",
        "imdb_rating": 6.8
    }


@pytest.mark.asyncio
async def test_get_person_data_by_unknown_id(make_get_request):
    response = await make_get_request('person/a5a8f573-3cee-4ccc-8a2b-91cb9aaaaaaa')
    assert response.status == 404
    assert len(response.body) == 1
    assert response.body['detail'] == 'Person not found'


