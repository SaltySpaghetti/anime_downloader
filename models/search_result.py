from pydantic import BaseModel

from models.anime import Anime


class SearchResult(BaseModel):
    records: list[Anime]
