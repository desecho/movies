"""Users views."""

from typing import TYPE_CHECKING

from django.http import Http404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class UsersView(APIView):
    """Users view."""

    permission_classes: list[type["BasePermission"]] = []

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Return a list of users."""
        users = []
        # Optimize query to select avatar field to avoid N+1 queries
        for user in User.objects.select_related().exclude(hidden=True):
            avatar_url = user.avatar.url if user.avatar else None
            users.append({"username": user.username, "avatar_url": avatar_url})

        response = Response(users)
        response["Cache-Control"] = "public, max-age=1800"
        return response


class UserAvatarView(APIView):
    """User avatar view."""

    permission_classes: list[type["BasePermission"]] = []

    def get(self, request: Request, username: str) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Return a specific user's avatar information."""
        try:
            user = User.objects.get(username=username, hidden=False)
        except User.DoesNotExist as exc:
            raise Http404("User not found") from exc

        avatar_url = user.avatar.url if user.avatar else None
        response = Response({"username": user.username, "avatar_url": avatar_url})

        # Add cache headers for performance
        response["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour
        response["ETag"] = f'"{username}-{user.id}"'

        return response
