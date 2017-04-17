import hashlib
import urllib

from django import template

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

        params = urllib.urlencode({'s': str(avatar_size)})
        return 'https://www.gravatar.com/avatar/%s?%s' % (hashlib.md5(user.email.lower()).hexdigest(), params)

    avatar_size = AVATAR_SIZES[size]
    url = get_url()
    # Avatars will be always 2 times larger than the image shown to look good at retina displays
    avatar_size /= 2
    return '<img class="avatar-{0}" src="{1}" width="{2}" height="{2}" alt="{3}" title="{3}"></img>'.format(
        size, url, avatar_size, user)


@register.simple_tag
def avatar_big(user):
    return avatar(user, 'big')
