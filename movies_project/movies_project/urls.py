from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'movies.views.search'),
    url(r'^search/$', 'movies.views.search'),

    url(r'^list/(?P<list>[\w-]+)/$', 'movies.views.list'),
    url(r'^people/$', 'movies.views.people'),
    url(r'^friends/$', 'movies.views.friends'),
    url(r'^feed/(?P<list>[\w-]+)/$', 'movies.views.feed'),
    url(r'^people/(?P<username>[\w\d]+)/(?P<list>[\w-]+)$', 'movies.views.list'),
    url(r'^recommendation/$', 'movies.views.recommendation'),

    url(r'^remove-record/$', 'movies.views.ajax_remove_record'),
    url(r'^search-movie/$', 'movies.views.ajax_search_movie'),
    url(r'^add-to-list/$', 'movies.views.ajax_add_to_list'),
    url(r'^add-to-list-from-db/$', 'movies.views.ajax_add_to_list_from_db'),
    url(r'^save-comment/$', 'movies.views.ajax_save_comment'),
    url(r'^change-rating/$', 'movies.views.ajax_change_rating'),
    url(r'^apply-setting/$', 'movies.views.ajax_apply_settings'),
    url(r'^download/$', 'movies.views.ajax_download'),
    url(r'^upload-photo-to-wall/$', 'movies.views.ajax_upload_photo_to_wall'),

    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'movies.views.logout_view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
