"""Views for movies."""
from typing import Any

from ..http import HttpRequest
from .mixins import TemplateAnonymousView
from .types import GalleryViewContextData, ListKeyName
from .utils import get_records, sort_by_rating


class AboutView(TemplateAnonymousView):
    """About view."""

    template_name = "about.html"


class GalleryView(TemplateAnonymousView):
    """Gallery view."""

    template_name = "gallery.html"

    def get_context_data(self, **kwargs: Any) -> GalleryViewContextData:  # type: ignore
        """Get context data."""
        list_name: ListKeyName = kwargs["list_name"]
        username = kwargs.get("username")
        self.check_if_allowed(username)
        request: HttpRequest = self.request  # type: ignore
        user = request.user if self.anothers_account is None else self.anothers_account
        records = get_records(list_name, user)
        records = sort_by_rating(records, username, list_name)

        return {
            "records": records,
            "anothers_account": self.anothers_account,
            "list": list_name,
        }
