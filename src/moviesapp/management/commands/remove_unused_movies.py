# -*- coding: utf-8 -*-

from importlib import reload

from django_tqdm import BaseCommand

from moviesapp.models import Movie


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        movies = Movie.objects.all()
        t = self.tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            t.set_description(movie_info)
            if not movie.records.exists():
                movie.delete()
                message = f'{movie} removed'
                t.info(message)
            t.update()
