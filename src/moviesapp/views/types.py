"""Types for views."""
from typing import TYPE_CHECKING, List, Optional

from django.core.paginator import Page
from django.db.models import QuerySet
from typing_extensions import TypedDict

from ..types import ListKeyName, SortType

if TYPE_CHECKING:
    from ..models import ActionRecord, Record, User


class FeedViewContextData(TypedDict):
    """Feed view context data."""

    feed_name: str
    action_records: QuerySet["ActionRecord"]


class PeopleViewContextData(TypedDict):
    """People view context data."""

    users: Page["User"]


class GalleryViewContextData(TypedDict):
    """Gallery view context data."""

    records: QuerySet["Record"]
    anothers_account: Optional["User"]
    list: ListKeyName


class ListViewContextData(TypedDict):
    """List view context data."""

    records: Page["Record"]
    anothers_account: Optional["User"]
    list_id: int
    list: ListKeyName
    list_data: str
    sort: SortType
    query: str


class RecommendationsViewContextData(TypedDict):
    """Recommendations view context data."""

    records: List["Record"]
