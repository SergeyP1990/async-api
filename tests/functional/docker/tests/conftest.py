import aiohttp
import pytest
import sys
import asyncio
import aiofiles
import json
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
sys.path.append('/usr/src/tests/')
import settings
from settings import HTTPResponse, test_settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    url = '{es_host}:{es_port}'.format(
        es_host=test_settings.es_host,
        es_port=test_settings.es_port
    )
    client = AsyncElasticsearch(
        hosts=url
    )
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = '{protocol}://{service_url}/api/v{api_version}/{method}'.format(
            protocol=test_settings.service_protocol,
            service_url=test_settings.service_url,
            api_version=test_settings.api_version,
            method=method
        )
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


def read_json_file(file_path):
    with open(file_path) as json_file:
        json_data = json.load(json_file)
    return json_data


async def create_index(es_client, index_name):
    index_path = settings.test_settings.index_path.joinpath(f"{index_name}.json")
    index = read_json_file(index_path)
    await es_client.indices.create(index=index_name, body=index, ignore=400)


async def load_data_in_index(es_client, index_name):
    data_path = settings.test_settings.load_data_path.joinpath(
        f"{index_name}.json"
    )
    data = read_json_file(data_path)
    await async_bulk(es_client, data, index=index_name)


async def initialize_es_index(es_client, index_name):
    await create_index(es_client, index_name)
    await load_data_in_index(es_client, index_name)


@pytest.fixture(scope="session", autouse=True)
async def load_data(es_client):
    for index in settings.test_settings.es_indexes:
        await initialize_es_index(es_client, index)


@pytest.fixture(scope="function")
async def expected_json_response(request):
    file = test_settings.expected_response_path.joinpath(f"{request.node.name}.json")
    async with aiofiles.open(file) as f:
        content = await f.read()
        response = json.loads(content)
    return response
