"""Custom Types."""
from __future__ import annotations

from datetime import date, time
from typing import Any, Literal, Optional, TypeAlias

from django.urls import URLPattern, URLResolver
from typing_extensions import NotRequired, TypedDict


class TemplatesSettingsOptions(TypedDict):
    """Templates settings options."""

    context_processors: list[str]
    loaders: list[str | tuple[str, list[str]]]
    builtins: list[str]


class TemplatesSettings(TypedDict):
    """Templates settings."""

    NAME: str
    BACKEND: str
    DIRS: NotRequired[list[str]]
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


class TmdbMovieListResultProcessed(TypedDict):
    """TMDB movie search result processed."""

    poster_path: Optional[str]
    popularity: float
    id: int
    release_date: Optional[date]
    title: str
    title_original: str


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
    trailers_en: list[TmdbTrailer]
    trailers_ru: list[TmdbTrailer]
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

# UntypedObject means it is a loaded JSON object
UntypedObject: TypeAlias = dict[str, Any]

URL: TypeAlias = URLPattern | URLResolver
