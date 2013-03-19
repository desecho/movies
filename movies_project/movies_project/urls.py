from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'applications_project.views.home', name='home'),
    # url(r'^applications_project/', include('applications_project.foo.urls')),
    url(r'^$', 'movies.views.search'),
    url(r'^search/$', 'movies.views.search'),

    url(r'^list/(?P<list>[\w-]+)/$', 'movies.views.list'),
    url(r'^people/$', 'movies.views.people'),
    url(r'^people/(?P<username>[\w\d]+)/(?P<list>[\w-]+)$', 'movies.views.list'),

    url(r'^remove-record/$', 'movies.views.ajax_remove_record'),
    url(r'^search-movie/$', 'movies.views.ajax_search_movie'),
    url(r'^add-to-list/$', 'movies.views.ajax_add_to_list'),
    url(r'^add-to-list-from-tmdb/$', 'movies.views.ajax_add_to_list_from_tmdb'),
    url(r'^save-comment/$', 'movies.views.ajax_save_comment'),
    url(r'^change-rating/$', 'movies.views.ajax_change_rating'),
    url(r'^apply-setting/$', 'movies.views.ajax_apply_setting'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'movies.views.logout_view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
