# Django settings for movies_project project.

import os
import django

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                       # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                       # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                       # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

DJANGO_DIR = os.path.dirname(os.path.realpath(django.__file__))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CACHE_DIR = BASE_DIR + '/cache/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = BASE_DIR + '/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = BASE_DIR + '/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    DJANGO_DIR + '/contrib/admin/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

try:
    from secret import SECRET_KEY
except ImportError:
    def gen_secret_key():
        here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))
        print "Django's SECRET_KEY not found, generating new."
        from random import choice
        secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        f = open(here('secret.py'), 'w')
        f.write('''# Make this unique, and don't share it with anybody.\nSECRET_KEY = '%s'\n''' % secret_key)
        f.close()
    gen_secret_key()
    from secret import SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'vk_iframe.middleware.IFrameFixMiddleware',
    'vk_iframe.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'vk_iframe.middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'movies_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'movies_project.wsgi.application'

TEMPLATE_DIRS = (
    BASE_DIR + '/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'movies',
    'vk_iframe',
    'menu',
    'bootstrap-pagination',
    'south',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'vk_iframe.backends.VkontakteUserBackend',
)

ADMIN_REORDER = (
    ('movies', ('User', 'Movie', 'Record', 'List', 'Action', 'ActionRecord')),
)

APPEND_SLASH = False

AUTH_USER_MODEL = 'movies.User'
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth')
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
SESSION_SAVE_EVERY_REQUEST = True
TMDB_CACHE_PATH = CACHE_DIR + 'tmdb3.cache'
MAX_RESULTS = 100
MIN_POPULARITY = 50
NO_POSTER_SMALL_IMAGE_URL = STATIC_URL + 'img/no_poster_small.jpg'
NO_POSTER_NORMAL_IMAGE_URL = STATIC_URL + 'img/no_poster_normal.jpg'
POSTER_SIZE_SMALL = 'w92'
POSTER_SIZE_NORMAL = 'w185'
POSTER_SIZE_BIG = 'w500'
POSTER_BASE_URL = 'http://image.tmdb.org/t/p/'
IMDB_BASE_URL = 'http://www.imdb.com/title/'
MAX_RECOMMENDATIONS = 50
RECORDS_ON_PAGE = 50
PEOPLE_ON_PAGE = 25
FEED_DAYS = 7
LOCALES = {'ru': ('ru', 'ru'),
           'en': ('en', 'US')}

# CACHE_TIMEOUT = 60 * 60 * 12
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'movies_dev'
#     }
# }

VK_P3P_POLICY = 'IDC DSP COR IVAi IVDi OUR TST'
VK_IMAGE_PATH = 'http://vk.com/images/'
VK_NO_IMAGE_SMALL = VK_IMAGE_PATH + 'camera_c.gif'
VK_NO_IMAGE_MEDIUM = VK_IMAGE_PATH + 'camera_b.gif'
VK_NO_IMAGE_BIG = VK_IMAGE_PATH + 'camera_a.gif'
MENU_SELECT_PARENTS = True

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass
