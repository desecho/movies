"""Types for views."""

from __future__ import annotations

from typing import Optional

from typing_extensions import NotRequired, TypedDict

from ..types import Trailer


class MovieObject(TypedDict):
    """Movie object."""

    id: int
    title: str
    titleOriginal: str
    posterSmall: Optional[str]
    posterNormal: Optional[str]
    posterBig: Optional[str]
    isReleased: bool
    imdbRating: Optional[float]
    releaseDate: Optional[str]
    releaseDateTimestamp: float
    country: Optional[str]
    director: Optional[str]
    writer: Optional[str]
    genre: Optional[str]
    actors: Optional[str]
    overview: Optional[str]
    homepage: Optional[str]
    runtime: Optional[str]
    imdbUrl: str
    tmdbUrl: str
    trailers: list[Trailer]
    hasPoster: bool


class ProviderObject(TypedDict):
    """Provider object."""

    logo: str
    name: str


class ProviderRecordObject(TypedDict):
    """Provider record object."""

    tmdbWatchUrl: str
    provider: ProviderObject


class OptionsObject(TypedDict):
    """Options object."""

    original: bool
    extended: bool
    theatre: bool
    hd: bool
    fullHd: bool
    ultraHd: bool
    ignoreRewatch: bool


class RecordObject(TypedDict):
    """Record object."""

    id: int
    order: int
    movie: MovieObject
    comment: str
    commentArea: bool
    rating: int
    providerRecords: list[ProviderRecordObject]
    options: OptionsObject
    listId: NotRequired[Optional[int]]
    additionDate: float


class SearchOptions(TypedDict):
    """Search options."""

    popularOnly: bool
    sortByDate: bool


class MovieListResult(TypedDict):
    """Movie search result."""

    id: int
    tmdbLink: str
    releaseDate: Optional[str]
    title: str
    titleOriginal: str
    poster: Optional[str]
    poster2x: Optional[str]
    isReleased: bool
