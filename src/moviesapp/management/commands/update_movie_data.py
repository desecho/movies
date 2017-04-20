# coding: utf-8
from __future__ import unicode_literals

import sys

from django_tqdm import BaseCommand

from ...models import Movie
from ...utils import add_movie_to_db

reload(sys)
sys.setdefaultencoding('utf8')


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

    def handle(self, movie_id, start_from_id, *args, **options):
        def get_filtered_movies():
            if start_from_id:
                return movies.filter(pk__gte=movie_id)
            else:
                return movies.filter(pk=movie_id)

        movies = Movie.objects.all()
        movies_total = movies.count()
        disable = None
        filtered = movie_id is not None
        if filtered:
            movies = get_filtered_movies()
            if not movies:  # In case the movie_id is too high and we don't get any movies
                if start_from_id:
                    self.error('There are no movies found with id > %d' % movie_id, fatal=True)
                else:
                    self.error('There is no movie with id %d' % movie_id, fatal=True)
            movies_filtered_number = movies.count()
            # We don't want a progress bar if we just have one movie to process
            if movies_filtered_number == 1:
                disable = True

        t = self.tqdm(total=movies_total, unit='movies', disable=disable)
        if filtered:
            t.update(movies_total - movies_filtered_number)
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
