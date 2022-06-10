"""HTTP classes."""
from typing import TYPE_CHECKING, Any, Dict, Union

from django.http import HttpRequest as DjangoHttpRequest

if TYPE_CHECKING:
    from .models import User, UserAnonymous


class AuthenticatedHttpRequest(DjangoHttpRequest):
    """Authenticated HTTP request."""

    user: "User"


class HttpRequest(DjangoHttpRequest):
    """HTTP request."""

    user: Union["UserAnonymous", "User"]


class AjaxHttpRequest(HttpRequest):
    """AJAX HTTP request."""

    PUT: Dict[str, Any] = {}
    LANGUAGE_CODE = ""


class AjaxAuthenticatedHttpRequest(AuthenticatedHttpRequest):
    """AJAX authenticated request."""

    PUT: Dict[str, Any] = {}
