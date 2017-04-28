from .settings import *  # noqa pylint: disable=unused-wildcard-import,wildcard-import

DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }  # noqa
