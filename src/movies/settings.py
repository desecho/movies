"""Django settings."""

from os import getenv
from os.path import abspath, dirname, join
from typing import Any, Dict, List

import django_stubs_ext
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

django_stubs_ext.monkeypatch()

SENTRY_TRACE_SAMPLING = 0.5

sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
    dsn=getenv("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=SENTRY_TRACE_SAMPLING,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# Custom
IS_DEV = bool(getenv("IS_DEV"))
IS_VK_DEV = bool(getenv("IS_VK_DEV"))
COLLECT_STATIC = bool(getenv("COLLECT_STATIC"))
SRC_DIR = dirname(dirname(abspath(__file__)))
PROJECT_DIR = dirname(SRC_DIR)
PROJECT_DOMAIN = getenv("PROJECT_DOMAIN")

# Debug
DEBUG = bool(getenv("DEBUG"))
INTERNAL_IPS = [getenv("INTERNAL_IP")]

ADMIN_EMAIL = getenv("ADMIN_EMAIL")
SECRET_KEY = getenv("SECRET_KEY")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "movies",
        "USER": getenv("DB_USER"),
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
ROOT_URLCONF = "movies.urls"
WSGI_APPLICATION = "movies.wsgi.application"
SESSION_SAVE_EVERY_REQUEST = True
SITE_ID = 1

# Email
EMAIL_USE_SSL = bool(getenv("EMAIL_USE_SSL", "True"))
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(getenv("EMAIL_PORT", "465"))
DEFAULT_FROM_EMAIL = ADMIN_EMAIL

# Allowed hosts
ALLOWED_HOSTS = [PROJECT_DOMAIN]
if IS_VK_DEV:  # pragma: no cover
    ALLOWED_HOSTS.append(getenv("HOST_MOVIES_TEST"))

# Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = (
    ("en", "English"),
    ("ru", "Русский"),
)
LOCALE_PATHS = (join(SRC_DIR, "locale"),)

# Timezone
TIME_ZONE = "US/Eastern"
USE_TZ = True

TEMPLATES: List[Dict[str, Any]] = [
    {
        "NAME": "Main",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (join(SRC_DIR, "templates"),),
        "OPTIONS": {
            "context_processors": (
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                # social_django
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                # Movies
                "moviesapp.context_processors.variables",
            ),
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "debug": DEBUG,
            "builtins": ["django.templatetags.static", "django.templatetags.i18n"],
        },
    },
    {
        "NAME": "Secondary",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
        },
    },
]
if IS_DEV:  # pragma: no cover
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # We disable this to make VK iframe app work
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom
    "django.middleware.gzip.GZipMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "custom_anonymous.middleware.AuthenticationMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
    "moviesapp.middleware.AjaxHandlerMiddleware",
    "moviesapp.middleware.language_middleware",
]
if DEBUG:  # pragma: no cover
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Custom
    "django.contrib.sites",
    "registration",
    "menu",
    "admin_reorder",
    "bootstrap_pagination",
    "rosetta",
    "modeltranslation",
    "social_django",
    "moviesapp",
]
if DEBUG:  # pragma: no cover
    INSTALLED_APPS += [
        "debug_toolbar",
        "template_timings_panel",
    ]

if IS_DEV or COLLECT_STATIC:  # pragma: no cover
    INSTALLED_APPS.append("django.contrib.staticfiles")

# Security
DISABLE_CSRF = bool(getenv("DISABLE_CSRF"))
if not DISABLE_CSRF:  # pragma: no cover
    # It is needed for VK app to work.
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [f"https://{PROJECT_DOMAIN}"]

# Authentication
AUTH_USER_MODEL = "moviesapp.User"
AUTH_ANONYMOUS_MODEL = "moviesapp.models.UserAnonymous"
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    # social_core
    "social_core.backends.vk.VKOAuth2",
    "social_core.backends.vk.VKAppOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
)
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Login
LOGIN_REDIRECT_URL = "/"
if IS_VK_DEV:  # pragma: no cover
    HOST_MOVIES_TEST = getenv("HOST_MOVIES_TEST")
    LOGIN_REDIRECT_URL = f"https://{HOST_MOVIES_TEST}"
LOGIN_URL = "/login/"
LOGIN_ERROR_URL = "/login-error/"

# Static files
if IS_DEV:  # pragma: no cover
    STATICFILES_DIRS = (join(SRC_DIR, "moviesapp", "static"),)
    STATIC_ROOT = None
else:
    STATIC_ROOT = join(PROJECT_DIR, "static")

STATIC_URL = getenv("STATIC_URL", "/static/")

# Media files
MEDIA_ROOT = join(PROJECT_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# --== Modules settings ==--

# django-registration-redux
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_FORM = "registration.forms.RegistrationFormUniqueEmail"
REGISTRATION_AUTO_LOGIN = True

# social-auth-app-django
SOCIAL_AUTH_VK_OAUTH2_KEY = getenv("SOCIAL_AUTH_VK_OAUTH2_KEY")
SOCIAL_AUTH_VK_OAUTH2_SECRET = getenv("SOCIAL_AUTH_VK_OAUTH2_SECRET")
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ["friends", "email", "offline"]

SOCIAL_AUTH_VK_APP_KEY = getenv("SOCIAL_AUTH_VK_APP_KEY")
SOCIAL_AUTH_VK_APP_SECRET = getenv("SOCIAL_AUTH_VK_APP_SECRET")
SOCIAL_AUTH_VK_APP_USER_MODE = 2

SOCIAL_AUTH_FACEBOOK_KEY = getenv("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = getenv("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email", "user_friends", "public_profile"]

SOCIAL_AUTH_USER_MODEL = AUTH_USER_MODEL
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    "social_core.pipeline.user.get_username",
    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    "social_core.pipeline.social_auth.associate_by_email",
    # Create a user account if we haven't found one yet.
    "social_core.pipeline.user.create_user",
    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # We might want to enable it
    # # Update the user record with any changed info from the auth service.
    # 'social_core.pipeline.user.user_details',
    # Custom
    # We do this only if the user get's created for the first time.
    "moviesapp.social.load_user_data",
)

# django-simple-menu
MENU_SELECT_PARENTS = True

# django-debug-toolbar
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    # django-debug-toolbar-template-timings
    "template_timings_panel.panels.TemplateTimings.TemplateTimings",
]

# django-modeladmin-reorder
ADMIN_REORDER = (
    {
        "app": "moviesapp",
        "models": (
            "moviesapp.User",
            "moviesapp.Movie",
            "moviesapp.Record",
            "moviesapp.List",
            "moviesapp.Action",
            "moviesapp.ActionRecord",
        ),
    },
    {"app": "social_django", "models": ("social_django.UserSocialAuth",)},
    {"app": "sites", "models": ("sites.models.Site",)},
    "registration",
)

# django-modeltranslation
MODELTRANSLATION_CUSTOM_FIELDS = ("JSONField",)

# --== Project settings ==--

GOOGLE_ANALYTICS_ID = getenv("GOOGLE_ANALYTICS_ID")

# Social
VK_BACKENDS = ("vk-app", "vk-oauth2")

# Search settings
MAX_RESULTS = 50
MIN_POPULARITY = 1.5

# Posters
NO_POSTER_SMALL_IMAGE_URL = STATIC_URL + "img/no_poster_small.png"
NO_POSTER_NORMAL_IMAGE_URL = STATIC_URL + "img/no_poster_normal.png"
# Available sizes:
# "w92",
# "w154",
# "w185",
# "w342",
# "w500",
# "w780",
# "original"
POSTER_SIZE_SMALL = "w92"
POSTER_SIZE_NORMAL = "w185"
# This one is only used for vk.
POSTER_SIZE_BIG = "w500"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/"

TMDB_BASE_URL = "https://www.themoviedb.org/movie/"
AVATAR_SIZES = {"small": 100, "big": 200}
IMDB_BASE_URL = "http://www.imdb.com/title/"
MAX_RECOMMENDATIONS = 50
RECORDS_ON_PAGE = 50
PEOPLE_ON_PAGE = 25
FEED_DAYS = 7
OMDB_BASE_URL = "http://www.omdbapi.com/"

VK_NO_AVATAR = ["https://vk.com/images/camera_100.png", "https://vk.com/images/camera_200.png"]

# API Keys
TMDB_KEY = getenv("TMDB_KEY")
OMDB_KEY = getenv("OMDB_KEY")
