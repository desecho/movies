# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from menu import Menu, MenuItem


def is_linked(request):
    user = request.user
    if user.is_authenticated():
        return user.is_linked()


Menu.add_item('main', MenuItem(_('Watched'), reverse('moviesapp.views.list_view', kwargs={'list_name': 'watched'})))

Menu.add_item('main', MenuItem(_('To Watch'),
                               reverse('moviesapp.views.list_view', kwargs={'list_name': 'to-watch'})))

Menu.add_item('main', MenuItem(_('Recommendations'), reverse('moviesapp.views.recommendation')))

Menu.add_item('main', MenuItem(_('Friends'),
                               reverse('moviesapp.views.friends'), check=is_linked))

Menu.add_item('main', MenuItem(_('People'),
                               reverse('moviesapp.views.people')))

feed_children = (
    MenuItem(_('Friends'),
             reverse('moviesapp.views.feed', kwargs={'list_name': 'friends'}), check=is_linked),

    MenuItem(_('People'),
             reverse('moviesapp.views.feed', kwargs={'list_name': 'people'}))
)

Menu.add_item(
    'main',
    MenuItem(_('Feed'),
             'moviesapp.views.search',
             children=feed_children))
