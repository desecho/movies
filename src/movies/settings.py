# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import os.path as op
import sys

import raven

try:
    import local_settings
except ImportError:
    try:
        from . import initial_settings as local_settings
    except ImportError:
        print('No initial settings!')
        sys.exit()

INTERNAL_IPS = local_settings.INTERNAL_IPS

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = local_settings.DEBUG
IS_VK_DEV = local_settings.IS_VK_DEV

ADMINS = (
    (local_settings.ADMIN_NAME, local_settings.ADMIN_EMAIL),
)

MANAGERS = ADMINS

DATABASES = local_settings.DATABASES

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [local_settings.PROJECT_DOMAIN]

if IS_VK_DEV:
    ALLOWED_HOSTS.append(local_settings.HOST_MOVIES_TEST)

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'moviesapp.context_processors.variables',
            ),
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            'debug': DEBUG
        },
    },
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'custom_anonymous.middleware.AuthenticationMiddleware',
]

if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'movies.urls'

WSGI_APPLICATION = 'movies.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'moviesapp',
    'menu',
    'bootstrap_pagination',
    'rosetta',
    'modeltranslation',
    'social_django',
    'raven.contrib.django.raven_compat',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }

AUTHENTICATION_BACKENDS = (
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.vk.VKAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ADMIN_REORDER = (
    ('moviesapp', ('User', 'Movie', 'Record', 'List', 'Action', 'ActionRecord')),
)

APPEND_SLASH = False

AUTH_USER_MODEL = 'moviesapp.User'
AUTH_ANONYMOUS_MODEL = 'moviesapp.models.UserAnonymous'

LOGIN_REDIRECT_URL = '/'
if IS_VK_DEV:
    LOGIN_REDIRECT_URL = 'https://{}'.format(local_settings.HOST_MOVIES_TEST)
LOGIN_URL = '/login/'

SESSION_SAVE_EVERY_REQUEST = True

STATIC_ROOT = op.join(local_settings.PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = op.join(local_settings.PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

CACHE_DIR = op.join(local_settings.PROJECT_ROOT, 'cache')

MAX_RESULTS = 50
MIN_POPULARITY = 50

NO_POSTER_SMALL_IMAGE_URL = STATIC_URL + 'img/no_poster_small.png'
NO_POSTER_NORMAL_IMAGE_URL = STATIC_URL + 'img/no_poster_normal.png'

# Available sizes:
# "w92",
# "w154",
# "w185",
# "w342",
# "w500",
# "w780",
# "original"

POSTER_SIZE_SMALL = 'w92'
POSTER_SIZE_NORMAL = 'w185'
POSTER_SIZE_BIG = 'w500'
POSTER_BASE_URL = 'http://image.tmdb.org/t/p/'

IMDB_BASE_URL = 'http://www.imdb.com/title/'
MAX_RECOMMENDATIONS = 50
RECORDS_ON_PAGE = 50
PEOPLE_ON_PAGE = 25
FEED_DAYS = 7

# CACHE_TIMEOUT = 60 * 60 * 12
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'movies_dev'
#     }
# }

MENU_SELECT_PARENTS = True

SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    # # Update the user record with any changed info from the auth service.
    # 'social_core.pipeline.user.user_details',

    # We do this only if the user get's created for the first time.
    'moviesapp.social.load_user_data',
)

LOGIN_ERROR_URL = '/login-error/'

GOOGLE_ANALYTICS_ID = local_settings.GOOGLE_ANALYTICS_ID

SOCIAL_AUTH_VK_OAUTH2_KEY = local_settings.SOCIAL_AUTH_VK_OAUTH2_KEY
SOCIAL_AUTH_VK_OAUTH2_SECRET = local_settings.SOCIAL_AUTH_VK_OAUTH2_SECRET
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['friends', 'email']

SOCIAL_AUTH_VK_APP_KEY = local_settings.SOCIAL_AUTH_VK_APP_KEY
SOCIAL_AUTH_VK_APP_SECRET = local_settings.SOCIAL_AUTH_VK_APP_SECRET
SOCIAL_AUTH_VK_APP_USER_MODE = 2

VK_BACKENDS_CREDENTIALS = {
    'vk-app': (SOCIAL_AUTH_VK_APP_KEY, SOCIAL_AUTH_VK_APP_SECRET),
    'vk-oauth2': (SOCIAL_AUTH_VK_OAUTH2_KEY, SOCIAL_AUTH_VK_OAUTH2_SECRET)
}

VK_BACKENDS = VK_BACKENDS_CREDENTIALS.keys()

SOCIAL_AUTH_FACEBOOK_KEY = local_settings.SOCIAL_AUTH_FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET = local_settings.SOCIAL_AUTH_FACEBOOK_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_friends', 'public_profile', 'user_location']

TMDB_KEY = local_settings.TMDB_KEY

APPEND_SLASH = True

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Русский'),
)

LOCALE_PATHS = (
    op.join(local_settings.PROJECT_ROOT, 'project', 'src', 'locale'),
)
RAVEN_CONFIG = {
    'dsn': local_settings.RAVEN_DSN,
    'release': raven.fetch_git_sha(local_settings.GIT_ROOT),
}

# This is here to fix the problem with static files on dev
try:
    from local_settings2 import *  # noqa pylint: disable=wildcard-import
except ImportError:
    pass
