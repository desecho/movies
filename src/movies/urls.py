"""URL Configuration."""

# import debug_toolbar
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.defaults import page_not_found
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from moviesapp.types import URL
from moviesapp.views.health import HealthView
from moviesapp.views.list import (
    AddToListView,
    ChangeRatingView,
    RecordsView,
    RemoveRecordView,
    SaveCommentView,
    SaveOptionsView,
    SaveRecordsOrderView,
)
from moviesapp.views.search import AddToListFromDbView, SearchMovieView
from moviesapp.views.trending import TrendingView
from moviesapp.views.user import UserCheckEmailAvailabilityView, UserPreferencesView

# from moviesapp.views.user import AccountDeletedView, AccountDeleteView, LoginErrorView, PreferencesView, logout_view

admin.autodiscover()
# register_converter(ListConverter, "list")
# register_converter(FeedConverter, "feed")


def path_404(url_path: str, name: str) -> URL:
    """Return a path for 404."""
    return path(
        url_path,
        page_not_found,
        name=name,
        kwargs={"exception": Exception("Page not Found")},
    )


urlpatterns: list[URL] = [
    # Health
    path("health/", HealthView.as_view()),
    # Admin
    path("admin/", admin.site.urls),
    # Auth
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    # User
    path("user/", include("rest_registration.api.urls")),
    path("user/preferences/", UserPreferencesView.as_view()),
    path("user/check-email-availability/", UserCheckEmailAvailabilityView.as_view()),
    path("search/", SearchMovieView.as_view()),
    path("trending/", TrendingView.as_view(), name="trending"),
    path("add-to-list-from-db/", AddToListFromDbView.as_view()),
    # List
    path(
        "records/",
        RecordsView.as_view(),
    ),
    path("users/<str:username>/records/", RecordsView.as_view()),
    path_404("remove-record/", "remove_record"),
    path("remove-record/<int:record_id>/", RemoveRecordView.as_view()),
    path_404("record/", "record"),
    path("record/<int:record_id>/options/", SaveOptionsView.as_view()),
    path("save-records-order/", SaveRecordsOrderView.as_view()),
    path_404("add-to-list/", "add_to_list"),
    path("add-to-list/<int:movie_id>/", AddToListView.as_view()),
    path_404("change-rating/", "change_rating"),
    path("change-rating/<int:record_id>/", ChangeRatingView.as_view()),
    path_404("save-comment/", "save_comment"),
    path("save-comment/<int:record_id>/", SaveCommentView.as_view()),
]


# if settings.DEBUG:  # pragma: no cover
#     urlpatterns += [
#         # path("__debug__/", include(debug_toolbar.urls)),
#     ]

# urlpatterns += [
#     path("about/", AboutView.as_view(), name="about"),
#     #
#     # User
#     path("preferences/", PreferencesView.as_view(), name="preferences"),
#     path("account/delete/", AccountDeleteView.as_view(), name="delete_account"),
#     path("account/deleted/", AccountDeletedView.as_view(), name="account_deleted"),
#     #
#     # Search
#     path("", SearchView.as_view(), name="search"),
#     #
#     # Login
#     path("login/", LoginView.as_view(template_name="user/login.html"), name="login"),
#     path("logout/", logout_view, name="logout"),
#     path("login-error/", LoginErrorView.as_view(), name="login_error"),
#     #
#     # Trending
#     #
#     #
#     # Social
#     # path("feed/<feed:feed_name>/", FeedView.as_view(), name="feed"),
#     path("people/", PeopleView.as_view(), name="people"),
#     # path("friends/", FriendsView.as_view(), name="friends"),
#     #
#     # Admin
#     path("admin/", admin.site.urls),
#     #
#     # Services
#     # path("accounts/", include("registration.backends.default.urls")),
#     # path("", include("social_django.urls", namespace="social")),
#     path("", include("django.contrib.auth.urls")),
#     # path("rosetta/", include("rosetta.urls")),
#     # path("i18n/", include("django.conf.urls.i18n")),
# ]
