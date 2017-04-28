# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from menu import Menu, MenuItem


def is_linked(request):
    user = request.user
    if user.is_authenticated():
        return user.is_linked()


Menu.add_item('main', MenuItem(_('Watched'), reverse('list', kwargs={'list_name': 'watched'})))

Menu.add_item('main', MenuItem(_('To Watch'), reverse('list', kwargs={'list_name': 'to-watch'})))

Menu.add_item('main', MenuItem(_('Recommendations'), reverse('recommendations')))

Menu.add_item('main', MenuItem(_('Friends'), reverse('friends'), check=is_linked))

Menu.add_item('main', MenuItem(_('People'), reverse('people')))

feed_children = (
    MenuItem(_('Friends'), reverse('feed', kwargs={'list_name': 'friends'}), check=is_linked),

    MenuItem(_('People'), reverse('feed', kwargs={'list_name': 'people'}))
)

Menu.add_item(
    'main',
    MenuItem(_('Feed'),
             'moviesapp.views.search',
             children=feed_children))
