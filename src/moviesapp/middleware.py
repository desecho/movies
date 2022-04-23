import json

from django.conf import settings
from django.utils.translation import activate


class AjaxHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.content_type == "application/json":
            method = request.method
            body = request.body
            if method == "PUT":
                request.PUT = json.loads(body)
            if method == "POST":
                request.POST = json.loads(body)
        response = self.get_response(request)
        return response


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
