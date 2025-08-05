"""Trending view."""

from typing import TYPE_CHECKING

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
        for user in User.objects.all().exclude(hidden=True):
            avatar_url = user.avatar.url if user.avatar else None
            users.append({"username": user.username, "avatar_url": avatar_url})
        return Response(users)
