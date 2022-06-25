"""HTTP classes."""
from typing import TYPE_CHECKING, Union

from django.http import HttpRequest as DjangoHttpRequest

from .types import UntypedObject

if TYPE_CHECKING:  # pragma: no cover
    from .models import User, UserAnonymous


class AuthenticatedHttpRequest(DjangoHttpRequest):
    """Authenticated HTTP request."""

    user: "User"


class HttpRequest(DjangoHttpRequest):
    """HTTP request."""

    LANGUAGE_CODE = ""

    user: Union["UserAnonymous", "User"]


class AjaxHttpRequest(HttpRequest):
    """AJAX HTTP request."""

    PUT: UntypedObject = {}


class AjaxAuthenticatedHttpRequest(AuthenticatedHttpRequest):
    """AJAX authenticated request."""

    PUT: UntypedObject = {}
