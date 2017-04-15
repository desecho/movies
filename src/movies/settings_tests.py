from .settings import *  # noqa


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return 'notmigrations'

DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:', }  # noqa
MIGRATION_MODULES = DisableMigrations()
