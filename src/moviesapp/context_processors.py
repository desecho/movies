# -*- coding: utf-8 -*-

from django.conf import settings


def variables(request):  # pylint: disable=unused-argument
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'DEBUG': settings.DEBUG,
    }
