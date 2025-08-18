"""Movie detail views."""

from datetime import datetime, time
from typing import TYPE_CHECKING, Any, List, Optional, cast
from urllib.parse import urljoin

from babel.dates import format_date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.http import Http404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_exception

from ..models import Movie, ProviderRecord, Record, User
from ..omdb import get_omdb_movie_data
from ..tmdb import get_poster_url, get_tmdb_movie_data, get_tmdb_url, get_watch_data
from ..utils import is_movie_released
from .types import MovieObject, ProviderObject, ProviderRecordObject, RecordObject

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class MovieDetailView(APIView):
    """Movie detail view."""

    permission_classes: list[type["BasePermission"]] = []

    def _filter_out_provider_records_for_other_countries(self, provider_records: list[ProviderRecord]) -> None:
        """Filter out provider records for other countries."""
        for provider_record in list(provider_records):
            user: User = cast(User, self.request.user)
            if user.is_authenticated and user.country != provider_record.country:
                provider_records.remove(provider_record)

    def _get_provider_records(self, movie: Movie) -> list[ProviderRecord]:
        """Get provider records for movie."""
        user: User = cast(User, self.request.user)
        if user.is_authenticated and user.is_country_supported and movie.is_released:
            provider_records = list(movie.provider_records.all())
            self._filter_out_provider_records_for_other_countries(provider_records)
            return provider_records
        return []

    @staticmethod
    def _get_provider_record_objects(provider_records: list[ProviderRecord]) -> list[ProviderRecordObject]:
        """Get provider record objects."""
        provider_record_objects: list[ProviderRecordObject] = []
        for provider_record in provider_records:
            provider_object: ProviderObject = {
                "logo": provider_record.provider.logo,
                "name": provider_record.provider.name,
            }
            provider_record_object: ProviderRecordObject = {
                "tmdbWatchUrl": provider_record.tmdb_watch_url,
                "provider": provider_object,
            }
            provider_record_objects.append(provider_record_object)

        return provider_record_objects

    @staticmethod
    def _get_movie_object(movie: Movie) -> MovieObject:
        """Get movie object."""
        return {
            "id": movie.pk,
            "title": movie.title,
            "titleOriginal": movie.title_original,
            "isReleased": movie.is_released,
            "posterNormal": movie.poster_normal,
            "posterBig": movie.poster_big,
            "posterSmall": movie.poster_small,
            "imdbRating": movie.imdb_rating_float,
            "releaseDate": movie.release_date_formatted,
            "releaseDateTimestamp": movie.release_date_timestamp,
            "country": movie.country,
            "director": movie.director,
            "writer": movie.writer,
            "genre": movie.genre,
            "actors": movie.actors,
            "overview": movie.overview,
            "homepage": movie.homepage,
            "runtime": movie.runtime_formatted,
            "imdbUrl": movie.imdb_url,
            "tmdbUrl": movie.tmdb_url,
            "trailers": movie.get_trailers(),
            "hasPoster": movie.has_poster,
        }

    def _get_user_record(self, movie: Movie) -> Optional[RecordObject]:
        """Get user's record for this movie if exists."""
        user: User = cast(User, self.request.user)
        if not user.is_authenticated:
            return None  # type: ignore[unreachable]

        try:
            record = Record.objects.select_related("movie").get(user=user, movie=movie)
            provider_records = self._get_provider_records(record.movie)
            return {
                "id": record.pk,
                "order": record.order,
                "movie": self._get_movie_object(record.movie),
                "comment": record.comment,
                "commentArea": bool(record.comment),
                "rating": record.rating,
                "providerRecords": self._get_provider_record_objects(provider_records),
                "listId": record.list.pk,
                "additionDate": record.date.timestamp(),
                "options": {
                    "original": record.watched_original,
                    "extended": record.watched_extended,
                    "theatre": record.watched_in_theatre,
                    "hd": record.watched_in_hd,
                    "fullHd": record.watched_in_full_hd,
                    "ultraHd": record.watched_in_4k,
                    "ignoreRewatch": record.ignore_rewatch,
                },
            }
        except Record.DoesNotExist:
            return None

    def _create_movie_object_from_tmdb(self, tmdb_id: int) -> MovieObject:
        """Create movie object from TMDB data when movie is not in database."""
        try:
            # Get TMDB data
            tmdb_data = get_tmdb_movie_data(tmdb_id)

            # Get additional data from OMDb if available
            try:
                omdb_data = get_omdb_movie_data(tmdb_data["imdb_id"])
                country = omdb_data.get("country")
                director = omdb_data.get("director")
                writer = omdb_data.get("writer")
                genre = omdb_data.get("genre")
                actors = omdb_data.get("actors")
                imdb_rating = omdb_data.get("imdb_rating")
            except Exception as e:  # pylint: disable=broad-exception-caught
                # If OMDb fails, continue with just TMDB data
                capture_exception(e)
                country = None
                director = None
                writer = None
                genre = None
                actors = None
                imdb_rating = None

            # Format release date
            release_date_formatted = None
            if tmdb_data["release_date"]:
                release_date_formatted = format_date(tmdb_data["release_date"], locale=self.request.LANGUAGE_CODE)

            # Calculate release date timestamp
            release_date_timestamp = 0.0
            if tmdb_data["release_date"]:
                dt = datetime.combine(tmdb_data["release_date"], time())
                release_date_timestamp = dt.timestamp()
            else:
                next_year = datetime.now() + relativedelta(years=1)
                release_date_timestamp = next_year.timestamp()

            # Format runtime
            runtime_formatted = None
            if tmdb_data["runtime"]:
                runtime_formatted = tmdb_data["runtime"].strftime("%H:%M")

            # Get poster URLs
            poster_small = get_poster_url("small", tmdb_data["poster"])
            poster_normal = get_poster_url("normal", tmdb_data["poster"])
            poster_big = get_poster_url("big", tmdb_data["poster"])

            # Get TMDB and IMDb URLs
            tmdb_url = get_tmdb_url(tmdb_id)
            imdb_url = urljoin(settings.IMDB_BASE_URL, tmdb_data["imdb_id"])

            return {
                "id": tmdb_id,  # Use TMDB ID as identifier
                "title": tmdb_data["title"],
                "titleOriginal": tmdb_data["title_original"],
                "isReleased": is_movie_released(tmdb_data["release_date"]),
                "posterNormal": poster_normal,
                "posterBig": poster_big,
                "posterSmall": poster_small,
                "imdbRating": float(imdb_rating) if imdb_rating else None,
                "releaseDate": release_date_formatted,
                "releaseDateTimestamp": release_date_timestamp,
                "country": country,
                "director": director,
                "writer": writer,
                "genre": genre,
                "actors": actors,
                "overview": tmdb_data["overview"],
                "homepage": tmdb_data["homepage"],
                "runtime": runtime_formatted,
                "imdbUrl": imdb_url,
                "tmdbUrl": tmdb_url,
                "trailers": self._convert_tmdb_trailers_to_trailers(tmdb_data["trailers"]),
                "hasPoster": tmdb_data["poster"] is not None,
            }
        except Exception as e:
            capture_exception(e)
            raise Http404("Movie not found on TMDB") from e

    @staticmethod
    def _convert_tmdb_trailers_to_trailers(tmdb_trailers: List[Any]) -> List[Any]:
        """Convert TMDB trailers to standard trailer format."""
        trailers = []
        for tmdb_trailer in tmdb_trailers:
            site = tmdb_trailer["site"]
            key = tmdb_trailer["key"]
            name = tmdb_trailer["name"]

            # Get base URL for the trailer site
            trailer_sites = dict(settings.TRAILER_SITES)
            if site in trailer_sites:
                base_url = trailer_sites[site]
                trailer_url = f"{base_url}{key}"

                trailer = {
                    "url": trailer_url,
                    "name": name,
                }
                trailers.append(trailer)

        return trailers

    @staticmethod
    def _get_tmdb_provider_records(tmdb_id: int) -> list[ProviderRecord]:
        """Get provider records from TMDB for a movie not in database."""
        try:
            # Note: This returns empty list since we don't have Provider objects in DB
            # for movies not in our database. We could enhance this later.
            _ = get_watch_data(tmdb_id)  # Keep the call but mark as intentionally unused
            return []
        except Exception as e:  # pylint: disable=broad-exception-caught
            capture_exception(e)
            return []

    def get(self, request: Request, tmdb_id: int) -> Response:  # pylint: disable=unused-argument
        """Get movie details by TMDB ID."""
        try:
            # Try to get movie from database first
            movie = Movie.objects.prefetch_related("provider_records__provider").get(tmdb_id=tmdb_id)

            # Movie exists in database - use existing logic
            provider_records = self._get_provider_records(movie)
            movie_object = self._get_movie_object(movie)
            user_record = self._get_user_record(movie)

            response_data = {
                "movie": movie_object,
                "providerRecords": self._get_provider_record_objects(provider_records),
                "userRecord": user_record,
            }

        except Movie.DoesNotExist:
            # Movie not in database - fetch from TMDB
            movie_object = self._create_movie_object_from_tmdb(tmdb_id)
            provider_records = self._get_tmdb_provider_records(tmdb_id)

            response_data = {
                "movie": movie_object,
                "providerRecords": self._get_provider_record_objects(provider_records),
                "userRecord": None,  # No user record for movies not in DB
            }

        return Response(response_data)
