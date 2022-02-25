import os
from pathlib import Path
from pydantic import BaseSettings, Field
from dataclasses import dataclass
from multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


class TestSettings(BaseSettings):
    es_host: str = Field(os.getenv('ELASTIC_HOST'))
    es_port: str = Field(os.getenv('ELASTIC_PORT'))

    redis_host: str = Field(os.getenv('REDIS_HOST'))
    redis_port: str = Field(os.getenv('REDIS_PORT'))

    service_protocol: str = Field('http')
    service_url: str = Field(os.getenv('SERVICE_URL'))
    api_version: int = Field(os.getenv('API_VERSION'))

    expected_response_path: Path = Field("tests/functional/testdata/expected_response")
    index_path: Path = Field("tests/functional/testdata/index")
    load_data_path: Path = Field("tests/functional/testdata/load_data")


test_settings = TestSettings()
