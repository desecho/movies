from django.conf import settings


def variables(request):
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS_ID,
        'DEBUG': settings.DEBUG,
    }
