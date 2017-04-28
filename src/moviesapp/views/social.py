# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ..models import ActionRecord
from .mixins import TemplateAnonymousView, TemplateView
from .utils import paginate


def get_users(user, friends=False, sort=False):
    if friends:
        return user.get_friends(sort=sort)
    else:
        return user.get_available_users_and_friends(sort=sort)


class FeedView(TemplateAnonymousView):
    template_name = 'social/feed.html'

    def get_context_data(self, list_name):
        FEED_TITLE = {
            'people': _('People'),
            'friends': _('Friends'),
        }

        date_to = datetime.today()
        date_from = date_to - relativedelta(days=settings.FEED_DAYS)
        actions = ActionRecord.objects.filter(
            date__range=(date_from, date_to)).order_by('-pk')

        users = get_users(self.request.user, friends=list_name == 'friends')
        actions = actions.filter(user__in=users)
        posters = [action.movie.poster_small for action in actions]
        actions_output = []

        i = 0
        for action in actions:
            a = {
                'user': action.user,
                'action': action,
                'movie': action.movie,
                'movie_poster': posters[i],
                'list': action.list,
                'comment': action.comment,
                'rating': action.rating,
                'date': action.date,
            }
            actions_output.append(a)
            i += 1
        return {'list_name': FEED_TITLE[list_name],
                'actions': actions_output}


class PeopleView(TemplateAnonymousView):
    template_name = 'social/people.html'
    users = None

    def get_context_data(self):
        return {'users': paginate(self.users, self.request.GET.get('page'),
                                  settings.PEOPLE_ON_PAGE)}

    def get(self, *args, **kwargs):
        self.users = get_users(self.request.user, sort=True)
        return super(PeopleView, self).get(*args, **kwargs)


class FriendsView(TemplateView, PeopleView):
    def get(self, *args, **kwargs):
        self.users = get_users(self.request.user, friends=True, sort=True)
        return TemplateAnonymousView.get(self, *args, **kwargs)
