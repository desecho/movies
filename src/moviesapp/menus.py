# coding: utf-8

from __future__ import unicode_literals

from menu import Menu, MenuItem
from django.core.urlresolvers import reverse


def is_vk_user(request):
    try:
        return request.user.is_vk_user()
    except:
        return False

Menu.add_item('main', MenuItem('Просмотрено',
                               reverse('moviesapp.views.list_view',
                                       kwargs=({'list_name': 'watched'})),
                               weight=10,))

Menu.add_item('main', MenuItem('К просмотру',
                               reverse('moviesapp.views.list_view',
                                       kwargs=({'list_name': 'to-watch'})),
                               weight=10,))

Menu.add_item('main', MenuItem('Рекомендации',
                               reverse('moviesapp.views.recommendation'),
                               weight=10,))

Menu.add_item('main', MenuItem('Друзья',
                               reverse('moviesapp.views.friends'),
                               weight=20, check=is_vk_user))

Menu.add_item('main', MenuItem('Люди',
                               reverse('moviesapp.views.people'),
                               weight=20,))

feed_children = (
    MenuItem('Друзья',
             reverse('moviesapp.views.feed', kwargs=({'list_name': 'friends'})),
             weight=20,
             check=is_vk_user),

    MenuItem('Люди',
             reverse('moviesapp.views.feed', kwargs=({'list_name': 'people'})),
             weight=20),
)

Menu.add_item(
    'main',
    MenuItem('Лента',
             # doesn't really matter because of the submenus
             reverse('moviesapp.views.search'),
             weight=20,
             children=feed_children))
