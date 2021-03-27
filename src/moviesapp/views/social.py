# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from moviesapp.models import ActionRecord

from .mixins import TemplateAnonymousView, TemplateView
from .utils import paginate


class FeedView(TemplateAnonymousView):
    template_name = "social/feed.html"

    def get_context_data(self, list_name):
        FEED_TITLE = {
            "people": _("People"),
            "friends": _("Friends"),
        }

        date_to = datetime.today()
        date_from = date_to - relativedelta(days=settings.FEED_DAYS)
        actions = ActionRecord.objects.filter(date__range=(date_from, date_to)).order_by("-pk")

        users = self.request.user.get_users(friends=list_name == "friends")
        actions = actions.filter(user__in=users)
        posters = [action.movie.poster_small for action in actions]
        posters_2x = [action.movie.poster_normal for action in actions]
        actions_output = []

        i = 0
        for action in actions:
            a = {
                "user": action.user,
                "action": action,
                "movie": action.movie,
                "movie_poster": posters[i],
                "movie_poster_2x": posters_2x[i],
                "list": action.list,
                "comment": action.comment,
                "rating": action.rating,
                "date": action.date,
            }
            actions_output.append(a)
            i += 1
        return {"list_name": FEED_TITLE[list_name], "actions": actions_output}


class PeopleView(TemplateAnonymousView):
    template_name = "social/people.html"
    users = None

    def get_context_data(self):
        return {"users": paginate(self.users, self.request.GET.get("page"), settings.PEOPLE_ON_PAGE)}

    def get(self, *args, **kwargs):
        self.users = self.request.user.get_users(sort=True)
        return super().get(*args, **kwargs)


class FriendsView(TemplateView, PeopleView):
    def get(self, *args, **kwargs):
        self.users = self.request.user.get_users(friends=True, sort=True)
        return TemplateAnonymousView.get(self, *args, **kwargs)
