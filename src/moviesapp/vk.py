"""VK."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import QuerySet
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod

from .types import UntypedObject

if TYPE_CHECKING:
    from .models import User


class VkError(Exception):
    """VK error."""


def _get_vk_avatar(url: str) -> Optional[str]:
    """Get VK avatar."""
    if url in settings.VK_NO_AVATAR:
        return None
    return url


def update_user_vk_avatar(user: "User", data: Dict[str, Any]) -> "User":
    """Update user's VK avatar."""
    avatar_small = _get_vk_avatar(data["photo_100"])
    if avatar_small:
        user.avatar_small = avatar_small
    avatar_big = _get_vk_avatar(data["photo_200"])
    if avatar_big:
        user.avatar_big = avatar_big
    return user


class Vk:
    """VK."""

    vk: VkApiMethod = None

    def __init__(self, user: "User"):
        """Init."""
        vk_account = user.get_vk_account()
        if vk_account is not None:
            vk_session = VkApi(token=vk_account.access_token)
            self.vk = vk_session.get_api()
            self.vk_id = vk_account.uid
        self.user = user

    def get_friends(self) -> QuerySet["User"]:  # pylint: disable=no-self-use
        """Get friends."""
        vk_friends = cache.get("vk_friends")
        if vk_friends is None:
            if self.vk is not None:
                friends_ids = self.vk.friends.get()["items"]
                cache.set("vk_friends", vk_friends)
            else:
                friends_ids = []

        user_model: "User" = get_user_model()  # type: ignore
        return user_model.objects.filter(social_auth__provider=settings.VK_BACKEND, social_auth__uid__in=friends_ids)

    def get_data(self, fields: List[str]) -> UntypedObject:
        """Get data."""
        if self.vk is None:
            return {}
        data: List[UntypedObject] = self.vk.users.get(fields=fields)
        return data[0]

    def get_countries(self, country_codes: List[str]) -> Dict[str, int]:
        """
        Get countries.

        Returns a dict with country codes as keys and VK country IDs as values.
        """
        if self.vk is None:
            raise VkError("VK is not initialized")
        country_codes_string = ",".join(country_codes)
        vk_countries = self.vk.database.getCountries(code=country_codes_string, count=len(country_codes))["items"]
        countries = {}
        for i, country_code in enumerate(country_codes):
            vk_country = vk_countries[i]
            vk_country_id = vk_country["id"]
            # Make sure to skip countries with no VK country id
            # VK country id is 0 if the country is not found
            if vk_country_id:
                countries[country_code] = vk_country_id
        return countries
