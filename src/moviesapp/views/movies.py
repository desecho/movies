from typing import Any, Dict, Optional

from .mixins import TemplateAnonymousView
from .utils import get_records, sort_by_rating


class AboutView(TemplateAnonymousView):
    template_name = "about.html"


class GalleryView(TemplateAnonymousView):
    template_name = "gallery.html"

    def get_context_data(self, list_name: str, username: Optional[str] = None) -> Dict[str, Any]:
        self.check_if_allowed(username)
        records = get_records(list_name, self.request.user, self.anothers_account)
        records = sort_by_rating(records, username, list_name)

        return {
            "records": records,
            "anothers_account": self.anothers_account,
            "list": list_name,
        }
