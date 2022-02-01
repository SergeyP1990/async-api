from typing import List, Optional
from uuid import UUID

import orjson
# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: UUID
    name: str


class Genre(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    title: str
    description: str
    rating: float
    type: str

    genres: Optional[List[Genre]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]
    directors: Optional[List[Person]]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
