"""Settings for tests."""

from .settings import *  # noqa pylint: disable=unused-wildcard-import,wildcard-import

DATABASES["default"] = {  # noqa
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Override REST_FRAMEWORK settings for tests to allow session authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
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

# Disable CSRF for tests to avoid 403 errors
USE_TZ = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

SECRET_KEY = "key"  # nosec B105
GOOGLE_ANALYTICS = "id"
IS_TEST = True
