"""Types for views."""
from typing import TYPE_CHECKING

from django.core.paginator import Page
from django.db.models import QuerySet
from typing_extensions import TypedDict

if TYPE_CHECKING:
    from ..models import ActionRecord, User


class FeedViewContextData(TypedDict):
    """Feed view context data."""

    feed_name: str
    action_records: QuerySet["ActionRecord"]


class PeopleViewContextData(TypedDict):
    """People view context data."""

    users: Page["User"]
