import json

from django.conf import settings
from django.utils.translation import activate


class AjaxHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.PUT = {}
        if request.content_type == "application/json":
            setattr(request, request.method, json.loads(request.body))
        return self.get_response(request)


def language_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        user = request.user
        if user.is_authenticated:
            language = user.language
            activate(language)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response

    return middleware
