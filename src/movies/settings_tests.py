from .settings import *  # noqa pylint: disable=unused-wildcard-import,wildcard-import

DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }  # noqa


def get_so_env(name):
    value = os.environ.get(name)  # noqa
    if os.environ.get(name):  # noqa
        return value


tmdb_key = os.environ.get('TMDB_KEY')  # noqa
if tmdb_key:
    TMDB_KEY = tmdb_key
