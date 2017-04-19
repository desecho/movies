# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings


def variables(request):
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'DEBUG': settings.DEBUG,
    }
