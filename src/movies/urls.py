"""URL Configuration."""

from typing import List, Union

import debug_toolbar
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import URLPattern, URLResolver, path, register_converter
from django.views.defaults import page_not_found
from django.views.i18n import JavaScriptCatalog

from moviesapp.converters import FeedConverter, ListConverter
from moviesapp.views.about import AboutView
from moviesapp.views.gallery import GalleryView
from moviesapp.views.list import (
    AddToListView,
    ChangeRatingView,
    ListView,
    RemoveRecordView,
    SaveCommentView,
    SaveOptionsView,
    SaveRecordsOrderView,
    SaveSettingsView,
)
from moviesapp.views.search import AddToListFromDbView, SearchMovieView, SearchView
from moviesapp.views.social import FeedView, FriendsView, PeopleView
from moviesapp.views.trending import TrendingView
from moviesapp.views.user import AccountDeletedView, AccountDeleteView, LoginErrorView, PreferencesView, logout_view

# from moviesapp.views.vk import UploadPosterToWallView

admin.autodiscover()
register_converter(ListConverter, "list")
register_converter(FeedConverter, "feed")

URL = Union[URLPattern, URLResolver]
URLList = List[URL]

urlpatterns: URLList = []


def path_404(url_path: str, name: str) -> URL:
    """Return a path for 404."""
    return path(
        url_path,
        page_not_found,
        name=name,
        kwargs={"exception": Exception("Page not Found")},
    )


if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += [
    path("about/", AboutView.as_view(), name="about"),
    #
    # User
    path("preferences/", PreferencesView.as_view(), name="preferences"),
    path("account/delete/", AccountDeleteView.as_view(), name="delete_account"),
    path("account/deleted/", AccountDeletedView.as_view(), name="account_deleted"),
    #
    # Search
    path("", SearchView.as_view(), name="search"),
    path("search-movie/", SearchMovieView.as_view(), name="search_movie"),
    path("add-to-list-from-db/", AddToListFromDbView.as_view(), name="add_to_list_from_db"),
    #
    # Login
    path("login/", LoginView.as_view(template_name="user/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("login-error/", LoginErrorView.as_view(), name="login_error"),
    #
    # Trending
    path("trending/", TrendingView.as_view(), name="trending"),
    #
    # Vk
    path_404("upload-poster-to-wall/", "upload_poster_to_wall"),
    # path("upload-poster-to-wall/<int:record_id>/", UploadPosterToWallView.as_view(), name="upload_poster_to_wall"),
    #
    # Gallery
    path("gallery/<list:list_name>/", GalleryView.as_view(), name="gallery"),
    path("<str:username>/gallery/<list:list_name>/", GalleryView.as_view(), name="gallery"),
    #
    # List
    path("list/<list:list_name>/", ListView.as_view(), name="list"),
    path("<str:username>/list/<list:list_name>/", ListView.as_view(), name="list"),
    #
    # Commented out because friends functionality is disabled
    # path("recommendations/", RecommendationsView.as_view(), name="recommendations"),
    path("save-settings/", SaveSettingsView.as_view(), name="save_settings"),
    #
    path_404("remove-record/", "remove_record"),
    path("remove-record/<int:record_id>/", RemoveRecordView.as_view(), name="remove_record"),
    #
    path_404("record/", "record"),
    path("record/<int:record_id>/options/", SaveOptionsView.as_view(), name="save_options"),
    #
    path("save-records-order/", SaveRecordsOrderView.as_view(), name="save_records_order"),
    #
    path_404("add-to-list/", "add_to_list"),
    path("add-to-list/<int:movie_id>/", AddToListView.as_view(), name="add_to_list"),
    #
    path_404("change-rating/", "change_rating"),
    path("change-rating/<int:record_id>/", ChangeRatingView.as_view(), name="change_rating"),
    #
    path_404("save-comment/", "save_comment"),
    path("save-comment/<int:record_id>/", SaveCommentView.as_view(), name="save_comment"),
    #
    # Social
    path("feed/<feed:feed_name>/", FeedView.as_view(), name="feed"),
    path("people/", PeopleView.as_view(), name="people"),
    path("friends/", FriendsView.as_view(), name="friends"),
    #
    # Admin
    path("admin/", admin.site.urls),
    #
    # Services
    path("accounts/", include("registration.backends.default.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(packages=("moviesapp",), domain="djangojs"), name="javascript-catalog"),
    path("", include("social_django.urls", namespace="social")),
    path("", include("django.contrib.auth.urls")),
    path("rosetta/", include("rosetta.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]
