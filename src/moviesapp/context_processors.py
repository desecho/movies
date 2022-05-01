from typing import Dict, Union

from django.conf import settings
from django.http import HttpRequest


def variables(request: HttpRequest) -> Dict[str, Union[bool, str]]:  # pylint: disable=unused-argument
    admin_email: str = settings.ADMIN_EMAIL  # type: ignore
    google_analytics_id: str = settings.GOOGLE_ANALYTICS_ID  # type: ignore
    return {
        "DEBUG": settings.DEBUG,
        "ADMIN_EMAIL": admin_email,
        "GOOGLE_ANALYTICS_ID": google_analytics_id,
    }
