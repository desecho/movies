"""Custom Types."""
from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional, Tuple, TypeAlias

from typing_extensions import NotRequired, TypedDict


class TemplatesSettingsOptions(TypedDict):
    """Templates settings options."""

    context_processors: List[str]
    loaders: List[str | Tuple[str, List[str]]]
    builtins: List[str]


class TemplatesSettings(TypedDict):
    """Templates settings."""

    NAME: str
    BACKEND: str
    DIRS: NotRequired[List[str]]
    OPTIONS: NotRequired[TemplatesSettingsOptions]
    APP_DIRS: NotRequired[Optional[bool]]


class WatchDataRecord(TypedDict):
    """Watch data record."""

    provider_id: int
    country: str


class ProviderTmdb(TypedDict):
    """Provider TMDB."""

    display_priority: int
    logo_path: str
    provider_name: str
    provider_id: int


class ContextVariables(TypedDict):
    """Context variables."""

    DEBUG: bool
    ADMIN_EMAIL: str
    GOOGLE_ANALYTICS_ID: str


class TrailerTmdb(TypedDict):
    """Trailer TMDB."""

    key: str
    name: str
    site: TrailerSite


class Trailer(TypedDict):
    """Trailer."""

    url: str
    name: str


class WatchDataTmdb(TypedDict):
    """Watch data from TMDB."""

    AR: WatchDataCountryTmdb
    AT: WatchDataCountryTmdb
    AU: WatchDataCountryTmdb
    BE: WatchDataCountryTmdb
    BR: WatchDataCountryTmdb
    CA: WatchDataCountryTmdb
    CH: WatchDataCountryTmdb
    CL: WatchDataCountryTmdb
    CO: WatchDataCountryTmdb
    CZ: WatchDataCountryTmdb
    DE: WatchDataCountryTmdb
    DK: WatchDataCountryTmdb
    EC: WatchDataCountryTmdb
    EE: WatchDataCountryTmdb
    ES: WatchDataCountryTmdb
    FI: WatchDataCountryTmdb
    FR: WatchDataCountryTmdb
    GB: WatchDataCountryTmdb
    GR: WatchDataCountryTmdb
    HU: WatchDataCountryTmdb
    ID: WatchDataCountryTmdb
    IE: WatchDataCountryTmdb
    IN: WatchDataCountryTmdb
    IT: WatchDataCountryTmdb
    JP: WatchDataCountryTmdb
    KR: WatchDataCountryTmdb
    LT: WatchDataCountryTmdb
    LV: WatchDataCountryTmdb
    MX: WatchDataCountryTmdb
    MY: WatchDataCountryTmdb
    NL: WatchDataCountryTmdb
    NO: WatchDataCountryTmdb
    NZ: WatchDataCountryTmdb
    PE: WatchDataCountryTmdb
    PH: WatchDataCountryTmdb
    PL: WatchDataCountryTmdb
    PT: WatchDataCountryTmdb
    RO: WatchDataCountryTmdb
    RU: WatchDataCountryTmdb
    SE: WatchDataCountryTmdb
    SG: WatchDataCountryTmdb
    TH: WatchDataCountryTmdb
    TR: WatchDataCountryTmdb
    US: WatchDataCountryTmdb
    VE: WatchDataCountryTmdb
    ZA: WatchDataCountryTmdb


class WatchDataCountryTmdb(TypedDict):
    """Watch data country TMDB."""

    link: str
    flatrate: NotRequired[ProvidersTmdb]
    free: NotRequired[ProvidersTmdb]
    ads: NotRequired[ProvidersTmdb]
    rent: NotRequired[ProvidersTmdb]
    buy: NotRequired[ProvidersTmdb]


class TrailerSites(TypedDict):
    """Trailer sites."""

    YouTube: str
    Vimeo: str


class OmdbRating(TypedDict):
    """OMDb rating."""

    Source: str
    Value: str


class OmdbMovie(TypedDict):
    """OMDb movie."""

    Title: str
    Year: str
    Rated: str
    Released: str
    Runtime: str
    Genre: str
    Director: str
    Writer: str
    Actors: str
    Plot: str
    Language: str
    Country: str
    Awards: str
    Poster: str
    Ratings: OmdbRatings
    Metascore: str
    imdbRating: str
    imdbVotes: str
    imdbID: str
    Type: str
    DVD: str
    BoxOffice: str
    Production: str
    Website: str
    Response: str
    Error: NotRequired[str]


class OmdbMovieProcessed(TypedDict):
    """OMDb movie processed."""

    writer: Optional[str]
    director: Optional[str]
    actors: Optional[str]
    genre: Optional[str]
    country: Optional[str]
    imdb_rating: Optional[str]
    runtime: Runtime


class OmdbMoviePreprocessed(TypedDict):
    """OMDb movie preprocessed."""

    Writer: Optional[str]
    Director: Optional[str]
    Actors: Optional[str]
    Genre: Optional[str]
    Country: Optional[str]
    imdbRating: Optional[str]
    Runtime: Optional[str]


WatchData: TypeAlias = List[WatchDataRecord]
TrailersTmdb: TypeAlias = List[TrailerTmdb]
Trailers: TypeAlias = List[Trailer]
ProvidersTmdb: TypeAlias = List[ProviderTmdb]
TrailerSite = Literal["YouTube", "Vimeo"]
Runtime: TypeAlias = Optional[datetime]
OmdbRatings: TypeAlias = List[OmdbRating]
OmdbMoviePreprocessedKey = Literal["Writer", "Actors", "Director", "Genre", "Country", "imdbRating", "Runtime"]
