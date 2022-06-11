"""Tasks."""
from celery import shared_task
from django.conf import settings
from sentry_sdk import capture_exception

from .exceptions import ProviderNotFoundError
from .models import Movie
from .tmdb import get_watch_data


@shared_task
def load_and_save_watch_data_task(movie_id: int) -> None:
    """Load and save watch data task."""
    movie = Movie.objects.get(pk=movie_id)
    watch_data = get_watch_data(movie.tmdb_id)
    try:
        movie.save_watch_data(watch_data)
    except ProviderNotFoundError as e:
        if settings.DEBUG:
            raise
        capture_exception(e)
