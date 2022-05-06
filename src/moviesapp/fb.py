from typing import TYPE_CHECKING

import facebook
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import QuerySet

if TYPE_CHECKING:  # pylint: disable=duplicate-code
    from moviesapp.models import User


class Fb:
    def __init__(self, user: "User"):
        access_token = user.get_fb_account().extra_data["access_token"]
        self.fb = facebook.GraphAPI(access_token=access_token, version="2.7")

    def get_friends(self) -> QuerySet["User"]:
        friends = cache.get("fb_friends")
        if friends is None:
            friends = self.fb.get_connections(id="me", connection_name="friends")["data"]
            cache.set("fb_friends", friends)
        friends_ids = [f["id"] for f in friends]
        user_model: "User" = get_user_model()  # type: ignore
        friends = user_model.objects.filter(social_auth__provider="facebook", social_auth__uid__in=friends_ids)
        return friends  # type: ignore
