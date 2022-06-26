"""Types for views."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional

from django.core.paginator import Page
from django.db.models import QuerySet
from typing_extensions import NotRequired, TypedDict

from ..types import Trailer

if TYPE_CHECKING:
    from ..models import ActionRecord, Record, User


class FeedViewContextData(TypedDict):
    """Feed view context data."""

    feed_name: str
    action_records: QuerySet["ActionRecord"]


class PeopleViewContextData(TypedDict):
    """People view context data."""

    users: Page["User"] | List["User"]


class GalleryViewContextData(TypedDict):
    """Gallery view context data."""

    records: str
    anothers_account: Optional["User"]
    list: ListKeyName
    list_id: int


class ListViewContextData(TypedDict):
    """List view context data."""

    records: Page["Record"] | List["Record"]
    record_objects: str
    anothers_account: Optional["User"]
    list_id: int
    list: ListKeyName
    sort: SortType
    query: str


class TrendingViewContextData(TypedDict):
    """Trending view context data."""

    movies: str


class MovieGalleryObject(TypedDict):
    """Movie gallery object."""

    title: str
    titleOriginal: str
    posterNormal: Optional[str]
    posterBig: Optional[str]


class RecordGalleryObject(TypedDict):
    """Record gallery object."""

    id: int
    order: int
    movie: MovieGalleryObject


class MovieObject(MovieGalleryObject):
    """Movie object."""

    id: int
    isReleased: bool
    posterSmall: Optional[str]
    imdbRating: Optional[float]
    releaseDate: Optional[str]
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
    trailers: List[Trailer]
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


class RecordObject(TypedDict):
    """Record object."""

    id: int
    order: int
    movie: MovieObject
    comment: str
    commentArea: bool
    rating: int
    providerRecords: List[ProviderRecordObject]
    options: OptionsObject
    listId: NotRequired[Optional[int]]


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


ListKeyName = Literal["watched", "to-watch"]
SortType = Literal["releaseDate", "rating", "additionDate", "custom"]
