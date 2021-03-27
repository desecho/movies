from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import FormView

from moviesapp.forms import UserForm
from moviesapp.models import activate_user_language_preference

from .mixins import TemplateAnonymousView


def logout_view(request):
    logout(request)
    return redirect("/")


class PreferencesView(FormView):
    template_name = "user/preferences.html"
    form_class = UserForm

    def get_form_kwargs(self):
        result = super().get_form_kwargs()
        result["instance"] = self.request.user
        return result

    def get_success_url(self):
        return reverse("preferences")

    def form_valid(self, form):
        if "language" in form.changed_data:
            activate_user_language_preference(self.request, form.cleaned_data["language"])
        form.save()
        return super().form_valid(form)


class LoginErrorView(TemplateAnonymousView):
    template_name = "user/login_error.html"
