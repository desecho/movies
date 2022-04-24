from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import TemplateView as TemplateViewOriginal, View

from moviesapp.models import User

from .utils import get_anothers_account


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    def success(self, **kwargs):
        response = {"status": "success"}
        response.update(kwargs)
        return self.render_json_response(response)


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    raise_exception = True


class VkAjaxView(AjaxView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_vk_user:
            return self.no_permissions_fail(request)
        return super().dispatch(request, *args, **kwargs)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    anothers_account = None

    def check_if_allowed(self, username=None):
        if username is None and self.request.user.is_anonymous:
            raise Http404
        if self.request.user.username == username:
            return
        self.anothers_account = get_anothers_account(username)
        if self.anothers_account:
            if User.objects.get(username=username) not in self.request.user.get_users():
                raise PermissionDenied
