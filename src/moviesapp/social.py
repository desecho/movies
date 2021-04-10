# -*- coding: utf-8 -*-

from django.conf import settings

from .vk import get_vk_avatar


def load_user_data(backend, user, **kwargs):  # pylint: disable=unused-argument
    if user.loaded_initial_data:
        return None

    if backend.name in settings.VK_BACKENDS:
        # We don't need the username and email because they are already loaded.
        FIELDS = (
            "first_name",
            "last_name",
            "photo_100",
            "photo_200",
        )
        vk = user.get_vk()
        data = vk.get_data(FIELDS)
        avatar_small = get_vk_avatar(data["photo_100"])
        if avatar_small:
            user.avatar_small = avatar_small
        avatar_big = get_vk_avatar(data["photo_200"])
        if avatar_big:
            user.avatar_big = avatar_big
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        # Language setting is only available for a standalone application. See details:
        # https://vk.com/dev/account.getProfileInfo
        # We assume that the language is Russian.
        user.language = "ru"
        user.loaded_initial_data = True
        user.save()
