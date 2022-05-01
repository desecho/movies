from typing import Any, Dict, Tuple

import vk_api
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import QuerySet


def _get_vk_avatar(url):
    if url in settings.VK_NO_AVATAR:
        return None
    return url


def update_user_vk_avatar(user: "get_user_model()", data: Dict[str, Any]) -> "get_user_model()":
    avatar_small = _get_vk_avatar(data["photo_100"])
    if avatar_small:
        user.avatar_small = avatar_small
    avatar_big = _get_vk_avatar(data["photo_200"])
    if avatar_big:
        user.avatar_big = avatar_big
    return user


class Vk:
    def __init__(self, user: "get_user_model()"):
        vk_account = user.get_vk_account()
        vk_session = vk_api.VkApi(token=vk_account.access_token)
        self.vk = vk_session.get_api()
        self.vk_id = vk_account.uid
        self.user = user

    def get_friends(self) -> QuerySet["get_user_model()"]:  # pylint: disable=no-self-use
        friends = cache.get("vk_friends")
        if friends is None:
            friends_ids = self.vk.friends.get()["items"]
            cache.set("vk_friends", friends)

        # We need to use distinct here because the same user can have several VK backends (both app and oauth)
        friends = (
            get_user_model()
            .objects.filter(social_auth__provider__in=settings.VK_BACKENDS, social_auth__uid__in=friends_ids)
            .distinct()
        )
        return friends

    def get_data(self, fields: Tuple[str]):
        return self.vk.users.get(fields=fields)[0]
