import hashlib
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def avatar(user, size='small'):
    def get_url():
        params = parse.urlencode({'s': str(avatar_size)})
        hash_ = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()  # nosec
        return f'https://www.gravatar.com/avatar/{hash_}?{params}'

    avatar_size = settings.AVATAR_SIZES[size]
    url_2x = get_url()
    # Avatars will be always 2 times larger than the image shown to look good at retina displays
    avatar_size /= 2
    url = get_url()
    return mark_safe('<img class="avatar-{0}" src="{1}" data-rjs="{2}" width="{3}" height="{3}"'  # nosec
                     'alt="{4}" title="{4}"></img>'.format(size, url, url_2x, avatar_size, user))


@register.simple_tag
def avatar_big(user):
    return avatar(user, 'big')
