"""Middlewares."""
import json
from typing import Callable

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import activate

from .http import AjaxHttpRequest, HttpRequest
from .models import User


class AjaxHandlerMiddleware:
    """AJAX Handler Middleware."""

    def __init__(self, get_response: Callable[[AjaxHttpRequest], HttpResponse]):
        """Init."""
        self.get_response = get_response

    def __call__(self, request: AjaxHttpRequest) -> HttpResponse:
        """Call."""
        request.PUT = {}
        method = request.method
        if method and request.content_type == "application/json":
            setattr(request, method, json.loads(request.body))
        return self.get_response(request)


def language_middleware(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    """Language middleware."""

    def middleware(request: HttpRequest) -> HttpResponse:
        """Middleware."""
        response = get_response(request)
        if request.user.is_authenticated:
            user: User = request.user
            language = user.language
            activate(language)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response

    return middleware
