from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Movie
from ...utils import load_omdb_movie_data


class Command(BaseCommand):
    help = 'Updates the IMDB ratings'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        t = tqdm(total=movies.count())
        format = '{0: < %d}' % len(str(movies.last().pk))
        for movie in movies:
            info = format.format(movie.pk)
            t.set_description(info)
            movie_data = load_omdb_movie_data(movie.imdb_id)
            movie.imdb_rating = movie_data.get('imdbRating')
            movie.save()
            t.update()
