"""Custom Types."""
from __future__ import annotations

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


TrailerSite = Literal["YouTube", "Vimeo"]
SearchType = Literal["movie", "actor", "director"]
# UntypedObject means it is a loaded JSON object
UntypedObject: TypeAlias = Dict[str, Any]
