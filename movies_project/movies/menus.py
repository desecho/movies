# -*- coding: utf8 -*-
from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

Menu.add_item('main', MenuItem(
    'Просмотрено',
    reverse('movies.views.list', kwargs=({'list': 'watched'})),
    weight=10,))

Menu.add_item('main', MenuItem(
    'К просмотру',
    reverse('movies.views.list', kwargs=({'list': 'to-watch'})),
    weight=10,))

Menu.add_item('main', MenuItem(
    'Рекомендации',
    reverse('movies.views.recommendation'),
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

Menu.add_item('main', MenuItem(
    'Лента',
    reverse('movies.views.feed'),
    weight=20,))