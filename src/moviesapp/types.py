"""Custom Types."""
from __future__ import annotations

from datetime import date, time
from typing import Any, Dict, List, Literal, Optional, Tuple, TypeAlias

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


class ProviderRecordType(WatchDataRecord, total=False):
    """Provider record."""

    id: int


class ContextVariables(TypedDict):
    """Context variables."""

    DEBUG: bool
    ADMIN_EMAIL: str
    GOOGLE_ANALYTICS_ID: str


class Trailer(TypedDict):
    """Trailer."""

    url: str
    name: str


class TrailerSitesSettings(TypedDict):
    """Trailer sites."""

    YouTube: str
    Vimeo: str


class SearchOptions(TypedDict):
    """Search options."""

    popularOnly: bool
    sortByDate: bool


class TmdbMovieSearchResultProcessed(TypedDict):
    """TMDB movie search result processed."""

    poster_path: Optional[str]
    popularity: float
    id: int
    release_date: Optional[date]
    title: str


class MovieSearchResult(TypedDict):
    """Movie search result."""

    id: int
    tmdbLink: str
    elementId: str
    releaseDate: Optional[str]
    title: str
    poster: Optional[str]
    poster2x: Optional[str]


class TmdbTrailer(TypedDict):
    """TMDB trailer."""

    key: str
    name: str
    site: TrailerSite


class TmdbMovieProcessed(TypedDict):
    """TMDB movie processed."""

    tmdb_id: int
    imdb_id: str
    release_date: Optional[date]
    title_original: str
    poster_ru: Optional[str]
    poster_en: Optional[str]
    homepage: Optional[str]
    trailers_en: List[TmdbTrailer]
    trailers_ru: List[TmdbTrailer]
    title_en: str
    title_ru: str
    overview_en: Optional[str]
    overview_ru: Optional[str]
    runtime: Optional[time]


class OmdbMovieProcessed(TypedDict):
    """OMDb movie processed."""

    writer: Optional[str]
    director: Optional[str]
    actors: Optional[str]
    genre: Optional[str]
    country: Optional[str]
    imdb_rating: Optional[str]


class MovieTmdbOmdb(TmdbMovieProcessed, OmdbMovieProcessed):
    """Movie TMDb and OMDb merged together."""


TrailerSite = Literal["YouTube", "Vimeo"]
SearchType = Literal["movie", "actor", "director"]
ListKeyName = Literal["watched", "to-watch"]
SortType = Literal["release_date", "rating", "addition_date"]

# UntypedObject means it is a loaded JSON object
UntypedObject: TypeAlias = Dict[str, Any]
