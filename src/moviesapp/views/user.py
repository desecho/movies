"""User views."""

from http import HTTPStatus

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User

# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.utils.decorators import method_decorator
# from django.views.generic.edit import FormView

# from ..forms import UserDeleteForm, UserForm
# from ..http import HttpRequest
# from ..types import UntypedObject
# from .mixins import TemplateAnonymousView


# def logout_view(request: HttpRequest) -> (HttpResponseRedirect | HttpResponsePermanentRedirect):
#     """Return response for the logout view."""
#     logout(request)
#     return redirect("/")


# @method_decorator(login_required, name="dispatch")
# class PreferencesView(FormView[UserForm]):  # pylint:disable=unsubscriptable-object
#     """Preferences view."""

#     template_name = "user/preferences.html"
#     form_class = UserForm

#     def get_form_kwargs(self) -> UntypedObject:
#         """Get form kwargs."""
#         result = super().get_form_kwargs()
#         result["instance"] = self.request.user
#         return result

#     def get_success_url(self) -> str:  # pylint:disable=no-self-use
#         """Get success url."""
#         return reverse("preferences")

#     def form_valid(self, form: UserForm) -> HttpResponse:
#         """Redirect to the supplied URL if the form is valid."""
#         form.save()
#         return super().form_valid(form)


# @method_decorator(login_required, name="dispatch")
# class AccountDeleteView(FormView[UserDeleteForm]):  # pylint:disable=unsubscriptable-object
#     """Account delete view."""

#     template_name = "user/delete.html"
#     form_class = UserDeleteForm

#     def get_form_kwargs(self) -> UntypedObject:
#         """Get form kwargs."""
#         result = super().get_form_kwargs()
#         result["instance"] = self.request.user
#         return result

#     def get_success_url(self) -> str:  # pylint:disable=no-self-use
#         """Get success url."""
#         return reverse("account_deleted")

#     def form_valid(self, form: UserDeleteForm) -> HttpResponse:
#         """Redirect to the supplied URL if the form is valid."""
#         request = self.request
#         request.user.delete()
#         return super().form_valid(form)


# class LoginErrorView(TemplateAnonymousView):
#     """Login error view."""

#     template_name = "user/login_error.html"


# class AccountDeletedView(TemplateAnonymousView):
#     """Account deleted view."""

#     template_name = "user/account_deleted.html"


class UserCheckEmailAvailabilityView(APIView):
    """Check email availability view."""

    permission_classes: list[str] = []  # type: ignore

    def post(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Return True if email is available."""
        try:
            email = request.data["email"]
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)
        response = not User.objects.filter(email=email).exists()
        return Response(response)


class UserPreferencesView(APIView):
    """User preferences view."""

    def put(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Save preferences."""
        user: User = request.user  # type: ignore
        try:
            hidden = bool(request.data["hidden"])
        except (KeyError, ValueError):
            return Response(status=HTTPStatus.BAD_REQUEST)
        user.hidden = hidden
        user.save()
        return Response()

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Load preferences."""
        user: User = request.user  # type: ignore
        preferences = {"hidden": user.hidden}
        return Response(preferences)
