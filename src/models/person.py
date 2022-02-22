from uuid import UUID
from typing import List, ClassVar

from models.base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    uuid: str
    full_name: str
    role: List[dict]
    film_ids: List[UUID]

    table_name: ClassVar[str] = "persons"
