"""TMDB types."""
from __future__ import annotations

from typing import List, Optional

from typing_extensions import NotRequired, TypedDict

from ..types import TrailerSite, UntypedObject


class TmdbBase(TypedDict):
    """TMDB base."""

    id: int
    adult: bool
    popularity: float


class TmdbMovieBase(TmdbBase):
    """TMDB movie base."""

    backdrop_path: Optional[str]
    original_title: str
    original_language: str
    poster_path: Optional[str]
    release_date: str
    title: str
    video: bool
    vote_average: float
    vote_count: int


class TmdbGenre(TypedDict):  # TODO: Not used yet but will need to use later
    """TMDB genre."""

    id: int
    name: str


class TmdbMovie(TmdbMovieBase):
    """TMDB movie."""

    belongs_to_collection: Optional[UntypedObject]  # TMDB does not provide a type for this
    budget: int
    genres: List[TmdbGenre]
    homepage: Optional[str]
    imdb_id: Optional[str]
    overview: Optional[str]
    production_companies: List[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    production_countries: List[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    revenue: int
    runtime: Optional[int]
    spoken_languages: List[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    status: str
    tagline: Optional[str]


class TmdbMovieSearchResult(TmdbMovieBase):
    """TMDB movie search result."""

    overview: str
    genre_ids: List[int]


class TmdbMovieSearchResultPreprocessed(TypedDict):
    """TMDB movie search result preprocessed."""

    poster_path: Optional[str]
    popularity: float
    id: int
    release_date: str
    title: str


class TmdbPerson(TmdbBase):
    """TMDB person."""

    profile_path: Optional[str]
    known_for: UntypedObject  # TMDB provides a type for this. Set as untyped because it is not used.
    name: str


class TmdbCastCrewBase(TmdbMovieSearchResult):
    """TMDB cast/crew base."""

    credit_id: str
    episode_count: int
    first_air_date: str
    media_type: str
    name: str
    origin_country: List[str]
    original_name: str


class TmdbCast(TmdbCastCrewBase):
    """TMDB cast."""

    character: str
    vote_average: int | float  # type: ignore


class TmdbCrew(TmdbCastCrewBase):
    """TMDB Crew."""

    department: str
    job: str


class TmdbCombinedCredits(TypedDict):
    """TMDB combined credits."""

    id: int
    cast: List[TmdbCast]
    crew: List[TmdbCrew]


class TmdbProvider(TypedDict):
    """TMDB Provider."""

    display_priority: int
    logo_path: str
    provider_name: str
    provider_id: int


class TmdbWatchDataCountry(TypedDict):
    """TMDB watch data country."""

    link: str
    flatrate: NotRequired[List[TmdbProvider]]
    free: NotRequired[List[TmdbProvider]]
    ads: NotRequired[List[TmdbProvider]]
    rent: NotRequired[List[TmdbProvider]]
    buy: NotRequired[List[TmdbProvider]]


class TmdbWatchData(TypedDict):
    """TMDB watch data from."""

    AR: TmdbWatchDataCountry
    AT: TmdbWatchDataCountry
    AU: TmdbWatchDataCountry
    BE: TmdbWatchDataCountry
    BR: TmdbWatchDataCountry
    CA: TmdbWatchDataCountry
    CH: TmdbWatchDataCountry
    CL: TmdbWatchDataCountry
    CO: TmdbWatchDataCountry
    CZ: TmdbWatchDataCountry
    DE: TmdbWatchDataCountry
    DK: TmdbWatchDataCountry
    EC: TmdbWatchDataCountry
    EE: TmdbWatchDataCountry
    ES: TmdbWatchDataCountry
    FI: TmdbWatchDataCountry
    FR: TmdbWatchDataCountry
    GB: TmdbWatchDataCountry
    GR: TmdbWatchDataCountry
    HU: TmdbWatchDataCountry
    ID: TmdbWatchDataCountry
    IE: TmdbWatchDataCountry
    IN: TmdbWatchDataCountry
    IT: TmdbWatchDataCountry
    JP: TmdbWatchDataCountry
    KR: TmdbWatchDataCountry
    LT: TmdbWatchDataCountry
    LV: TmdbWatchDataCountry
    MX: TmdbWatchDataCountry
    MY: TmdbWatchDataCountry
    NL: TmdbWatchDataCountry
    NO: TmdbWatchDataCountry
    NZ: TmdbWatchDataCountry
    PE: TmdbWatchDataCountry
    PH: TmdbWatchDataCountry
    PL: TmdbWatchDataCountry
    PT: TmdbWatchDataCountry
    RO: TmdbWatchDataCountry
    RU: TmdbWatchDataCountry
    SE: TmdbWatchDataCountry
    SG: TmdbWatchDataCountry
    TH: TmdbWatchDataCountry
    TR: TmdbWatchDataCountry
    US: TmdbWatchDataCountry
    VE: TmdbWatchDataCountry
    ZA: TmdbWatchDataCountry


class TmdbTrailer(TypedDict):
    """TMDB trailer."""

    key: str
    name: str
    site: TrailerSite
