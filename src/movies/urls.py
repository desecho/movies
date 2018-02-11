"""URL Configuration."""

import django
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import path, re_path
from django.views.i18n import JavaScriptCatalog

from moviesapp.views.list import (
    AddToListView,
    ApplySettingsView,
    ChangeRatingView,
    ListView,
    RecommendationsView,
    RemoveMovieView,
    SaveCommentView,
)

from moviesapp.views import AboutView

from moviesapp.views.search import (
    AddToListFromDbView,
    SearchMovieView,
    SearchView,
)
from moviesapp.views.social import FeedView, FriendsView, PeopleView
from moviesapp.views.user import (
    PreferencesView,
    SavePreferencesView,
    logout_view,
)
from moviesapp.views.vk import UploadPosterToWallView

admin.autodiscover()

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    # Search
    path('', SearchView.as_view(), name='search'),
    path('search-movie/', SearchMovieView.as_view(), name='search_movie'),
    path('add-to-list-from-db/', AddToListFromDbView.as_view(), name='add_to_list_from_db'),

    # Vk
    path('upload-poster-to-wall/', UploadPosterToWallView.as_view(), name='upload_poster_to_wall'),

    # Accounts
    path('accounts/login/', login, {'template_name': 'user/login.html'}, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('registration.backends.default.urls')),

    # Preferences
    path('preferences/', PreferencesView.as_view(), name='preferences'),
    path('save-preferences/', SavePreferencesView.as_view(), name='save_preferences'),

    # List
    re_path('list/(?P<list_name>watched|to-watch)/', ListView.as_view(), name='list'),
    re_path(r'people/(?P<username>[\w\d]+)/(?P<list_name>watched|to-watch)', ListView.as_view(), name='people'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    path('apply-setting/', ApplySettingsView.as_view(), name='apply_settings'),
    path('remove-movie/', django.views.defaults.page_not_found, name='remove_movie'),
    re_path(r'remove-movie/(?P<id>\d+)/', RemoveMovieView.as_view(), name='remove_movie'),
    path('add-to-list/', AddToListView.as_view(), name='add_to_list'),
    path('change-rating/', ChangeRatingView.as_view(), name='change_rating'),
    path('save-comment/', SaveCommentView.as_view(), name='save_comment'),

    # Social
    re_path('feed/(?P<list_name>people|friends)/', FeedView.as_view(), name='feed'),
    path('people/', PeopleView.as_view(), name='people'),
    path('friends/', FriendsView.as_view(), name='friends'),

    # Admin
    path('admin/', admin.site.urls),

    # Services
    path('jsi18n/',
        JavaScriptCatalog.as_view(packages=('moviesapp', ), domain='djangojs'),
        name='javascript-catalog'),
    path('', include('social_django.urls', namespace='social')),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('djga/', include('google_analytics.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
