# coding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand

from ...command_utils import tqdm
from ...models import Movie
from ...utils import load_omdb_movie_data

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    help = 'Updates the IMDB ratings'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        t = tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            t.set_description(movie_info)
            movie_data = load_omdb_movie_data(movie.imdb_id)
            new_rating = movie_data.get('imdbRating')
            if new_rating != movie.imdb_rating:
                movie.save()
                message = '{} - rating updated'.format(movie)
                t.info(message)
            t.update()
