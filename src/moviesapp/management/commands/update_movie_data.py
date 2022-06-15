"""Update movie data."""
from typing import Any, Optional

from django.core.management.base import CommandParser
from django_tqdm import BaseCommand

from moviesapp.models import Movie
from moviesapp.tmdb import TmdbNoImdbIdError
from moviesapp.utils import load_movie_data


class Command(BaseCommand):
    """Update movie data."""

    help = """Update all movie data except for IMDb ratings and watch data.

    If one argument is used then the movie with the selected movie_id is updated.
    If no arguments are used - all movies get updated.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument("movie_id", nargs="?", default=None, type=int)
        parser.add_argument(
            "-s",
            action="store_true",
            dest="start_from_id",
            default=False,
            help="Start running the script fom provided movie id",
        )

    @staticmethod
    def _update_movie_data(movie: Movie) -> bool:
        """Return if the movie was updated or not."""
        movie_data = load_movie_data(movie.tmdb_id)
        # We create a new dict here to avoid modifying the original dict which would result in an error
        movie_data_to_update = dict(movie_data)
        # Use filter here to be able to use "update" functionality.
        # We will always have only one movie.
        movies = Movie.objects.filter(pk=movie.pk)
        movie_initial_data = movies.values()[0]
        movie_data_to_update.pop("imdb_rating")
        movies.update(**movie_data_to_update)
        movie_updated_data = Movie.objects.filter(pk=movie.pk).values()[0]
        updated: bool = movie_initial_data != movie_updated_data
        return updated

    def handle(
        self,
        movie_id: Optional[int],
        start_from_id: bool,
        *args: Any,
        **options: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Execute command."""
        movies = Movie.filter(movie_id, start_from_id)
        movies_total = movies.count()
        # We don't want a progress bar if we just have one movie to process
        disable = movies_total == 1
        if not movies:  # In case movie_id is too high and we don't get any movies
            if start_from_id:
                self.error(f"There are no movies with IDs > {movie_id}", fatal=True)
            else:
                # Assume we have at least one movie in the DB
                self.error(f"There is no movie with ID {movie_id}", fatal=True)

        tqdm = self.tqdm(total=movies_total, unit="movies", disable=disable)
        last_movie = movies.last()  # pylint: disable=duplicate-code
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                try:
                    result = self._update_movie_data(movie)
                except TmdbNoImdbIdError:
                    tqdm.error(f'"{movie.title_with_id}" is not found in IMDb')
                else:
                    updated = result
                    if updated:
                        tqdm.info(f'"{movie}" is updated')
                tqdm.update()
