from django.core.management.base import BaseCommand
from movies.models import Movie
from datetime import datetime, timedelta
from movies.functions import tmdb

class Command(BaseCommand):
    # Not used
    help = 'Gets runtime'

    def handle(self, *args, **options):
        def get_runtime(id):
            try:
                runtime = tmdb.Movie(id).runtime
            except:
                return
            if runtime:
                runtime = datetime(1990, 1, 1, 0, 0) + timedelta(minutes=runtime)
                return runtime.time()

        for movie in Movie.objects.filter(runtime=None):
            movie.runtime = get_runtime(movie.tmdb_id)
            movie.save()
