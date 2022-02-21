import orjson
from typing import ClassVar
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    print("======== JSON DUMPS CALL ==========")
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    table_name: ClassVar[str] = ""

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
