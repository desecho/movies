import json
from typing import Callable

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import activate

from moviesapp.http import AjaxHttpRequest, HttpRequest
from moviesapp.models import User


class AjaxHandlerMiddleware:
    def __init__(self, get_response: Callable[[AjaxHttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: AjaxHttpRequest) -> HttpResponse:
        request.PUT = {}
        method = request.method
        if method and request.content_type == "application/json":
            setattr(request, method, json.loads(request.body))
        return self.get_response(request)


def language_middleware(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        response = get_response(request)
        if request.user.is_authenticated:
            user: User = request.user
            language = user.language
            activate(language)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response

    return middleware
