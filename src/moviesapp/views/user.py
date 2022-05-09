from typing import Any, Dict

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from ..forms import UserForm
from ..http import HttpRequest
from .mixins import TemplateAnonymousView


def logout_view(request: HttpRequest) -> (HttpResponseRedirect | HttpResponsePermanentRedirect):
    logout(request)
    return redirect("/")


@method_decorator(login_required, name="dispatch")
class PreferencesView(FormView[UserForm]):  # pylint:disable=unsubscriptable-object
    template_name = "user/preferences.html"
    form_class = UserForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        result = super().get_form_kwargs()
        result["instance"] = self.request.user
        return result

    def get_success_url(self) -> str:  # pylint:disable=no-self-use
        return reverse("preferences")

    def form_valid(self, form: UserForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)


class LoginErrorView(TemplateAnonymousView):
    template_name = "user/login_error.html"
