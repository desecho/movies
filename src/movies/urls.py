"""URL Configuration."""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import path
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
    # Search
    url(r'^$', SearchView.as_view(), name='search'),
    url(r'^search-movie/$', SearchMovieView.as_view(), name='search_movie'),
    url(r'^add-to-list-from-db$', AddToListFromDbView.as_view(), name='add_to_list_from_db'),

    # Vk
    url(r'^upload-poster-to-wall/$', UploadPosterToWallView.as_view(), name='upload_poster_to_wall'),

    # Accounts
    url(r'^accounts/login/', login, {'template_name': 'user/login.html'}, name='login'),
    url(r'^accounts/logout/', logout_view, name='logout'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    # Preferences
    url(r'^preferences/$', PreferencesView.as_view(), name='preferences'),
    url(r'^save-preferences/$', SavePreferencesView.as_view(), name='save_preferences'),

    # List
    url(r'^list/(?P<list_name>watched|to-watch)/$', ListView.as_view(), name='list'),
    url(r'^people/(?P<username>[\w\d]+)/(?P<list_name>watched|to-watch)$', ListView.as_view(), name='people'),
    url(r'^recommendations/$', RecommendationsView.as_view(), name='recommendations'),
    url(r'^apply-setting/$', ApplySettingsView.as_view(), name='apply_settings'),
    url(r'^remove-movie/$', RemoveMovieView.as_view(), name='remove_movie'),
    url(r'^add-to-list/$', AddToListView.as_view(), name='add_to_list'),
    url(r'^change-rating/$', ChangeRatingView.as_view(), name='change_rating'),
    url(r'^save-comment/$', SaveCommentView.as_view(), name='save_comment'),

    # Social
    url(r'^feed/(?P<list_name>people|friends)/$', FeedView.as_view(), name='feed'),
    url(r'^people/$', PeopleView.as_view(), name='people'),
    url(r'^friends/$', FriendsView.as_view(), name='friends'),

    # Admin
    path('admin/', admin.site.urls),

    # Services
    url(r'^jsi18n/$',
        JavaScriptCatalog.as_view(packages=('moviesapp', ), domain='djangojs'),
        name='javascript-catalog'),
    url('', include('social_django.urls', namespace='social')),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^djga/', include('google_analytics.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
