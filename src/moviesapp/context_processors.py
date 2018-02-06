# -*- coding: utf-8 -*-

from django.conf import settings


def variables(request):  # pylint: disable=unused-argument
    return {
        'DEBUG': settings.DEBUG,
        'ADMIN_EMAIL': settings.ADMIN_EMAIL,
    }
