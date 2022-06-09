from typing import Any, Dict, List, Union

from django.conf import settings
from django.core.management.base import CommandParser
from django.db.models.query import QuerySet
from django_tqdm import BaseCommand
from sentry_sdk import capture_exception

from moviesapp.exceptions import ProviderNotFoundError
from moviesapp.models import Movie, ProviderRecord
from moviesapp.tmdb import TmdbNoImdbIdError
from moviesapp.utils import load_movie_data, save_watch_data


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

    @staticmethod
    def _remove_no_longer_available_provider_records(
        existing_provider_records: List[Dict[str, Union[str, int]]], watch_data: List[Dict[str, Union[str, int]]]
    ) -> None:
        for provider_record in existing_provider_records:
            provider_record_id = provider_record.pop("id")
            # Remove the record if it's no longer available.
            if provider_record not in watch_data:
                ProviderRecord.objects.get(pk=provider_record_id).delete()

    @staticmethod
    def _filter_out_already_existing_provider_records(
        existing_provider_records: List[Dict[str, Union[str, int]]], watch_data: List[Dict[str, Union[str, int]]]
    ) -> None:
        """Remove the provider record from the watch_data if it's already in the existing_provider_records."""
        for provider_record in existing_provider_records:
            if provider_record in watch_data:
                # Don't create a record if it already exists.
                watch_data.remove(provider_record)

    def _update_movie_data(self, movie: Movie) -> bool:
        """Return if the movie was updated or not."""
        movie_data = load_movie_data(movie.tmdb_id)
        # Use filter here to be able to use "update" functionality.
        movies = Movie.objects.filter(pk=movie.pk)
        movie_initial_data = movies.values()[0]
        watch_data = movie_data.pop("watch_data")
        movies.update(**movie_data)
        existing_provider_records = movie.provider_records.all().values("id", "provider_id", "country")
        self._remove_no_longer_available_provider_records(list(existing_provider_records), watch_data)  # type: ignore
        self._filter_out_already_existing_provider_records(
            list(existing_provider_records.values("provider_id", "country")), watch_data  # type: ignore
        )
        try:
            save_watch_data(movies[0], watch_data)
        except ProviderNotFoundError as e:
            if settings.DEBUG:
                raise
            capture_exception(e)
        movie_updated_data = Movie.objects.filter(pk=movie.pk).values()[0]
        updated: bool = movie_initial_data != movie_updated_data
        return updated

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
        last_movie = movies.last()  # pylint: disable=duplicate-code
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                try:
                    result = self._update_movie_data(movie)
                except TmdbNoImdbIdError:
                    tqdm.error(f'"{movie.id_title}" is not found in IMDb')
                else:
                    updated = result
                    if updated:
                        tqdm.info(f'"{movie}" is updated')
                tqdm.update()
