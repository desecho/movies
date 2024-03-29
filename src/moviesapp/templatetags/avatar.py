"""Template tags for avatar."""

import hashlib
from typing import Optional
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.conf import settings
from django.utils.safestring import SafeString, mark_safe

from ..models import User

register = template.Library()


def _get_social_avatar_urls(user: User, size_type: str) -> Optional[tuple[str, Optional[str]]]:
    """Get avatar URLs from social accounts."""
    if not user.avatar_small:
        return None
    if size_type == "small":
        return (user.avatar_small, user.avatar_small)
    return (user.avatar_small, user.avatar_big)


def _get_avatar_urls(
    user: User, size: float, social_avatars_urls: Optional[tuple[str, Optional[str]]]
) -> tuple[str, Optional[str]]:
    """Get avatar URLs."""
    if social_avatars_urls is None:
        return _get_gravatar_urls(user, size)
    return social_avatars_urls


def _get_gravatar_url(user: User, size: float) -> str:
    """Get Gravatar URL."""
    params = parse.urlencode({"s": str(size)})
    hash_ = hashlib.md5(user.email.lower().encode("utf-8")).hexdigest()  # nosec B324
    return f"https://www.gravatar.com/avatar/{hash_}?{params}"


def _get_gravatar_urls(user: User, size: float) -> tuple[str, str]:
    """Get Gravatar URLs."""
    url = _get_gravatar_url(user, size)
    url_2x = _get_gravatar_url(user, size * 2)
    return url, url_2x


@register.simple_tag
def avatar(user: User, size_type: str = "small") -> SafeString:
    """Get avatar HTML snippet."""
    size = settings.AVATAR_SIZES[size_type] / 2
    social_avatars_urls = _get_social_avatar_urls(user, size_type)
    url, url_2x = _get_avatar_urls(user, size, social_avatars_urls)
    html = (
        f'<v-lazy-image class="avatar-{size_type}" srcset="{url} 1x, {url_2x} 2x" src="{url_2x}" width="{size}" '
        f'title="{user}" alt="{user}" />'
    )
    return mark_safe(html)  # nosec B703 B308


@register.simple_tag
def avatar_big(user: User) -> SafeString:
    """Get big avatar HTML snippet."""
    return avatar(user, "big")
