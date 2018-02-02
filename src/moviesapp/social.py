# -*- coding: utf-8 -*-

from django.conf import settings

from .models import Vk


def load_user_data(backend, user, **kwargs):  # pylint: disable=unused-argument
    if user.loaded_initial_data:
        return None

    if backend.name in settings.VK_BACKENDS:
        # We don't need the username and email because they are already loaded
        FIELDS = ('first_name', 'last_name')
        data = Vk(user).get_data(FIELDS)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.language = 'ru'
        user.loaded_initial_data = True
        user.save()
