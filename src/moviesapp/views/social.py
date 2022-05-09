from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ..http import AuthenticatedHttpRequest, HttpRequest
from ..models import ActionRecord, User
from .mixins import TemplateAnonymousView, TemplateView
from .utils import paginate


class FeedView(TemplateAnonymousView):
    template_name = "social/feed.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        feed_name = kwargs["feed_name"]
        FEED_TITLE = {
            "people": _("People"),
            "friends": _("Friends"),
        }

        date_to = datetime.today()
        date_from = date_to - relativedelta(days=settings.FEED_DAYS)
        actions = ActionRecord.objects.filter(date__range=(date_from, date_to)).order_by("-pk")
        request: AuthenticatedHttpRequest = self.request  # type: ignore
        users = request.user.get_users(friends=feed_name == "friends")
        actions = actions.filter(user__in=users)
        posters = [action.movie.poster_small for action in actions]
        posters_2x = [action.movie.poster_normal for action in actions]
        actions_output = []

        i = 0
        for action in actions:
            action_ = {
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
            actions_output.append(action_)
            i += 1
        return {"feed_name": FEED_TITLE[feed_name], "actions": actions_output}


class PeopleView(TemplateAnonymousView):
    template_name = "social/people.html"
    users: Optional[List[User]] = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:  # pylint: disable=unused-argument
        # Users are supposed to be here already.
        if self.users:
            return {"users": paginate(self.users, self.request.GET.get("page"), settings.PEOPLE_ON_PAGE)}
        return {}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        self.users = request.user.get_users(sort=True)
        return super().get(request, *args, **kwargs)


class FriendsView(TemplateView, PeopleView):
    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        self.users = request.user.get_users(friends=True, sort=True)
        return TemplateView.get(self, request, *args, **kwargs)
