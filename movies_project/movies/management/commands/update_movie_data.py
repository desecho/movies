from movies.functions import add_movie_to_db
from movies.models import Movie
from django.core.management.base import BaseCommand
import sys
from tmdb3.tmdb_exceptions import TMDBRequestInvalid


class Command(BaseCommand):
    help = '''Updates movie data
    optional arguments -
    1 - movie_id
    2 - any char
    If one argument is used then the movie with the selected movie_id is updated
    If two arguments are used then movie update starts from the selected movie_id
    If no arguments are used - all movies get updated
    '''

    def handle(self, *args, **options):
        def get_tmdb_ids():
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
            return movies.values_list('tmdb_id', flat=True)

        for tmdb_id in get_tmdb_ids():
            try:
                print add_movie_to_db(tmdb_id, True)
            except TMDBRequestInvalid:
                print 'Movie id - %d' % Movie.objects.get(tmdb_id=tmdb_id).id
                print sys.exc_info()[1]
