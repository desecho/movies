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


class ContextVariables(TypedDict):
    """Context variables."""

    DEBUG: bool
    ADMIN_EMAIL: str
    GOOGLE_ANALYTICS_ID: str


class Trailer(TypedDict):
    """Trailer."""

    url: str
    name: str


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


class SearchOptions(TypedDict):
    """Search options."""

    popularOnly: bool
    sortByDate: bool


WatchData: TypeAlias = List[WatchDataRecord]
Trailers: TypeAlias = List[Trailer]
TrailerSite = Literal["YouTube", "Vimeo"]
SearchType = Literal["movie", "actor", "director"]
Runtime: TypeAlias = Optional[datetime]
OmdbRatings: TypeAlias = List[OmdbRating]
OmdbMoviePreprocessedKey = Literal["Writer", "Actors", "Director", "Genre", "Country", "imdbRating", "Runtime"]
