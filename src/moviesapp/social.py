# -*- coding: utf-8 -*-

from django.conf import settings

from .vk import get_vk_avatar


def load_user_data(backend, user, **kwargs):  # pylint: disable=unused-argument
    def get_vk_country(id_):
        country = vk.vk.getCountries(cids=id_, lang=settings.VK_EN)
        if country:
            return country[0]['name']
        return None

    def get_vk_city(id_):
        city = vk.vk.getCities(cids=id_, lang=settings.VK_EN)
        if city:
            return city[0]['name']
        return None

    if user.loaded_initial_data:
        return None

    if backend.name in settings.VK_BACKENDS:
        # We don't need the username and email because they are already loaded.
        FIELDS = (
            'first_name',
            'last_name',
            'city',
            'country',
            'photo_medium',
            'photo_big',
        )
        vk = user.get_vk()
        data = vk.get_data(FIELDS)
        avatar_small = get_vk_avatar(data['photo_medium'])
        if avatar_small:
            user.avatar_small = avatar_small
        avatar_big = get_vk_avatar(data['photo_big'])
        if avatar_big:
            user.avatar_big = avatar_big
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.language = 'ru'

        country = get_vk_country(data['country'])
        city = get_vk_city(data['city'])
        if country and city:
            location = f'{city}, {country}'
        elif city:
            location = city
        elif country:
            location = country
        user.location = location
        user.loaded_initial_data = True
        user.save()
