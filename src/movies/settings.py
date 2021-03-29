"""Django settings."""

from os import getenv
from os.path import abspath, dirname, join

SRC_DIR = dirname(dirname(abspath(__file__)))
PROJECT_DIR = dirname(SRC_DIR)

# Custom
IS_DEV = bool(getenv("IS_DEV"))
IS_VK_DEV = bool(getenv("IS_VK_DEV"))

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
EMAIL_USE_SSL = bool(getenv("EMAIL_USE_SSL"))
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(getenv("EMAIL_PORT"))
DEFAULT_FROM_EMAIL = ADMIN_EMAIL

# Allowed hosts
ALLOWED_HOSTS = [getenv("PROJECT_DOMAIN")]
if IS_VK_DEV:
    ALLOWED_HOSTS.append(getenv("HOST_MOVIES_TEST"))

# Internationalization
LANGUAGE_CODE = "en"
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ("en", "English"),
    ("ru", "Русский"),
)
LOCALE_PATHS = (join(SRC_DIR, "locale"),)

# Timezone
TIME_ZONE = "US/Eastern"
USE_TZ = True

TEMPLATES = [
    {
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
                "django.template.context_processors.static",
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
        },
    },
]
if DEBUG:
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # We disable this to make VK iframe app work
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "custom_anonymous.middleware.AuthenticationMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
    "moviesapp.middleware.PutHandlerMiddleware",
]
if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Custom
    "django.contrib.sites",
    "google_analytics",
    "registration",
    "menu",
    "admin_reorder",
    "bootstrap_pagination",
    "rosetta",
    "modeltranslation",
    "social_django",
    "raven.contrib.django.raven_compat",
    "moviesapp",
]
if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
        "template_timings_panel",
    ]

# Logging
if not DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "root": {
            "level": "WARNING",
            "handlers": ["sentry"],
        },
        "formatters": {
            "verbose": {"format": ("%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s")},
        },
        "handlers": {
            "sentry": {
                "level": "ERROR",  # To capture more than ERROR, change to WARNING, INFO, etc.
                "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
                "tags": {"custom-tag": "x"},
            },
            "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "verbose"},
        },
        "loggers": {
            "django.db.backends": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
            "raven": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
            "sentry.errors": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

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
if IS_VK_DEV:
    LOGIN_REDIRECT_URL = "https://{}".format(getenv("HOST_MOVIES_TEST"))
LOGIN_URL = "/login/"
LOGIN_ERROR_URL = "/login-error/"

# Static files
if IS_DEV:
    STATICFILES_DIRS = (join(SRC_DIR, "moviesapp", "static"), join(PROJECT_DIR, "static"))
    STATIC_ROOT = None
else:
    STATIC_ROOT = join(PROJECT_DIR, "static")

STATIC_URL = "/static/"

# Media files
MEDIA_ROOT = join(PROJECT_DIR, "media")
MEDIA_URL = "/media/"

# --== Modules settings ==--

# django-registration-redux
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_FORM = "registration.forms.RegistrationFormUniqueEmail"

# social-auth-app-django
SOCIAL_AUTH_VK_OAUTH2_KEY = getenv("SOCIAL_AUTH_VK_OAUTH2_KEY")
SOCIAL_AUTH_VK_OAUTH2_SECRET = getenv("SOCIAL_AUTH_VK_OAUTH2_SECRET")
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ["friends", "email"]

SOCIAL_AUTH_VK_APP_KEY = getenv("SOCIAL_AUTH_VK_APP_KEY")
SOCIAL_AUTH_VK_APP_SECRET = getenv("SOCIAL_AUTH_VK_APP_SECRET")
SOCIAL_AUTH_VK_APP_USER_MODE = 2

SOCIAL_AUTH_FACEBOOK_KEY = getenv("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = getenv("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email", "user_friends", "public_profile", "user_location"]

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

# raven
RAVEN_CONFIG = {"dsn": getenv("RAVEN_DSN")}

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

# django-google-analytics-app
GOOGLE_ANALYTICS = {"google_analytics_id": getenv("GOOGLE_ANALYTICS_ID")}

# --== Project settings ==--

# Social
VK_BACKENDS_CREDENTIALS = {
    "vk-app": (SOCIAL_AUTH_VK_APP_KEY, SOCIAL_AUTH_VK_APP_SECRET),
    "vk-oauth2": (SOCIAL_AUTH_VK_OAUTH2_KEY, SOCIAL_AUTH_VK_OAUTH2_SECRET),
}
VK_BACKENDS = VK_BACKENDS_CREDENTIALS.keys()

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
POSTER_BASE_URL = "http://image.tmdb.org/t/p/"

TMDB_MOVIE_BASE_URL = "https://www.themoviedb.org/movie/"
AVATAR_SIZES = {"small": 100, "big": 200}
IMDB_BASE_URL = "http://www.imdb.com/title/"
MAX_RECOMMENDATIONS = 50
RECORDS_ON_PAGE = 50
PEOPLE_ON_PAGE = 25
FEED_DAYS = 7

VK_EN = 3
VK_NO_AVATAR = ["https://vk.com/images/camera_100.png", "https://vk.com/images/camera_200.png"]

# API Keys
TMDB_KEY = getenv("TMDB_KEY")
OMDB_KEY = getenv("OMDB_KEY")
