"""Update watch data."""

import sys
from typing import Any, Optional

from django.conf import settings
from django.core.management.base import CommandParser
from django.db.models import QuerySet
from django_tqdm import BaseCommand
from sentry_sdk import capture_exception

from moviesapp.exceptions import ProviderNotFoundError
from moviesapp.models import List, Movie, ProviderRecord, Record
from moviesapp.tmdb import get_watch_data
from moviesapp.types import ProviderRecordType, WatchDataRecord


class Command(BaseCommand):
    """Update watch data."""

    help = """Update watch data.

    If one argument is provided then the movie with the selected movie_id is updated.
    It is updated even if the movie does not need to be updated (was recently updated).

    If no arguments are provided - all movies get updated.
    """

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument("movie_id", nargs="?", default=None, type=int)
        parser.add_argument(
            "-m",
            action="store_true",
            dest="minimal",
            default=False,
            help=(
                'Update only minimal watch data. It updates only watch data for movies that are in "To Watch" '
                "list, is released, and only if a movie is in a list of a user who's country is supported"
            ),
        )

    @staticmethod
    def _filter_out_movies_not_requiring_update(movies: list[Movie]) -> None:
        """
        Filter out movies that don't need an update.

        Remove movies that don't need an update from `movies`.
        """
        for movie in list(movies):
            if movie.is_watch_data_updated_recently:
                movies.remove(movie)

    @staticmethod
    def _remove_no_longer_available_provider_records(
        existing_provider_records: list[ProviderRecordType],
        watch_data: list[WatchDataRecord],
    ) -> bool:
        """Remove provider records that are no longer available."""
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
        existing_provider_records: list[ProviderRecordType],
        watch_data: list[WatchDataRecord],
    ) -> None:
        """
        Filter out already existing provider records.

        Remove already existing provider records from `watch_data`.
        """
        for provider_record in existing_provider_records:
            if provider_record in watch_data:
                # Don't create a record if it already exists.
                watch_data.remove(provider_record)

    def handle(self, *args: Any, **options: Any) -> None:  # pylint: disable=unused-argument
        """Execute command."""
        movie_id: Optional[int] = options["movie_id"]
        minimal: bool = options["minimal"]
        if minimal and not movie_id:
            records: QuerySet[Record] = Record.objects.filter(
                list_id=List.TO_WATCH, movie__release_date__isnull=False, user__country__isnull=False
            )
            movies = list(
                set(
                    record.movie for record in records if record.movie.is_released and record.user.is_country_supported
                )
            )
        else:
            if movie_id is not None:
                try:
                    Movie.objects.get(pk=movie_id)
                except Movie.DoesNotExist:
                    self.error(f"There is no movie with ID {movie_id}", fatal=True)
            movies = list(Movie.filter(movie_id, release_date__isnull=False))
            # If movie_id is provided, we force update the movie
            # (we ignore if the movie needs an update or not).
            if movie_id is None:
                self._filter_out_movies_not_requiring_update(movies)

        movies_total = len(movies)
        # We don't want a progress bar if we just have one movie to process
        disable = movies_total == 1
        if not movies:
            self.info("No movies to update")
            sys.exit()

        tqdm = self.tqdm(total=movies_total, unit="movie", disable=disable)
        last_movie = Movie.last()
        if last_movie:
            for movie in movies:
                movie_info = movie.cli_string(last_movie.pk)
                tqdm.set_description(movie_info)
                watch_data = get_watch_data(movie.tmdb_id)
                if not watch_data:
                    tqdm.error(f"No watch data obtained for {movie}. Skipping.")
                    tqdm.update()
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
