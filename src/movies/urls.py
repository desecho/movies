"""URL Configuration."""

import django
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import path, re_path
from django.views.i18n import JavaScriptCatalog

from moviesapp.views import AboutView, GalleryView
from moviesapp.views.list import (
    AddToListView,
    ChangeRatingView,
    ListView,
    RecommendationsView,
    RemoveRecordView,
    SaveCommentView,
    SaveOptionsView,
    SaveSettingsView,
)
from moviesapp.views.search import (
    AddToListFromDbView,
    SearchMovieView,
    SearchView,
)
from moviesapp.views.social import FeedView, FriendsView, PeopleView
from moviesapp.views.user import LoginErrorView, PreferencesView, logout_view
from moviesapp.views.vk import UploadPosterToWallView

admin.autodiscover()

urlpatterns = [
    path('about/', AboutView.as_view(), name='about'),
    path('preferences/', PreferencesView.as_view(), name='preferences'),

    # Search
    path('', SearchView.as_view(), name='search'),
    path('search-movie/', SearchMovieView.as_view(), name='search_movie'),
    path('add-to-list-from-db/', AddToListFromDbView.as_view(), name='add_to_list_from_db'),

    # Login
    path('login/', login, {'template_name': 'user/login.html'}, name='login'),
    path('logout/', logout_view, name='logout'),
    path('login-error/', LoginErrorView.as_view(), name='login_error'),

    # Vk
    path(
        'upload-poster-to-wall/',
        django.views.defaults.page_not_found,
        name='upload_poster_to_wall',
        kwargs={'exception': Exception('Page not Found')}),
    re_path(r'upload-poster-to-wall/(?P<id>\d+)/', UploadPosterToWallView.as_view(), name='upload_poster_to_wall'),

    # Gallery
    re_path('gallery/(?P<list_name>watched|to-watch)/', GalleryView.as_view(), name='gallery'),
    re_path(r'(?P<username>[\w\d]+)/gallery/(?P<list_name>watched|to-watch)', GalleryView.as_view(), name='gallery'),

    # List
    re_path('list/(?P<list_name>watched|to-watch)/', ListView.as_view(), name='list'),
    re_path(r'(?P<username>[\w\d]+)/list/(?P<list_name>watched|to-watch)', ListView.as_view(), name='list'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    path('save-settings/', SaveSettingsView.as_view(), name='save_settings'),
    path(
        'remove-record/',
        django.views.defaults.page_not_found,
        name='remove_record',
        kwargs={'exception': Exception('Page not Found')}),
    re_path(r'remove-record/(?P<id>\d+)/', RemoveRecordView.as_view(), name='remove_record'),
    path(
        'record/',
        django.views.defaults.page_not_found,
        name='record',
        kwargs={'exception': Exception('Page not Found')}),
    re_path(r'record/(?P<id>\d+)/options/', SaveOptionsView.as_view(), name='save_options'),
    path(
        'add-to-list/',
        django.views.defaults.page_not_found,
        name='add_to_list',
        kwargs={'exception': Exception('Page not Found')}),
    re_path(r'add-to-list/(?P<id>\d+)/', AddToListView.as_view(), name='add_to_list'),
    path(
        'change-rating/',
        django.views.defaults.page_not_found,
        name='change_rating',
        kwargs={'exception': Exception('Page not Found')}),
    re_path(r'change-rating/(?P<id>\d+)/', ChangeRatingView.as_view(), name='change_rating'),
    path('save-comment/', SaveCommentView.as_view(), name='save_comment'),

    # Social
    re_path('feed/(?P<list_name>people|friends)/', FeedView.as_view(), name='feed'),
    path('people/', PeopleView.as_view(), name='people'),
    path('friends/', FriendsView.as_view(), name='friends'),

    # Admin
    path('admin/', admin.site.urls),

    # Services
    path('accounts/', include('registration.backends.default.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=('moviesapp', ), domain='djangojs'), name='javascript-catalog'),
    path('', include('social_django.urls', namespace='social')),
    path('', include('django.contrib.auth.urls')),
    path('rosetta/', include('rosetta.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('djga/', include('google_analytics.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
