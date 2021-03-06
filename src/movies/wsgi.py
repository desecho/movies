"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies.settings')

application = Sentry(get_wsgi_application())
