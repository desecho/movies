"""Social."""
from typing import Any

from django.conf import settings
from sentry_sdk import capture_exception
from social_core.backends.base import BaseAuth

from .exceptions import VkCountryNotFoundError
from .models import User, VkCountry
from .vk import update_user_vk_avatar


def _get_country_from_vk_country_id(vk_country_id: int) -> str:
    """Get country from VK country ID."""
    vk_countries = VkCountry.objects.filter(pk=vk_country_id)
    if not vk_countries.exists():
        raise VkCountryNotFoundError(vk_country_id)
    vk_country: VkCountry = vk_countries.first()  # type: ignore
    country: str = vk_country.country
    return country


def load_user_data(backend: BaseAuth, user: User, **kwargs: Any) -> None:  # pylint: disable=unused-argument
    """Load user data."""
    if user.loaded_initial_data:
        return None

    if backend.name == settings.VK_BACKEND:
        # We don't need the username and email because they are already loaded.
        FIELDS = [
            "first_name",
            "last_name",
            "photo_100",
            "photo_200",
            "country",
        ]
        vk = user.get_vk()
        if vk:
            data = vk.get_data(FIELDS)
            user = update_user_vk_avatar(user, data)
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            try:
                country = _get_country_from_vk_country_id(data["country"]["id"])
            except VkCountryNotFoundError as e:
                if settings.DEBUG:
                    raise
                capture_exception(e)
            else:
                user.country = country
            # Language setting is only available for a standalone application. See details:
            # https://dev.vk.com/method/account.getInfo
            # We assume that the language is Russian.
            user.language = "ru"
            user.loaded_initial_data = True
            user.save()
    return None
