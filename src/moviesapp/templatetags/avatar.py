import hashlib
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def avatar(user, size="small"):
    def get_social_avatar_urls():
        if not user.avatar_small:
            return None
        if size == "small":
            return (user.avatar_small, user.avatar_small)
        else:
            return (user.avatar_small, user.avatar_big)

    def get_gravatar_urls():
        def get_url(size):
            params = parse.urlencode({"s": str(size)})
            hash_ = hashlib.md5(user.email.lower().encode("utf-8")).hexdigest()  # nosec
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
    return mark_safe(  # nosec
        '<img class="avatar-{0}" src="{1}" data-rjs="{2}" width="{3}"'
        'alt="{4}" title="{4}" @load="retinajs"></img>'.format(size, url, url_2x, avatar_size, user)
    )


@register.simple_tag
def avatar_big(user):
    return avatar(user, "big")
