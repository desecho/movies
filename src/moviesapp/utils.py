# coding: utf-8
from __future__ import unicode_literals

from django.utils.translation import activate, LANGUAGE_SESSION_KEY
from django.conf import settings


def activate_user_language_preference(request, lang):
    activate(lang)
    request.session[LANGUAGE_SESSION_KEY] = lang


def get_poster_url(size, poster):
    if size == 'small':
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == 'normal':
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == 'big':
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = None
    if poster is not None:
        return settings.POSTER_BASE_URL + poster_size + '/' + poster
    else:
        return no_image_url
