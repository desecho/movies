from django.core.management.base import BaseCommand
from movies.models import Movie
from datetime import datetime, timedelta
from django.conf import settings
import tmdb3

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)
tmdb3.set_locale(settings.LANGUAGE_CODE, settings.LANGUAGE_CODE)

class Command(BaseCommand):
    help = 'Gets runtime'

    def handle(self, *args, **options):
        def get_runtime(id):
            try:
                runtime = tmdb3.Movie(id).runtime
            except:
                return
            if runtime:
                runtime = datetime(1990, 1, 1, 0, 0) + timedelta(minutes=runtime)
                return runtime.time()

        for movie in Movie.objects.filter(runtime=None):
            movie.runtime = get_runtime(movie.tmdb_id)
            movie.save()
