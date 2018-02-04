# -*- coding: utf-8 -*-
"""Django settings."""

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

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Development
IS_VK_DEV = local_settings.IS_VK_DEV

# Debug
DEBUG = local_settings.DEBUG
INTERNAL_IPS = local_settings.INTERNAL_IPS
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

MENU_SELECT_PARENTS = True
SECRET_KEY = local_settings.SECRET_KEY
ADMINS = ((local_settings.ADMIN_NAME, local_settings.ADMIN_EMAIL), )
MANAGERS = ADMINS
DATABASES = local_settings.DATABASES
CACHE_DIR = op.join(local_settings.PROJECT_ROOT, 'cache')
SITE_ID = 1
ROOT_URLCONF = 'movies.urls'
WSGI_APPLICATION = 'movies.wsgi.application'
SESSION_SAVE_EVERY_REQUEST = True

# Allowed hosts
ALLOWED_HOSTS = [local_settings.PROJECT_DOMAIN]
if IS_VK_DEV:
    ALLOWED_HOSTS.append(local_settings.HOST_MOVIES_TEST)

# Internationalization
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Русский'),
)
LOCALE_PATHS = (op.join(local_settings.PROJECT_ROOT, 'project', 'src', 'locale'), )

# Timezone
TIME_ZONE = 'US/Eastern'
USE_TZ = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'), ),
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
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
            'debug':
            DEBUG
        },
    },
]
if DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'custom_anonymous.middleware.AuthenticationMiddleware',
]
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

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
    INSTALLED_APPS += [
        'debug_toolbar',
        'template_timings_panel',
    ]

# Logging
RAVEN_CONFIG = {
    'dsn': local_settings.RAVEN_DSN,
    'release': raven.fetch_git_sha(local_settings.GIT_ROOT),
}
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
                'format': ('%(levelname)s %(asctime)s %(module)s '
                           '%(process)d %(thread)d %(message)s')
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {
                    'custom-tag': 'x'
                },
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

# Admin
ADMIN_REORDER = (('moviesapp', ('User', 'Movie', 'Record', 'List', 'Action', 'ActionRecord')), )

# Authentication
AUTH_USER_MODEL = 'moviesapp.User'
AUTH_ANONYMOUS_MODEL = 'moviesapp.models.UserAnonymous'
AUTHENTICATION_BACKENDS = (
    'social_core.backends.vk.VKOAuth2',
    'social_core.backends.vk.VKAppOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
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

    # We might want to enable it
    # # Update the user record with any changed info from the auth service.
    # 'social_core.pipeline.user.user_details',

    # We do this only if the user get's created for the first time.
    'moviesapp.social.load_user_data',
)
# Login
LOGIN_REDIRECT_URL = '/'
if IS_VK_DEV:
    LOGIN_REDIRECT_URL = 'https://{}'.format(local_settings.HOST_MOVIES_TEST)
LOGIN_URL = '/login/'
LOGIN_ERROR_URL = '/login-error/'

# Static files
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATIC_ROOT = op.join(local_settings.PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# Media files
MEDIA_ROOT = op.join(local_settings.PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

# Internationalization
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Русский'),
)
LOCALE_PATHS = (op.join(local_settings.PROJECT_ROOT, 'project', 'locale'), )

# Timezone
TIME_ZONE = 'US/Eastern'
USE_TZ = True

# --== Project settings ==--

# Search settings
MAX_RESULTS = 50
MIN_POPULARITY = 1.5

# Posters
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
GOOGLE_ANALYTICS_ID = local_settings.GOOGLE_ANALYTICS_ID

# Secrets
SOCIAL_AUTH_VK_OAUTH2_KEY = local_settings.SOCIAL_AUTH_VK_OAUTH2_KEY
SOCIAL_AUTH_VK_OAUTH2_SECRET = local_settings.SOCIAL_AUTH_VK_OAUTH2_SECRET
SOCIAL_AUTH_VK_APP_KEY = local_settings.SOCIAL_AUTH_VK_APP_KEY
SOCIAL_AUTH_VK_APP_SECRET = local_settings.SOCIAL_AUTH_VK_APP_SECRET
SOCIAL_AUTH_FACEBOOK_KEY = local_settings.SOCIAL_AUTH_FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET = local_settings.SOCIAL_AUTH_FACEBOOK_SECRET

# Social
SOCIAL_AUTH_VK_APP_USER_MODE = 2
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['friends', 'email']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_friends', 'public_profile', 'user_location']

VK_BACKENDS_CREDENTIALS = {
    'vk-app': (SOCIAL_AUTH_VK_APP_KEY, SOCIAL_AUTH_VK_APP_SECRET),
    'vk-oauth2': (SOCIAL_AUTH_VK_OAUTH2_KEY, SOCIAL_AUTH_VK_OAUTH2_SECRET)
}
VK_BACKENDS = VK_BACKENDS_CREDENTIALS.keys()

# API Keys
TMDB_KEY = local_settings.TMDB_KEY
OMDB_KEY = local_settings.OMDB_KEY

# This is here to fix the problem with static files on dev
try:
    from local_settings2 import *  # noqa pylint: disable=wildcard-import
except ImportError:
    pass
