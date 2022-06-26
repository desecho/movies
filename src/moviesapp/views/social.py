"""Social views."""

from datetime import datetime
from typing import Any, List

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.paginator import Page
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from ..http import AuthenticatedHttpRequest, HttpRequest
from ..models import ActionRecord, User
from .mixins import TemplateAnonymousView, TemplateView
from .types import FeedViewContextData, PeopleViewContextData
from .utils import paginate


class FeedView(TemplateAnonymousView):
    """Feed view."""

    template_name = "social/feed.html"

    def get_context_data(self, **kwargs: Any) -> FeedViewContextData:  # type: ignore
        """Get context data."""
        feed_name = kwargs["feed_name"]
        FEED_TITLE = {
            "people": _("People"),
            "friends": _("Friends"),
        }

        date_to = datetime.today()
        date_from = date_to - relativedelta(days=settings.FEED_DAYS)
        action_records = ActionRecord.objects.filter(date__range=(date_from, date_to)).order_by("-pk")
        request: AuthenticatedHttpRequest = self.request  # type: ignore
        users = request.user.get_users(friends=feed_name == "friends")
        action_records = action_records.filter(user__in=users).select_related("movie", "action", "user", "list")
        data: FeedViewContextData = {"feed_name": FEED_TITLE[feed_name], "action_records": action_records}
        return data


class PeopleView(TemplateAnonymousView):
    """People view."""

    template_name = "social/people.html"
    users: List[User] = list(User.objects.none())

    def get_context_data(self, **kwargs: Any) -> PeopleViewContextData:  # type: ignore  # pylint: disable=unused-argument
        """Get context data."""
        users: Page[User] | List[User] = paginate(  # type: ignore
            self.users, self.request.GET.get("page"), settings.PEOPLE_ON_PAGE
        )
        return {"users": users}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        """Get."""
        self.users = request.user.get_users(sort=True)
        return super().get(request, *args, **kwargs)


class FriendsView(TemplateView, PeopleView):
    """Friends view."""

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        """Get."""
        self.users = request.user.get_users(friends=True, sort=True)
        return TemplateView.get(self, request, *args, **kwargs)
