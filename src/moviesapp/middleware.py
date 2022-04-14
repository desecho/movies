from django.conf import settings
from django.http import QueryDict
from django.utils.translation import activate


class PutHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "PUT":
            request.PUT = QueryDict(request.body)
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
