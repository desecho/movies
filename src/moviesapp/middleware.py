"""Middlewares."""

import zoneinfo
from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.utils import timezone


class TimezoneMiddleware:
    """Timezone middleware."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        """Init."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Call."""
        if request.user.is_authenticated:
            tzname = request.user.timezone.key
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                timezone.deactivate()
        return self.get_response(request)
