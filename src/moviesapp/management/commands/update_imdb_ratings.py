from django.core.management.base import BaseCommand

from ...models import Movie
from ...utils import load_omdb_movie_data


class Command(BaseCommand):
    help = 'Updates the IMDB ratings'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        for movie in movies:
            movie_data = load_omdb_movie_data(movie.imdb_id)
            movie.imdb_rating = movie_data.get('imdbRating')
            movie.save()
