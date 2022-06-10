"""Social views."""

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
    """Feed view."""

    template_name = "social/feed.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
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
        return {"feed_name": FEED_TITLE[feed_name], "action_records": action_records}


class PeopleView(TemplateAnonymousView):
    """People view."""

    template_name = "social/people.html"
    users: Optional[List[User]] = None

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:  # pylint: disable=unused-argument
        """Get context data."""
        # Users are supposed to be here already.
        if self.users:
            return {"users": paginate(self.users, self.request.GET.get("page"), settings.PEOPLE_ON_PAGE)}
        return {}

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
