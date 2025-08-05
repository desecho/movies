"""Health views."""

from typing import TYPE_CHECKING

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class HealthView(APIView):
    """Health view."""

    permission_classes: list[type["BasePermission"]] = []

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Return health status."""
        return Response({"status": "ok"})
