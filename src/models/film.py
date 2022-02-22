from typing import List, Optional, ClassVar

from models.base import BaseOrjsonModel


class FilmSmall(BaseOrjsonModel):
    uuid: str
    title: str
    imdb_rating: float = None

    table_name: ClassVar[str] = "movies"


class Film(FilmSmall):
    description: str = None
    genre: Optional[List[dict]] = None
    actors: Optional[List[dict]] = None
    writers: Optional[List[dict]] = None
    directors: Optional[List[dict]] = None
