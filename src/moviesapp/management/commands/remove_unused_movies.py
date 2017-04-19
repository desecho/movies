# coding: utf-8
from __future__ import unicode_literals

import sys

from django.core.management.base import BaseCommand
from tqdm import tqdm as tqdm_original

from ...command_utils import tqdm
# from tqdm import tqdm
from ...models import Movie

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):
        def format_movie(movie, last_movie_id):
            MAX_CHARS = 40
            ENDING = '..'
            id_format = '{0: < %d}' % (len(str(last_movie_id)) + 1)
            title = unicode(movie)
            title = (title[:MAX_CHARS] + ENDING) if len(title) > MAX_CHARS else title
            id = id_format.format(movie.pk)
            title_max_length = MAX_CHARS + len(ENDING)
            title_format = '{:%ds}' % title_max_length
            title = title_format.format(title)
            return '{} - {}'.format(id, title)[1:].decode('utf8')

        movies = Movie.objects.all()
        t = tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            info = format_movie(movie, last_movie_id)
            t.set_description(info)
            if not movie.records.exists():
                movie.delete()
                message = '{} removed'.format(movie)
                t.error(message)
            if movie.pk == 178:
                t.error(movie)
            if movie.pk == 1023:
                t.info(movie)
            t.update()
