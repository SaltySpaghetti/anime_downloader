from pydantic import BaseModel


class Anime(BaseModel):
    id: int
    user_id: int
    title: str | None
    imageurl: str
    plot: str
    date: str
    episodes_count: int
    episodes_length: int
    author: str
    created_at: str
    status: str
    imageurl_cover: str
    type: str
    slug: str
    title_eng: str
    day: str
    favorites: int
    score: str
    visite: int
    studio: str
    dub: int
    always_home: int
    members: int
    cover: str | None
    anilist_id: int
    season: str
    title_it: str | None
    mal_id: int | None
    crunchy_id: str | None
    netflix_id: str | None
    prime_id: str | None
    disney_id: str | None
    real_episodes_count: int
