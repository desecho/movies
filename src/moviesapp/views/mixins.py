from typing import Any, Optional

from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import TemplateView as TemplateViewOriginal, View

from moviesapp.http import AjaxAuthenticatedHttpRequest, AuthenticatedHttpRequest, HttpRequest
from moviesapp.models import User

from .utils import get_anothers_account


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    def success(self, **kwargs: Any) -> HttpResponse:
        payload = {"status": "success"}
        payload.update(kwargs)
        response: HttpResponse = self.render_json_response(payload)
        return response


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    raise_exception = True


class VkAjaxView(AjaxView):
    def dispatch(  # type: ignore
        self, request: AjaxAuthenticatedHttpRequest, *args: Any, **kwargs: Any
    ) -> (HttpResponseRedirect | HttpResponse | StreamingHttpResponse | Any):
        if not request.user.is_vk_user:
            return self.no_permissions_fail(request)
        return super().dispatch(request, *args, **kwargs)


class TemplateAnonymousView(TemplateViewOriginal):
    anothers_account: Optional[User] = None

    def check_if_allowed(self, username: Optional[str] = None) -> None:
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
    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        request: HttpRequest = request  # type: ignore
        return TemplateAnonymousView.get(self, request, *args, **kwargs)
