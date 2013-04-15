from django.core.management.base import BaseCommand
from movies.models import Movie
from django.conf import settings
import tmdb3

tmdb3.set_key(settings.TMDB_KEY)
tmdb3.set_cache(filename=settings.TMDB_CACHE_PATH)
tmdb3.set_locale(settings.LANGUAGE_CODE, settings.LANGUAGE_CODE)

class Command(BaseCommand):
    help = 'Gets russian title and overview'
    def handle(self, *args, **options):
        for movie in Movie.objects.all():
            m = tmdb3.Movie(movie.tmdb_id)
            movie.overview = m.overview
            movie.title_ru = m.title
            movie.save()
