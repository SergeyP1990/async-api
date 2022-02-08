from uuid import UUID
from typing import List

from models.base import BaseOrjsonModel


class Person(BaseOrjsonModel):
    uuid: str
    full_name: str
    role: List[dict]
    film_ids: List[UUID]
