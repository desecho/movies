"""Update watch data."""
from typing import Any, Dict, List, Optional, Union

from django.conf import settings
from django.core.management.base import CommandParser
from django_tqdm import BaseCommand
from sentry_sdk import capture_exception

from moviesapp.exceptions import ProviderNotFoundError
from moviesapp.models import Movie, ProviderRecord
from moviesapp.tmdb import get_watch_data


class Command(BaseCommand):
    """Update watch data."""

    help = """Update watch data.

    If an argument is provided then the movie with the selected movie_id is updated.
    It is updated even if the movie does not need to be updated (was recently updated).
    If no arguments are provided - all movies get updated.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument("movie_id", nargs="?", default=None, type=int)

    @staticmethod
    def _remove_no_longer_available_provider_records(
        existing_provider_records: List[Dict[str, Union[str, int]]], watch_data: List[Dict[str, Union[str, int]]]
    ) -> bool:
        removed = False
        for provider_record in existing_provider_records:
            provider_record_id = provider_record.pop("id")
            # Remove the record if it's no longer available.
            if provider_record not in watch_data:
                ProviderRecord.objects.get(pk=provider_record_id).delete()
                removed = True
        return removed

    @staticmethod
    def _filter_out_already_existing_provider_records(
        existing_provider_records: List[Dict[str, Union[str, int]]], watch_data: List[Dict[str, Union[str, int]]]
    ) -> None:
        """Remove the provider record from watch_data if it's already in existing_provider_records."""
        for provider_record in existing_provider_records:
            if provider_record in watch_data:
                # Don't create a record if it already exists.
                watch_data.remove(provider_record)

    @staticmethod
    def filter_out_movies_not_requiring_update(movies: List[Movie]) -> None:
        for movie in list(movies):
            if movie.is_watch_data_updated_recently:
                movies.remove(movie)

    def handle(self, movie_id: Optional[int], *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        """Execute command."""
        if movie_id is not None:
            try:
                Movie.objects.get(pk=movie_id)
            except Movie.DoesNotExist:
                self.error(f"There is no movie with ID {movie_id}", fatal=True)
        movies = list(Movie.filter(movie_id, release_date__isnull=False))
        # If movie_id is provided, we force update the movie
        # (we ignore if the movie needs an update or not).
        if movie_id is None:
            self.filter_out_movies_not_requiring_update(movies)
        movies_total = len(movies)
        # We don't want a progress bar if we just have one movie to process
        disable = movies_total == 1
        if not movies:
            self.info("No movies to update")
            return

        tqdm = self.tqdm(total=movies_total, unit=settings.PROJECT, disable=disable)
        last_movie = Movie.last()
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                watch_data = get_watch_data(movie.tmdb_id)
                if not watch_data:
                    self.error(f"No watch data obtained for {movie}. Skipping.")
                    continue
                existing_provider_records = movie.provider_records.all().values("id", "provider_id", "country")
                removed = self._remove_no_longer_available_provider_records(
                    list(existing_provider_records), watch_data  # type: ignore
                )
                self._filter_out_already_existing_provider_records(
                    list(existing_provider_records.values("provider_id", "country")), watch_data  # type: ignore
                )
                try:  # pylint: disable=duplicate-code
                    movie.save_watch_data(watch_data)
                except ProviderNotFoundError as e:
                    if settings.DEBUG:
                        raise
                    capture_exception(e)
                if watch_data or removed:
                    message = f"{movie} - watch data updated"
                    tqdm.info(message)
                tqdm.update()
