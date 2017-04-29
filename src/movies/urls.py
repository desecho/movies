from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login
from django.views.i18n import javascript_catalog
from moviesapp.views.list import (AddToListView, ApplySettingsView,
                                  ChangeRatingView, ListView,
                                  RecommendationsView, RemoveMovieView,
                                  SaveCommentView)
from moviesapp.views.search import (AddToListFromDbView, SearchMovieView,
                                    SearchView)
from moviesapp.views.social import FeedView, FriendsView, PeopleView
from moviesapp.views.user import (PreferencesView, SavePreferencesView,
                                  logout_view)
from moviesapp.views.vk import UploadPosterToWallView

admin.autodiscover()

urlpatterns = [
    # Search
    url(r'^$', SearchView.as_view(), name='search'),
    url(r'^search-movie/$', SearchMovieView.as_view(), name='search_movie'),
    url(r'^add-to-list-from-db$', AddToListFromDbView.as_view(), name='add_to_list_from_db'),

    # Vk
    url(r'^upload-poster-to-wall/$', UploadPosterToWallView.as_view(), name='upload_poster_to_wall'),

    # User
    url(r'^login/$', login, {'template_name': 'user/login.html'}, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    # -= Preferences =-
    url(r'^preferences/$', PreferencesView.as_view(), name='preferences'),
    url(r'^save-preferences/$', SavePreferencesView.as_view(), name='save_preferences'),

    # List
    url(r'^apply-setting/$', ApplySettingsView.as_view(), name='apply_settings'),
    url(r'^remove-movie/$', RemoveMovieView.as_view(), name='remove_movie'),
    url(r'^add-to-list/$', AddToListView.as_view(), name='add_to_list'),
    url(r'^change-rating/$', ChangeRatingView.as_view(), name='change_rating'),
    url(r'^save-comment/$', SaveCommentView.as_view(), name='save_comment'),
    url(r'^list/(?P<list_name>[\w-]+)/$', ListView.as_view(), name='list'),
    url(r'^recommendations/$', RecommendationsView.as_view(), name='recommendations'),
    url(r'^people/(?P<username>[\w\d]+)/(?P<list_name>[\w-]+)$',
        ListView.as_view(), name='people'),

    # Social
    url(r'^feed/(?P<list_name>[\w-]+)/$', FeedView.as_view(), name='feed'),
    url(r'^people/$', PeopleView.as_view(), name='people'),
    url(r'^friends/$', FriendsView.as_view(), name='friends'),

    # Admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Services
    url(r'^jsi18n/$', javascript_catalog, {
        'domain': 'djangojs',
        'packages': ('movies',)}, name='javascript-catalog'),

    url('', include('social_django.urls', namespace='social')),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
