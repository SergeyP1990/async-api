from typing import List, Optional

from models.base import BaseOrjsonModel


class FilmSmall(BaseOrjsonModel):
    uuid: str
    title: str
    imdb_rating: float = None

class Film(FilmSmall):
    description: str = None
    genre: Optional[List[dict]] = None
    actors: Optional[List[dict]] = None
    writers: Optional[List[dict]] = None
    directors: Optional[List[dict]] = None
