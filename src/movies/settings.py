# Django settings for movies project.

import os
import os.path as op
import sys

from django.utils.translation import ugettext_lazy as _

try:
    import local_settings
except ImportError:
    print("no local_settings!")
    sys.exit()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = local_settings.DATABASES

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [local_settings.PROJECT_DOMAIN]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'vk_iframe.middleware.IFrameFixMiddleware',
    # 'vk_iframe.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'vk_iframe.middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'movies.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'movies.wsgi.application'

TEMPLATE_DIRS = (
    BASE_DIR + '/templates',
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
    'moviesapp',
    # 'vk_iframe',
    'menu',
    'bootstrap_pagination',
    'rosetta',
    'modeltranslation',
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
    # 'vk_iframe.backends.VkontakteUserBackend',
)

ADMIN_REORDER = (
    ('moviesapp', ('User', 'Movie', 'Record', 'List', 'Action', 'ActionRecord')),
)

APPEND_SLASH = False

AUTH_USER_MODEL = 'moviesapp.User'
TEMPLATE_CONTEXT_PROCESSORS = ('django.core.context_processors.request',
                               'django.contrib.auth.context_processors.auth')
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
SESSION_SAVE_EVERY_REQUEST = True

STATIC_ROOT = op.join(local_settings.PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = op.join(local_settings.PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

CACHE_DIR = op.join(local_settings.PROJECT_ROOT, 'cache')
TMDB_CACHE_PATH = op.join(CACHE_DIR, 'tmdb3.cache')


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

VK_APP_ID = local_settings.VK_APP_ID
VK_APP_SECRET = local_settings.VK_APP_SECRET

TMDB_KEY = local_settings.TMDB_KEY

APPEND_SLASH = True

LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

LOCALE_PATHS = (
    op.join(local_settings.PROJECT_ROOT, 'project', 'src', 'locale'),
)
