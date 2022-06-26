"""Views mixins."""
from typing import Any, Optional

from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView as TemplateViewOriginal, View

from ..http import AuthenticatedHttpRequest, HttpRequest
from ..models import User
from .utils import get_anothers_account


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


class TemplateAnonymousView(TemplateViewOriginal):
    """Template anonymous view."""

    anothers_account: Optional[User] = None

    def check_if_allowed(self, username: Optional[str] = None) -> None:
        """Check if user is allowed to see the page."""
        request: HttpRequest = self.request  # type: ignore
        if username is None and request.user.is_anonymous:
            raise Http404
        user = request.user
        if user.username == username:
            return
        self.anothers_account = get_anothers_account(username)
        if self.anothers_account:
            if User.objects.get(username=username) not in user.get_users():
                raise PermissionDenied


class TemplateView(LoginRequiredMixin, TemplateAnonymousView):
    """Template authenticated view."""

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        """Get."""
        request: HttpRequest = request  # type: ignore
        return TemplateAnonymousView.get(self, request, *args, **kwargs)
