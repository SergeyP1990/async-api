from models.base import BaseOrjsonModel
from typing import ClassVar


class Genre(BaseOrjsonModel):
    uuid: str
    name: str

    table_name: ClassVar[str] = "genres"
