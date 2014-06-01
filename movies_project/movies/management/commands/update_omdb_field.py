from django.core.management.base import BaseCommand
from movies.models import Movie
from movies.functions import load_omdb_movie_data

class Command(BaseCommand):
    help = 'Updates field from omdb'

    def handle(self, *args, **options):
        field = 'Country'
        movies = Movie.objects.all()
        for movie in movies:
            movie_data = load_omdb_movie_data(movie.imdb_id)
            movie.country = movie_data.get(field)
            movie.save()
            print movie.title
