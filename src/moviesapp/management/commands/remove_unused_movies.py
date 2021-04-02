# -*- coding: utf-8 -*-

from django_tqdm import BaseCommand

from moviesapp.models import Movie


class Command(BaseCommand):
    help = "Removes unused movies"

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        movies = Movie.objects.all()
        tqdm = self.tqdm(total=movies.count())
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            tqdm.set_description(movie_info)
            if not movie.records.exists():
                movie.delete()
                message = f"{movie} removed"
                tqdm.info(message)
            tqdm.update()
