# -*- coding: utf8 -*-
from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

Menu.add_item('main', MenuItem(
    'Смотрел',
    reverse('movies.views.list', kwargs=({'list': 'watched'})),
    weight=10,))

Menu.add_item('main', MenuItem(
    'Хочу посмотреть',
    reverse('movies.views.list', kwargs=({'list': 'to-watch'})),
    weight=10,))

Menu.add_item('main', MenuItem(
    'Друзья',
    reverse('movies.views.friends'),
    weight=20,
    separator=True,))

Menu.add_item('main', MenuItem(
    'Люди',
    reverse('movies.views.people'),
    weight=20,))
