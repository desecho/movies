"""Views mixins."""

from typing import Any

from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView as View


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    """AJAX anonymous view."""

    def success(self, **kwargs: Any) -> HttpResponse:
        """Return success response."""
        payload = {"status": "success"}
        payload.update(kwargs)
        response: HttpResponse = self.render_json_response(payload)
        return response


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    """AJAX authenticated view."""

    raise_exception = True
