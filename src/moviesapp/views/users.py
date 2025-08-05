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
        users = User.objects.all().exclude(hidden=True).values_list("username", flat=True)
        return Response(users)
