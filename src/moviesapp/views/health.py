"""Health views."""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Health view."""

    permission_classes: list[str] = []  # type: ignore

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use,unused-argument
        """Return health status."""
        return Response({"status": "ok"})
