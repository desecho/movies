# coding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand
from tqdm import tqdm as tqdm_original

from ...command_utils import tqdm
from ...models import Movie

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        t = tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            t.set_description(movie_info)
            if not movie.records.exists():
                movie.delete()
                message = '{} removed'.format(movie)
                t.error(message)
            t.update()
