"""Django settings."""

from datetime import timedelta
from os import getenv
from os.path import abspath, dirname, join
from urllib.parse import urljoin

import django_stubs_ext
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from moviesapp.types import TemplatesSettings, TrailerSitesSettings

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
IS_CELERY_DEBUG = bool(getenv("IS_CELERY_DEBUG"))
COLLECT_STATIC = bool(getenv("COLLECT_STATIC"))
SRC_DIR = dirname(dirname(abspath(__file__)))
PROJECT = "movies"
APP = "moviesapp"
PROJECT_DIR = dirname(SRC_DIR)
PROJECT_DOMAIN = getenv("PROJECT_DOMAIN")
REDIS_URL = getenv("REDIS_URL")
LANGUAGE_EN = "en"
LANGUAGE_RU = "ru"

# Debug
DEBUG = bool(getenv("DEBUG"))
INTERNAL_IPS = [getenv("INTERNAL_IP")]

ADMIN_EMAIL = getenv("ADMIN_EMAIL")
SECRET_KEY = getenv("SECRET_KEY", "key")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": PROJECT,
        "USER": getenv("DB_USER"),
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
ROOT_URLCONF = f"{PROJECT}.urls"
WSGI_APPLICATION = f"{PROJECT}.wsgi.application"
SESSION_SAVE_EVERY_REQUEST = True

# Email
EMAIL_USE_SSL = bool(getenv("EMAIL_USE_SSL", "True"))
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(getenv("EMAIL_PORT", "465"))
DEFAULT_FROM_EMAIL = ADMIN_EMAIL

# Allowed hosts
ALLOWED_HOSTS = [PROJECT_DOMAIN]

# Internationalization
LANGUAGE_CODE = LANGUAGE_EN
LANGUAGES = (
    (LANGUAGE_EN, "English"),
    (LANGUAGE_RU, "Русский"),
)
LOCALE_PATHS = (join(SRC_DIR, "locale"),)

# Timezone
TIME_ZONE = "US/Eastern"
USE_TZ = True

TEMPLATES: list[TemplatesSettings] = [
    {
        "NAME": "Main",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [join(SRC_DIR, "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom
                "django.template.context_processors.media",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
            "builtins": ["django.templatetags.static"],
        },
    },
]
if IS_DEV:  # pragma: no cover
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        "django.template.loaders.filesystem.Loader",
        "django.template.loaders.app_directories.Loader",
    ]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom
    "django.middleware.gzip.GZipMiddleware",
    "custom_anonymous.middleware.AuthenticationMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
    "moviesapp.middleware.TimezoneMiddleware",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Custom
    "admin_reorder",
    "django_countries",
    "django_celery_results",
    "rest_framework",
    "corsheaders",
    "rest_registration",
    "storages",
    APP,
]
if DEBUG:  # pragma: no cover
    INSTALLED_APPS += []

if IS_DEV or COLLECT_STATIC:  # pragma: no cover
    INSTALLED_APPS.append("django.contrib.staticfiles")

# Security
DISABLE_CSRF = bool(getenv("DISABLE_CSRF"))
if not DISABLE_CSRF:  # pragma: no cover
    # CSRF_COOKIE_SAMESITE = "None"
    # SESSION_COOKIE_SAMESITE = "None"

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [f"https://{PROJECT_DOMAIN}"]

# Authentication
AUTH_USER_MODEL = "moviesapp.User"
AUTH_ANONYMOUS_MODEL = "moviesapp.models.UserAnonymous"
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# Login
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
LOGIN_ERROR_URL = "/login-error/"

# Static files
STATICFILES_DIR = join(SRC_DIR, APP, "static")
if IS_DEV:  # pragma: no cover
    STATICFILES_DIRS = (STATICFILES_DIR,)
    STATIC_ROOT = None
else:
    STATIC_ROOT = join(PROJECT_DIR, "static")

STATIC_URL = getenv("STATIC_URL", "/static/")

# Media files
MEDIA_ROOT = join(PROJECT_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# --== Modules settings ==--

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
}

FRONTEND_URL = getenv("FRONTEND_URL")
CORS_ALLOWED_ORIGINS = [FRONTEND_URL]
FRONTEND_URL2 = getenv("FRONTEND_URL2")
if FRONTEND_URL2:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL2)

REST_REGISTRATION = {
    "VERIFICATION_FROM_EMAIL": ADMIN_EMAIL,
    "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    "RESET_PASSWORD_VERIFICATION_URL": f"{FRONTEND_URL}/reset-password/",
    "REGISTER_VERIFICATION_URL": f"{FRONTEND_URL}/verify-user/",
    "REGISTER_SERIALIZER_PASSWORD_CONFIRM": False,
    "CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": False,
}

# django-modeladmin-reorder
ADMIN_REORDER = [
    {
        "app": APP,
        "models": (
            "moviesapp.User",
            "moviesapp.Movie",
            "moviesapp.Record",
            "moviesapp.List",
            "moviesapp.Action",
            "moviesapp.ActionRecord",
            "moviesapp.Provider",
            "moviesapp.ProviderRecord",
        ),
    },
]

if IS_CELERY_DEBUG:  # pragma: no cover
    ADMIN_REORDER.append({"app": "django_celery_results", "models": ("django_celery_results.TaskResult",)})

# django-modeltranslation
MODELTRANSLATION_CUSTOM_FIELDS = ("JSONField",)

# Celery
CELERY_CACHE_BACKEND = "default"
if IS_CELERY_DEBUG:  # pragma: no cover
    CELERY_RESULT_BACKEND = "django-db"
else:
    CELERY_RESULT_BACKEND = f"{REDIS_URL}0"
CELERY_BROKER_URL = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE

# --== Project settings ==--

REQUESTS_TIMEOUT = 5

# Search settings
MAX_RESULTS = 50
MIN_POPULARITY = 1.5

# Posters
NO_POSTER_SMALL_IMAGE_URL = "img/no_poster_small.png"
NO_POSTER_NORMAL_IMAGE_URL = "img/no_poster_normal.png"
NO_POSTER_BIG_IMAGE_URL = "img/no_poster_big.png"
POSTER_SIZE_SMALL = "w92"
POSTER_SIZE_NORMAL = "w185"
POSTER_SIZE_BIG = "w500"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/"

PROVIDERS_IMG_DIR = join(PROJECT_DIR, "frontend", "public", "img", "providers")
TMDB_BASE_URL = "https://www.themoviedb.org/"
TMDB_MOVIE_BASE_URL = urljoin(TMDB_BASE_URL, "movie/")
TMDB_PROVIDER_BASE_URL = urljoin(TMDB_BASE_URL, "t/p/original/")
TMDB_API_BASE_URL = "https://api.themoviedb.org/3/"
IMDB_BASE_URL = "http://www.imdb.com/title/"
RECORDS_ON_PAGE = 50
PEOPLE_ON_PAGE = 25
FEED_DAYS = 7
OMDB_BASE_URL = "http://www.omdbapi.com/"
TRAILER_SITES: TrailerSitesSettings = {
    "YouTube": "https://www.youtube.com/watch?v=",
    "Vimeo": "https://vimeo.com/",
}
IS_TEST = False
INCLUDE_ADULT = False

AVATAR_MAX_DIMENSION = 4096

# Watch data
PROVIDERS_SUPPORTED_COUNTRIES = ("RU", "CA", "US")
# Number of min days that need to pass before the next watch data update
WATCH_DATA_UPDATE_MIN_DAYS = 3

# API Keys
TMDB_KEY = getenv("TMDB_KEY")
OMDB_KEY = getenv("OMDB_KEY")
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

# AI Recommendations
AI_MAX_RECOMMENDATIONS = 10
AI_MIN_RECOMMENDATIONS = 1
AI_MIN_RATING = 0
AI_MAX_RATING = 5
AI_MAX_MOVIE_TITLE_LENGTH = 100

OPENAI_MODEL = "gpt-4.1"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 1000

# Movie Genres
MAIN_GENRES = [
    "Action",
    "Adventure",
    "Animation",
    "Biography",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Family",
    "Fantasy",
    "History",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Sport",
    "Thriller",
    "War",
    "Western",
]

SUBGENRES = [
    "Action-Comedy",
    "Romantic Comedy",
    "Psychological Thriller",
    "Dark Comedy",
    "Superhero",
    "Post-Apocalyptic",
    "Coming-of-Age",
    "Noir",
    "Neo-Noir",
    "Slasher",
    "Found Footage",
    "Cyberpunk",
    "Steampunk",
    "Zombie",
    "Mockumentary",
]

# Digital Ocean Spaces Configuration
DO_SPACES_ACCESS_KEY_ID = getenv("DO_SPACES_ACCESS_KEY_ID")
DO_SPACES_SECRET_ACCESS_KEY = getenv("DO_SPACES_SECRET_ACCESS_KEY")
DO_SPACES_ENDPOINT_URL = getenv("DO_SPACES_ENDPOINT_URL", "https://nyc3.digitaloceanspaces.com")
DO_SPACES_BUCKET_NAME = getenv("DO_SPACES_BUCKET_NAME")
DO_SPACES_REGION = getenv("DO_SPACES_REGION")
DO_SPACES_CUSTOM_DOMAIN = getenv("DO_SPACES_BUCKET_NAME")

# Storage configuration for avatars using modern Django 5.2+ STORAGES setting
if DO_SPACES_ACCESS_KEY_ID and DO_SPACES_SECRET_ACCESS_KEY:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": DO_SPACES_ACCESS_KEY_ID,
                "secret_key": DO_SPACES_SECRET_ACCESS_KEY,
                "bucket_name": DO_SPACES_BUCKET_NAME,
                "endpoint_url": DO_SPACES_ENDPOINT_URL,
                "region_name": DO_SPACES_REGION,
                "custom_domain": DO_SPACES_CUSTOM_DOMAIN,
                "default_acl": "public-read",
                "location": "",
                "object_parameters": {
                    "CacheControl": "max-age=86400",
                },
                "querystring_auth": False,  # Don't use query string authentication for public files
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    # Fallback to local storage when Digital Ocean Spaces is not configured
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
