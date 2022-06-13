"""TMDB types."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypeAlias

from typing_extensions import NotRequired, TypedDict

from ..types import TrailerSite


class TmdbBase(TypedDict):
    """TMDB base."""

    id: int
    adult: bool
    popularity: float


class TmdbMovie(TmdbBase):
    """Movie TMDB."""

    poster_path: TmdbPoster
    overview: str
    release_date: str
    genre_ids: List[int]
    original_title: str
    original_language: str
    title: str
    backdrop_path: Optional[str]
    vote_count: int
    video: bool
    vote_average: float


class TmdbMoviePreprocessed(TypedDict):
    """Movie TMDB preprocessed."""

    poster_path: TmdbPoster
    popularity: float
    id: int
    release_date: str
    title: str


class TmdbPerson(TmdbBase):
    """Person TMDB."""

    profile_path: Optional[str]
    known_for: Dict[str, Any]
    name: str


class TmdbCastCrewBase(TmdbMovie):
    """Cast/Crew base TMDB."""

    credit_id: str
    episode_count: int
    first_air_date: str
    media_type: str
    name: str
    origin_country: List[str]
    original_name: str


class TmdbCast(TmdbCastCrewBase):
    """Cast TMDB."""

    character: str
    vote_average: int | float  # type: ignore


class TmdbCrew(TmdbCastCrewBase):
    """Crew TMDB."""

    department: str
    job: str


class TmdbProvider(TypedDict):
    """Provider TMDB."""

    display_priority: int
    logo_path: str
    provider_name: str
    provider_id: int


class TmdbCombinedCredits(TypedDict):
    """Combined credits TMDB."""

    id: int
    cast: TmdbCastEntries
    crew: TmdbCrewEntries


class TmdbWatchData(TypedDict):
    """Watch data from TMDB."""

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


class TmdbWatchDataCountry(TypedDict):
    """Watch data country TMDB."""

    link: str
    flatrate: NotRequired[TmdbProviders]
    free: NotRequired[TmdbProviders]
    ads: NotRequired[TmdbProviders]
    rent: NotRequired[TmdbProviders]
    buy: NotRequired[TmdbProviders]


class TmdbTrailer(TypedDict):
    """Trailer TMDB."""

    key: str
    name: str
    site: TrailerSite


TmdbTrailers: TypeAlias = List[TmdbTrailer]
TmdbProviders: TypeAlias = List[TmdbProvider]
TmdbMovies: TypeAlias = List[TmdbMovie]
TmdbPersons: TypeAlias = List[TmdbPerson]
TmdbCastEntries: TypeAlias = List[TmdbCast]
TmdbCrewEntries: TypeAlias = List[TmdbCrew]
TmdbMoviesPreprocessed: TypeAlias = List[TmdbMoviePreprocessed]
TmdbPoster: TypeAlias = Optional[str]
