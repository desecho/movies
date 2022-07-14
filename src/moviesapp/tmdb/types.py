"""TMDB types."""
from typing import Optional

from typing_extensions import TypedDict

from ..types import UntypedObject


class TmdbBase(TypedDict, total=False):
    """TMDB base."""

    id: int
    adult: bool
    popularity: float


class TmdbMovieBase(TmdbBase, total=False):
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


class TmdbMovie(TmdbMovieBase, total=False):
    """TMDB movie."""

    belongs_to_collection: Optional[UntypedObject]  # TMDB does not provide a type for this
    budget: int
    genres: list[TmdbGenre]
    homepage: Optional[str]
    imdb_id: Optional[str]
    overview: Optional[str]
    production_companies: list[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    production_countries: list[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    revenue: int
    runtime: Optional[int]
    spoken_languages: list[UntypedObject]  # TMDB provides a type for this. Set as untyped because it is not used.
    status: str
    tagline: Optional[str]


class TmdbMovieListResult(TmdbMovieBase, total=False):
    """TMDB movie search result."""

    overview: str
    genre_ids: list[int]


class TmdbPerson(TmdbBase, total=False):
    """TMDB person."""

    profile_path: Optional[str]
    known_for: UntypedObject  # TMDB provides a type for this. Set as untyped because it is not used.
    name: str


class TmdbCastCrewBase(TmdbMovieListResult, total=False):
    """TMDB cast/crew base."""

    credit_id: str
    episode_count: int
    first_air_date: str
    media_type: str
    name: str
    origin_country: list[str]
    original_name: str


class TmdbCast(TmdbCastCrewBase, total=False):
    """TMDB cast."""

    character: str
    vote_average: int | float  # type: ignore


class TmdbCrew(TmdbCastCrewBase, total=False):
    """TMDB Crew."""

    department: str
    job: str


class TmdbCombinedCredits(TypedDict):
    """TMDB combined credits."""

    id: int
    cast: list[TmdbCast]
    crew: list[TmdbCrew]


class TmdbProvider(TypedDict, total=False):
    """TMDB Provider."""

    display_priority: int
    logo_path: str
    provider_name: str
    provider_id: int


class TmdbWatchDataCountry(TypedDict, total=False):
    """TMDB watch data country."""

    link: str
    flatrate: list[TmdbProvider]
    free: list[TmdbProvider]
    ads: list[TmdbProvider]
    rent: list[TmdbProvider]
    buy: list[TmdbProvider]


class TmdbWatchData(TypedDict, total=False):
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
