"""FB."""

# from typing import TYPE_CHECKING

# from django.contrib.auth import get_user_model
# from django.db.models import QuerySet
# from facebook import GraphAPI

# if TYPE_CHECKING:  # pylint: disable=duplicate-code
#     from .models import User


# class Fb:
#     """FB."""

#     def __init__(self, user: "User"):
#         """Init."""
#         access_token = user.get_fb_account().extra_data["access_token"]
#         self.fb = GraphAPI(access_token=access_token, version="2.7")

#     @staticmethod
#     def get_friends() -> QuerySet["User"]:
#         """Get friends from Facebook."""
#         user_model: "User" = get_user_model()  # type: ignore
#         return user_model.objects.none()
#         # fb_friends = cache.get("fb_friends")
#         # if fb_friends is None:
#         #     fb_friends = self.fb.get_connections(id="me", connection_name="friends")["data"]
#         #     cache.set("fb_friends", fb_friends)
#         # friends_ids = [f["id"] for f in fb_friends]
#         # user_model: "User" = get_user_model()  # type: ignore
#         # friends: QuerySet["User"] = user_model.objects.filter(
#         #     social_auth__provider="facebook", social_auth__uid__in=friends_ids
#         # ).exclude(hidden=True)
#         # return friends
