"""Context processors."""

from django.conf import settings

from .http import HttpRequest
from .types import ContextVariables


def variables(request: HttpRequest) -> ContextVariables:  # pylint: disable=unused-argument
    """Add variables to the context."""
    admin_email: str = settings.ADMIN_EMAIL  # type: ignore
    google_analytics_id: str = settings.GOOGLE_ANALYTICS_ID  # type: ignore
    return {
        "DEBUG": settings.DEBUG,
        "ADMIN_EMAIL": admin_email,
        "GOOGLE_ANALYTICS_ID": google_analytics_id,
    }
