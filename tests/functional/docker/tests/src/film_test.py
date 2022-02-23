import pytest


@pytest.mark.asyncio
async def test_get_films_data_default(make_get_request):
    response = await make_get_request('film/')
    assert response.status == 200
    assert len(response.body) == 50
    assert response.body[0]['imdb_rating'] == 9.6
    assert response.body[49]['title'] == 'Wishes on a Falling Star'


@pytest.mark.asyncio
async def test_get_all_films_data(make_get_request):
    response = await make_get_request('film/?page[size]=1000')
    assert response.status == 200
    assert len(response.body) == 999
    assert response.body[0]['imdb_rating'] == 9.6
    assert response.body[998]['imdb_rating'] == None


@pytest.mark.asyncio
async def test_get_films_data_by_filter_comedy_and_sort_asc(make_get_request):
    response = await make_get_request('film/?sort=imdb_rating&filter[genre]=comedy')
    assert response.status == 200
    assert len(response.body) == 50
    assert response.body[0]['imdb_rating'] == 1.8
    assert response.body[49]['title'] == 'Pick a Star'


@pytest.mark.asyncio
async def test_get_film_data_by_id_1(make_get_request):
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
async def test_get_film_data_by_id_2_null_imdb_rating(make_get_request):
    response = await make_get_request('film/e7e6d147-cc10-406c-a7a2-5e0be2231327')
    assert response.status == 200
    assert len(response.body) == 8
    assert response.body['uuid'] == 'e7e6d147-cc10-406c-a7a2-5e0be2231327'
    assert response.body['title'] == 'Shooting Star'
    assert response.body['imdb_rating'] == None
    assert response.body['description'] == 'How far would a mother go' \
                                           ' to protect her children?'
    assert len(response.body['genre']) == 2
    assert response.body['genre'][0] == {
        "name": "Drama",
        "uuid": "1cacff68-643e-4ddd-8f57-84b62538081a"
    }
    assert response.body['genre'][1] == {
        "name": "Short",
        "uuid": "a886d0ec-c3f3-4b16-b973-dedcf5bfa395"
    }
    assert len(response.body['actors']) == 4
    assert len(response.body['writers']) == 2
    assert response.body['writers'][0] == {
        "uuid": "178c9768-6d04-4419-8afc-83d8228421ef",
        "full_name": "Yassen Genadiev"
    }
    assert response.body['writers'][1] == {
        "uuid": "1b8773c9-7e15-4809-a6d7-949c9b9def3b",
        "full_name": "Lyubo Yonchev"
    }
    assert response.body['directors'][0]['full_name'] == "Lyubo Yonchev"


@pytest.mark.asyncio
async def test_get_film_data_by_id_3_null_actors_writers_directors(make_get_request):
    response = await make_get_request('film/fd78a0e5-d4ec-435e-8994-4ccbdfc4e60b')
    assert response.status == 200
    assert len(response.body) == 8
    assert response.body['uuid'] == 'fd78a0e5-d4ec-435e-8994-4ccbdfc4e60b'
    assert response.body['title'] == 'Lone Star Restoration'
    assert response.body['imdb_rating'] == 8.7
    assert response.body['genre'][0] == {
      "name": "Reality-TV",
      "uuid": "e508c1c8-24c0-4136-80b4-340c4befb190"
    }
    assert response.body['actors'] == None
    assert response.body['writers'] == None
    assert response.body['directors'] == None


@pytest.mark.asyncio
async def test_get_film_data_by_unknown_id(make_get_request):
    response = await make_get_request('film/ead9b449-734b-4878-86f1-1e4c96a28bba')
    assert response.status == 404
    assert len(response.body) == 1
    assert response.body['detail'] == 'Film not found'
