"""Types for views."""
from typing import TYPE_CHECKING, Optional

from django.core.paginator import Page
from django.db.models import QuerySet
from typing_extensions import TypedDict

from ..types import ListKeyName

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
