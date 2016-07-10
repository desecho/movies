from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'moviesapp.views.search'),
    url(r'^search/$', 'moviesapp.views.search'),

    url(r'^list/(?P<list_name>[\w-]+)/$', 'moviesapp.views.list_view'),
    url(r'^people/$', 'moviesapp.views.people'),
    url(r'^friends/$', 'moviesapp.views.friends'),
    url(r'^feed/(?P<list_name>[\w-]+)/$', 'moviesapp.views.feed'),
    url(r'^people/(?P<username>[\w\d]+)/(?P<list_name>[\w-]+)$',
        'moviesapp.views.list_username'),
    url(r'^recommendation/$', 'moviesapp.views.recommendation'),
    url(r'^preferences/$', TemplateView.as_view(template_name='preferences.html')),

    url(r'^remove-record/$', 'moviesapp.views.ajax_remove_record'),
    url(r'^search-movie/$', 'moviesapp.views.ajax_search_movie'),
    url(r'^add-to-list/$', 'moviesapp.views.ajax_add_to_list'),
    url(r'^add-to-list-from-db$', 'moviesapp.views.ajax_add_to_list_from_db'),
    url(r'^save-comment/$', 'moviesapp.views.ajax_save_comment'),
    url(r'^change-rating/$', 'moviesapp.views.ajax_change_rating'),
    url(r'^apply-setting/$', 'moviesapp.views.ajax_apply_settings'),
    # url(r'^download/$', 'moviesapp.views.ajax_download'),
    url(r'^upload-photo-to-wall/$', 'moviesapp.views.ajax_upload_photo_to_wall'),
    url(r'^save-preferences/$', 'moviesapp.views.ajax_save_preferences'),

    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}),
    url(r'^logout/$', 'moviesapp.views.logout_view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
