import hashlib
from urllib import parse  # pylint: disable=no-name-in-module

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def avatar(user, size='small'):
    AVATAR_SIZES = {
        'small': 100,
        'big': 200
    }

    def get_url():
        if user.avatar:
            if size == 'small':
                return user.avatar
            elif size == 'big':
                return user.avatar_big

        params = parse.urlencode({'s': str(avatar_size)})
        hash_ = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/%s?%s' % (hash_, params)

    avatar_size = AVATAR_SIZES[size]
    url = get_url()
    # Avatars will be always 2 times larger than the image shown to look good at retina displays
    avatar_size /= 2
    return mark_safe('<img class="avatar-{0}" src="{1}" width="{2}" height="{2}" alt="{3}" title="{3}"></img>'.format(
        size, url, avatar_size, user))


@register.simple_tag
def avatar_big(user):
    return avatar(user, 'big')
