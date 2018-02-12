# -*- coding: utf-8 -*-

from importlib import reload

from django_tqdm import BaseCommand

from ...models import Movie
from ...utils import load_omdb_movie_data


class Command(BaseCommand):
    help = 'Updates the IMDB ratings'

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        movies = Movie.objects.all()
        t = self.tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            t.set_description(movie_info)
            movie_data = load_omdb_movie_data(movie.imdb_id)
            new_rating = movie_data.get('imdbRating')
            if new_rating != str(movie.imdb_rating):
                movie.save()
                message = f'{movie} - rating updated. {movie.imdb_rating} -> {new_rating}'
                t.info(message)
            t.update()
