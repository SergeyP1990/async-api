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
async def test_get_film_data_by_id_2(make_get_request):
    response = await make_get_request('film/fc23ea9c-e799-419a-9df0-fc9d9b941a12')
    assert response.status == 200
    assert len(response.body) == 8
    assert response.body['uuid'] == 'fc23ea9c-e799-419a-9df0-fc9d9b941a12'
    assert response.body['title'] == 'Star Troopers'
    assert response.body['imdb_rating'] == 4.7
    assert response.body['description'] == 'In the closing stages of the' \
                                           ' 21st Century, an enigmatic' \
                                           ' warrior, called the Baron,' \
                                           ' leads the crusade that the' \
                                           ' religious organization Exorcio' \
                                           ' Deus Machine is conducting' \
                                           ' against the forces of Evil.' \
                                           ' During an extermination mission,' \
                                           ' the Baron is taken prisoner' \
                                           ' by the evil sorceress Lady' \
                                           ' Pervertvm and is tortured' \
                                           ' until she gets his seed.' \
                                           ' Lady Pervertvm uses the' \
                                           ' Baron\'s seminal fluid to' \
                                           ' fertilize the Beast-Ragnarok' \
                                           ' in order to have it engender' \
                                           ' the most powerful and ultimate' \
                                           ' race of demons. The Baron manages' \
                                           ' to escape but, blinded by his' \
                                           ' guilt, he begins a bloody Via ' \
                                           'Crucis which will start to reveal' \
                                           ' his true nature.'
    assert len(response.body['genre']) == 3
    assert response.body['genre'][0] == {
        "name": "Action",
        "uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"
    }
    assert response.body['genre'][1] == {
        "name": "Adventure",
        "uuid": "120a21cf-9097-479e-904a-13dd7198c1dd"
    }
    assert response.body['genre'][2] == {
        "name": "Fantasy",
        "uuid": "b92ef010-5e4c-4fd0-99d6-41b6456272cd"
    }
    assert len(response.body['actors']) == 4
    assert len(response.body['writers']) == 1
    assert response.body['writers'][0] == {
        "uuid": "9672c2ca-c113-4b3c-8a34-31edf0398a88",
        "full_name": "Ricardo Ribelles"
    }
    assert response.body['directors'][0]['full_name'] == "Ricardo Ribelles"


@pytest.mark.asyncio
async def test_get_film_data_by_unknown_id(make_get_request):
    response = await make_get_request('film/ead9b449-734b-4878-86f1-1e4c96a28bba')
    assert response.status == 404
    assert len(response.body) == 1
    assert response.body['detail'] == 'Film not found'
