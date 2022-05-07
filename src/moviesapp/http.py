from typing import TYPE_CHECKING, Any, Dict, Union

from django.http import HttpRequest as DjangoHttpRequest

if TYPE_CHECKING:
    from moviesapp.models import User, UserAnonymous


class AuthenticatedHttpRequest(DjangoHttpRequest):
    user: "User"


class HttpRequest(DjangoHttpRequest):
    user: Union["UserAnonymous", "User"]


class AjaxHttpRequest(HttpRequest):
    PUT: Dict[str, Any] = {}
    LANGUAGE_CODE = ""


class AjaxAuthenticatedHttpRequest(AuthenticatedHttpRequest):
    PUT: Dict[str, Any] = {}
