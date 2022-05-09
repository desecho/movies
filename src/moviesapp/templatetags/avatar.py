import hashlib
from typing import Optional, Tuple
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.conf import settings
from django.utils.safestring import SafeString, mark_safe

from ..models import User

register = template.Library()


def _get_social_avatar_urls(user: User, size_type: str) -> Optional[Tuple[str, Optional[str]]]:
    if not user.avatar_small:
        return None
    if size_type == "small":
        return (user.avatar_small, user.avatar_small)
    return (user.avatar_small, user.avatar_big)


def _get_avatar_urls(
    user: User, size: float, social_avatars_urls: Optional[Tuple[str, Optional[str]]]
) -> Tuple[str, Optional[str]]:
    if social_avatars_urls is None:
        return _get_gravatar_urls(user, size)
    return social_avatars_urls


def _get_url(user: User, size: float) -> str:
    params = parse.urlencode({"s": str(size)})
    hash_ = hashlib.md5(user.email.lower().encode("utf-8")).hexdigest()  # nosec B324
    return f"https://www.gravatar.com/avatar/{hash_}?{params}"


def _get_gravatar_urls(user: User, size: float) -> Tuple[str, str]:
    url = _get_url(user, size)
    url_2x = _get_url(user, size * 2)
    return url, url_2x


@register.simple_tag
def avatar(user: User, size_type: str = "small") -> SafeString:
    size = settings.AVATAR_SIZES[size_type] / 2
    social_avatars_urls = _get_social_avatar_urls(user, size_type)
    url, url_2x = _get_avatar_urls(user, size, social_avatars_urls)
    return mark_safe(  # nosec B703 B308
        f'<img class="avatar-{size_type}" src="{url}" data-rjs="{url_2x}" width="{size}"'
        f'alt="{user}" title="{user}" @load="retinajs"></img>'
    )


@register.simple_tag
def avatar_big(user: User) -> SafeString:
    return avatar(user, "big")
