"""VK."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import QuerySet
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod

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
        # We need to use distinct here because the same user can have several VK backends (both app and oauth)
        friends = user_model.objects.filter(
            social_auth__provider__in=settings.VK_BACKENDS, social_auth__uid__in=friends_ids
        ).distinct()
        return friends

    def get_data(self, fields: Union[Tuple[str, str, str, str], Tuple[str, str]]) -> Dict[str, Union[str, bool, int]]:
        """Get data."""
        if self.vk is None:
            return {}
        data: List[Dict[str, Union[str, bool, int]]] = self.vk.users.get(fields=fields)
        return data[0]
