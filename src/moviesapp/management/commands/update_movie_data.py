# coding: utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ...command_utils import tqdm
from ...models import Movie
from ...utils import add_movie_to_db


class Command(BaseCommand):
    help = """Updates movie data
    If one argument is used then the movie with the selected movie_id is updated
    If no arguments are used - all movies get updated
    We are not specifying if the movie info got actually changed here.
    """

    def add_arguments(self, parser):
        parser.add_argument('movie_id', nargs='?', default=None, type=int)
        parser.add_argument(
            '-s',
            action='store_true',
            dest='start_from_id',
            default=False,
            help='Start running the script fom provided movie id',
        )

    def handle(self, *args, **options):
        def get_movies():
            movie_id = options['movie_id']
            movies = Movie.objects.all()
            if movie_id is None:
                return movies

            if options['start_from_id']:
                movies = movies.filter(pk__gte=movie_id)
            else:
                movies = movies.filter(pk=movie_id)

        movies = get_movies()
        t = tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            t.set_description(movie_info)
            result = add_movie_to_db(movie.tmdb_id, update=True)
            if type(result) == bool:
                updated = result
                if updated:
                    t.info('{} updated'.format(movie))
            else:  # int
                error_id = result
                t.error('Error #{} - {}'.format(error_id, movie.id_title))
            t.update()
