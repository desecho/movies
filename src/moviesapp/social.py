from django.conf import settings

from .vk import update_user_vk_avatar


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
        user = update_user_vk_avatar(user, data)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        # Language setting is only available for a standalone application. See details:
        # https://vk.com/dev/account.getProfileInfo
        # We assume that the language is Russian.
        user.language = "ru"
        user.loaded_initial_data = True
        user.save()
    return None
