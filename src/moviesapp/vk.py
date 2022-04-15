from django.conf import settings


def _get_vk_avatar(url):
    if url in settings.VK_NO_AVATAR:
        return None
    return url


def update_user_vk_avatar(user, data):
    avatar_small = _get_vk_avatar(data["photo_100"])
    if avatar_small:
        user.avatar_small = avatar_small
    avatar_big = _get_vk_avatar(data["photo_200"])
    if avatar_big:
        user.avatar_big = avatar_big
    return user
