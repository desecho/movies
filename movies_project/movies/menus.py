# -*- coding: utf8 -*-
from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

Menu.add_item('main', MenuItem('Просмотрено',
    reverse('movies.views.list', kwargs=({'list': 'watched'})),
    weight=10,))

Menu.add_item('main', MenuItem('К просмотру',
    reverse('movies.views.list', kwargs=({'list': 'to-watch'})),
    weight=10,))

Menu.add_item('main', MenuItem('Рекомендации',
    reverse('movies.views.recommendation'),
    weight=10,))

Menu.add_item('main', MenuItem('Друзья',
    reverse('movies.views.friends'),
    weight=20,))

Menu.add_item('main', MenuItem('Люди',
    reverse('movies.views.people'),
    weight=20,))

feed_children = (
    MenuItem('Друзья',
        reverse('movies.views.feed', kwargs=({'list': 'friends'})),
        weight=20,),
    MenuItem('Люди',
        reverse('movies.views.feed', kwargs=({'list': 'people'})),
        weight=20,),
)

Menu.add_item('main', MenuItem('Лента',
    reverse('movies.views.search'),  # doesn't really matter because of the submenus
    weight=20,
    children=feed_children))
