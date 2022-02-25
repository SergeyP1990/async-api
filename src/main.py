import backoff
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from socket import gaierror

from api.v1 import film, genre, person
from core import config
from db.search_engine import search_engine
from db.cache import cache

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    # Адрес документации в красивом интерфейсе
    docs_url='/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/api/openapi.json',
    # Можно сразу сделать небольшую оптимизацию сервиса
    # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0"
)


@app.on_event('startup')
@backoff.on_exception(backoff.expo, (ValueError, gaierror), max_time=25)
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    await cache.connect()
    await search_engine.connect()


@app.on_event('shutdown')
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await cache.close()
    await search_engine.close()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации

app.include_router(film.router, prefix='/api/v1/film')
app.include_router(genre.router, prefix='/api/v1/genre')
app.include_router(person.router, prefix='/api/v1/person')
