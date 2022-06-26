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

SECRET_KEY = "key"  # nosec B105
GOOGLE_ANALYTICS = "id"
IS_TEST = True
