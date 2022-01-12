from .settings import *  # noqa pylint: disable=unused-wildcard-import,wildcard-import

DATABASES["default"] = {  # noqa
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

SECRET_KEY = "key"
GOOGLE_ANALYTICS = "id"
