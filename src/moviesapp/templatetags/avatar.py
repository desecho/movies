import hashlib
from typing import Tuple
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.conf import settings
from django.utils.safestring import SafeString, mark_safe

from moviesapp.models import User

register = template.Library()


@register.simple_tag
def avatar(user: User, size: str = "small") -> SafeString:
    def get_social_avatar_urls() -> Tuple[str, str]:
        if not user.avatar_small:
            return None
        if size == "small":
            return (user.avatar_small, user.avatar_small)
        return (user.avatar_small, user.avatar_big)

    def get_gravatar_urls() -> Tuple[str, str]:
        def get_url(size: int) -> str:
            params = parse.urlencode({"s": str(size)})
            hash_ = hashlib.md5(user.email.lower().encode("utf-8")).hexdigest()  # nosec B324
            return f"https://www.gravatar.com/avatar/{hash_}?{params}"

        url_2x = get_url(avatar_size * 2)
        url = get_url(avatar_size)
        return url, url_2x

    avatar_size = settings.AVATAR_SIZES[size] / 2
    social_avatars_urls = get_social_avatar_urls()
    if social_avatars_urls is None:
        url, url_2x = get_gravatar_urls()
    else:
        url, url_2x = social_avatars_urls
    return mark_safe(  # nosec B703 B308
        f'<img class="avatar-{size}" src="{url}" data-rjs="{url_2x}" width="{avatar_size}"'
        f'alt="{user}" title="{user}" @load="retinajs"></img>'
    )


@register.simple_tag
def avatar_big(user: User) -> SafeString:
    return avatar(user, "big")
