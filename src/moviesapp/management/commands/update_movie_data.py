from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Movie
from ...utils import add_movie_to_db


class Command(BaseCommand):
    help = """Updates movie data
    optional arguments -
    1 - movie_id
    2 - any char
    If one argument is used then the movie with the selected movie_id is updated
    If two arguments are used then movie update starts from the selected movie_id
    If no arguments are used - all movies get updated
    """

    def handle(self, *args, **options):
        def get_movies():
            def get_args():
                if args:
                    movie_id = args[0]
                    try:
                        batch = args[1]
                    except:
                        batch = False
                else:
                    movie_id = None
                    batch = None
                return movie_id, batch

            movie_id, batch = get_args()

            movies = Movie.objects.all()
            if movie_id is not None:
                if batch:
                    movies = movies.filter(pk__gte=movie_id)
                else:
                    movies = movies.filter(pk=movie_id)
            return movies

        movies = get_movies()
        t = tqdm(total=movies.count())
        format = '{0: < %d}' % len(str(movies.last().pk))
        for movie in movies:
            id = add_movie_to_db(movie.tmdb_id, True)
            info = format.format(movie.pk)
            t.set_description(info)
            id = add_movie_to_db(movie.tmdb_id, True)
            if id < 0:
                t.write('Error {} ({})'.format(id, movie.pk))
            t.update()
