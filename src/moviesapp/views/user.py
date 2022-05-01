from typing import Any, Dict

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from moviesapp.forms import UserForm

from .mixins import TemplateAnonymousView


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("/")


@method_decorator(login_required, name="dispatch")
class PreferencesView(FormView):
    template_name = "user/preferences.html"
    form_class = UserForm

    def get_form_kwargs(self) -> Dict[str, Any]:
        result = super().get_form_kwargs()
        result["instance"] = self.request.user
        return result

    def get_success_url(self) -> str:
        return reverse("preferences")

    def form_valid(self, form: UserForm) -> HttpResponse:
        form.save()
        return super().form_valid(form)


class LoginErrorView(TemplateAnonymousView):
    template_name = "user/login_error.html"
