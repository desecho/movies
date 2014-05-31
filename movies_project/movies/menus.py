# -*- coding: utf8 -*-
from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

def is_vk_user(request):
    try:
        return request.user.is_vk_user()
    except:
        return False

Menu.add_item('main', MenuItem('Просмотрено',
    reverse('movies.views.list_view', kwargs=({'list_name': 'watched'})),
    weight=10,))

Menu.add_item('main', MenuItem('К просмотру',
    reverse('movies.views.list_view', kwargs=({'list_name': 'to-watch'})),
    weight=10,))

Menu.add_item('main', MenuItem('Рекомендации',
    reverse('movies.views.recommendation'),
    weight=10,))

Menu.add_item('main', MenuItem('Друзья',
    reverse('movies.views.friends'),
    weight=20, check=is_vk_user))

Menu.add_item('main', MenuItem('Люди',
    reverse('movies.views.people'),
    weight=20,))

feed_children = (
    MenuItem('Друзья',
        reverse('movies.views.feed', kwargs=({'list_name': 'friends'})),
        weight=20,
        check=is_vk_user), #for some reason doesn't work

    MenuItem('Люди',
        reverse('movies.views.feed', kwargs=({'list_name': 'people'})),
        weight=20),
)

Menu.add_item('main', MenuItem('Лента',
    reverse('movies.views.search'),  # doesn't really matter because of the submenus
    weight=20,
    children=feed_children))