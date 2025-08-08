"""User views."""

from http import HTTPStatus
from typing import TYPE_CHECKING, cast

from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User
from ..serializers import AvatarUploadSerializer, UserPreferencesSerializer

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission

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


# class AccountDeletedView(TemplateAnonymousView):
#     """Account deleted view."""

#     template_name = "user/account_deleted.html"


class UserCheckEmailAvailabilityView(APIView):
    """Check email availability view."""

    permission_classes: list[type["BasePermission"]] = []

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
        user: User = cast(User, request.user)
        serializer = UserPreferencesSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(status=HTTPStatus.OK)

        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Load preferences."""
        user: User = cast(User, request.user)
        serializer = UserPreferencesSerializer(user)
        return Response(serializer.data)


class AvatarView(APIView):
    """Avatar view."""

    parser_classes = [MultiPartParser]

    def get(self, request: Request) -> Response:
        """Get current avatar information."""
        user: User = cast(User, request.user)
        avatar_url = user.avatar.url if user.avatar else None

        return Response({"avatar_url": avatar_url, "has_avatar": bool(user.avatar)}, status=HTTPStatus.OK)

    def post(self, request: Request) -> Response:
        """Upload avatar."""
        user: User = cast(User, request.user)
        serializer = AvatarUploadSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            avatar_url = user.avatar.url if user.avatar else None
            return Response({"avatar_url": avatar_url}, status=HTTPStatus.OK)

        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    def delete(self, request: Request) -> Response:
        """Delete avatar."""
        user: User = cast(User, request.user)

        if user.avatar:
            user.avatar.delete(save=True)
            return Response(status=HTTPStatus.NO_CONTENT)

        return Response({"error": "No avatar to delete"}, status=HTTPStatus.NOT_FOUND)
