from django.conf import settings


def get_vk_avatar(url):
    if url in settings.VK_NO_AVATAR:
        return None
    return url
