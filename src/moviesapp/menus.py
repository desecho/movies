from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

from .http import HttpRequest

# def has_friends(request: HttpRequest) -> bool:
#     return request.user.has_friends()


def is_authenticated(request: HttpRequest) -> bool:
    return request.user.is_authenticated


feed_children = (
    # MenuItem(_("Friends"), reverse("feed", kwargs={"feed_name": "friends"}), check=has_friends),
    MenuItem(_("People"), reverse("feed", kwargs={"feed_name": "people"})),
)

Menu.add_item("main", MenuItem(_("Search"), reverse("search")))
Menu.add_item("main", MenuItem(_("Watched"), reverse("list", kwargs={"list_name": "watched"}), check=is_authenticated))
Menu.add_item(
    "main", MenuItem(_("To Watch"), reverse("list", kwargs={"list_name": "to-watch"}), check=is_authenticated)
)
# Menu.add_item("main", MenuItem(_("Recommendations"), reverse("recommendations"), check=has_friends))
# Menu.add_item("main", MenuItem(_("Friends"), reverse("friends"), check=has_friends))
Menu.add_item("main", MenuItem(_("People"), reverse("people")))
Menu.add_item("main", MenuItem(_("Feed"), "moviesapp.views.search", children=feed_children))
