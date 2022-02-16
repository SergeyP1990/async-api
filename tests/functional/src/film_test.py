import pytest


@pytest.mark.asyncio
async def test_get_films_data(make_get_request):
    response = await make_get_request('film/')
    print(response.body[0]['imdb_rating'])
    assert response.status == 200
    assert len(response.body) == 50
    assert response.body[0]['imdb_rating'] == 9.6
    assert response.body[49]['title'] == 'Wishes on a Falling Star'


@pytest.mark.asyncio
async def test_get_films_data_by_filter_comedy_and_sort_asc(make_get_request):
    response = await make_get_request('film/?sort=imdb_rating&filter[genre]=comedy')
    print(response.body[0]['imdb_rating'])
    assert response.status == 200
    assert len(response.body) == 50
    assert response.body[0]['imdb_rating'] == 1.8
    assert response.body[49]['title'] == 'Pick a Star'


@pytest.mark.asyncio
async def test_get_film_data_by_id(make_get_request):
    response = await make_get_request('film/2a090dde-f688-46fe-a9f4-b781a985275e')
    assert response.status == 200
    assert len(response.body) == 8
    assert response.body['uuid'] == '2a090dde-f688-46fe-a9f4-b781a985275e'
    assert response.body['title'] == 'Star Wars: Knights of the Old Republic'
    assert response.body['imdb_rating'] == 9.6
    assert response.body['description'] == 'Four thousand years before the' \
                                           ' fall of the Republic, before the' \
                                           ' fall of the Jedi, a great war was' \
                                           ' fought, between the armies of the' \
                                           ' Sith and the forces of the' \
                                           ' Republic. A warrior is chosen' \
                                           ' to rescue a Jedi with a power' \
                                           ' important to the cause of the' \
                                           ' Republic, but in the end, will' \
                                           ' the warrior fight for the Light' \
                                           ' Side of the Force, or succumb' \
                                           ' to the Darkness?'
    assert len(response.body['genre']) == 3
    assert len(response.body['actors']) == 4
    assert len(response.body['writers']) == 8
    assert response.body['directors'][0]['full_name'] == "Casey Hudson"


@pytest.mark.asyncio
async def test_get_film_data_by_unknown_id(make_get_request):
    response = await make_get_request('film/ead9b449-734b-4878-86f1-1e4c96a28bba')
    assert response.status == 404
    assert response.body['detail'] == 'Film not found'
