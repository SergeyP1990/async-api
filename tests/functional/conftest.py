import aiohttp
import pytest
import sys
import asyncio
from elasticsearch import AsyncElasticsearch
sys.path.append('/usr/src/tests/')
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
