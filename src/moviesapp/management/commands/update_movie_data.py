from typing import Any

from django.core.management import CommandParser
from django.db.models.query import QuerySet
from django_tqdm import BaseCommand

from moviesapp.exceptions import MovieNotInDb
from moviesapp.models import Movie
from moviesapp.utils import add_movie_to_db


class Command(BaseCommand):
    help = """Updates movie data
    If one argument is used then the movie with the selected movie_id is updated
    If no arguments are used - all movies get updated
    We are not specifying if the movie info got actually changed here.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("movie_id", nargs="?", default=None, type=int)
        parser.add_argument(
            "-s",
            action="store_true",
            dest="start_from_id",
            default=False,
            help="Start running the script fom provided movie id",
        )

    def handle(
        self, movie_id: int, start_from_id: bool, *args: Any, **options: Any  # pylint: disable=unused-argument
    ) -> None:
        def get_filtered_movies() -> QuerySet[Movie]:
            if start_from_id:
                return movies.filter(pk__gte=movie_id)
            return movies.filter(pk=movie_id)

        movies = Movie.objects.all()
        movies_total = movies.count()
        disable = None
        filtered = movie_id is not None
        if filtered:
            movies = get_filtered_movies()
            if not movies:  # In case the movie_id is too high and we don't get any movies
                if start_from_id:
                    self.error(f"There are no movies found with id > {movie_id}", fatal=True)
                else:
                    self.error(f"There is no movie with id {movie_id}", fatal=True)
            movies_filtered_number = movies.count()
            # We don't want a progress bar if we just have one movie to process
            if movies_filtered_number == 1:
                disable = True

        tqdm = self.tqdm(total=movies_total, unit="movies", disable=disable)
        if filtered:
            tqdm.update(movies_total - movies_filtered_number)
        last_movie_id = movies.last().pk
        for movie in movies:
            movie_info = movie.cli_string(last_movie_id)
            tqdm.set_description(movie_info)
            try:
                result = add_movie_to_db(movie.tmdb_id, update=True)
            except MovieNotInDb:
                tqdm.error(f'"{movie.id_title}" is not found in IMDB')
            else:
                updated = result
                if updated:
                    tqdm.info(f'"{movie}" is updated')
            tqdm.update()
