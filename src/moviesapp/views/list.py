"""List views."""

from http import HTTPStatus
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet, prefetch_related_objects
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Action, ActionRecord, List, Movie, ProviderRecord, Record, User, UserAnonymous
from .types import MovieObject, OptionsObject, ProviderObject, ProviderRecordObject, RecordObject
from .utils import add_movie_to_list, get_anothers_account

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


class ChangeRatingView(APIView):
    """Change rating view."""

    def put(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Change rating."""
        try:
            rating = int(request.data["rating"])
        except (KeyError, ValueError):
            return Response(status=HTTPStatus.BAD_REQUEST)

        if rating < 0 or rating > 5:
            return Response(status=HTTPStatus.BAD_REQUEST)

        record = get_object_or_404(Record, user=request.user, pk=record_id)

        user: User = cast(User, request.user)
        if record.rating != rating:
            if not record.rating:
                ActionRecord(action_id=Action.ADDED_RATING, user=user, movie=record.movie, rating=rating).save()
            record.rating = rating
            record.save()
        return Response()


class AddToListView(APIView):
    """Add to list view."""

    def post(self, request: Request, movie_id: int) -> Response:  # pylint: disable=no-self-use
        """Add movie to list."""
        try:  # pylint: disable=duplicate-code
            list_id = int(request.data["listId"])  # pylint: disable=duplicate-code
        except (KeyError, ValueError):  # pylint: disable=duplicate-code
            return Response(status=HTTPStatus.BAD_REQUEST)  # pylint: disable=duplicate-code

        if not List.is_valid_id(list_id):  # pylint: disable=duplicate-code
            raise Http404  # pylint: disable=duplicate-code

        get_object_or_404(Movie, pk=movie_id)
        user: User = cast(User, request.user)
        add_movie_to_list(movie_id, list_id, user)
        return Response()


class RemoveRecordView(APIView):
    """Remove record view."""

    def delete(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Remove record."""
        record = get_object_or_404(Record, user=request.user, pk=record_id)
        record.delete()
        return Response()


class SaveOptionsView(APIView):
    """Save options view."""

    def put(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Save options."""
        get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            options_object: OptionsObject = request.data["options"]
            options = {
                "watched_original": options_object["original"],
                "watched_extended": options_object["extended"],
                "watched_in_theatre": options_object["theatre"],
                "watched_in_4k": options_object["ultraHd"],
                "watched_in_hd": options_object["hd"],
                "watched_in_full_hd": options_object["fullHd"],
                "ignore_rewatch": options_object["ignoreRewatch"],
            }
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)

        Record.objects.filter(pk=record_id).update(**options)
        return Response()


class SaveCommentView(APIView):
    """Save comment view."""

    def put(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Save comment."""
        record = get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            comment = request.data["comment"]
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)

        user: User = cast(User, request.user)
        if record.comment != comment:
            if not record.comment:
                ActionRecord(action_id=Action.ADDED_COMMENT, user=user, movie=record.movie, comment=comment).save()
            record.comment = comment
            record.save()
        return Response()


class RecordsView(APIView):
    """Records view."""

    anothers_account: Optional[User] = None
    permission_classes: list[type["BasePermission"]] = []

    @staticmethod
    def _sort_records(records: QuerySet[Record]) -> QuerySet[Record]:
        """Sort records."""
        return records.order_by("-date")

    @staticmethod
    def _get_record_movie_data(
        record_ids_and_movie_ids_list: list[tuple[int, int]],
    ) -> tuple[list[int], dict[int, int]]:
        """
        Get record's movie data.

        Returns a tuple of movie ids and a dictionary of record ids and movies ids.
        """
        movie_ids = [x[1] for x in record_ids_and_movie_ids_list]
        record_ids_and_movie_ids = {x[0]: x[1] for x in record_ids_and_movie_ids_list}
        return (movie_ids, record_ids_and_movie_ids)

    def _get_list_data(self, records: QuerySet[Record]) -> dict[int, int]:
        """
        Get list data.

        Returns a dictionary with record ids as keys and list ids as values.
        """
        movie_ids, record_and_movie_ids = self._get_record_movie_data(list(records.values_list("id", "movie_id")))
        user: Union[User, UserAnonymous] = cast(Union[User, UserAnonymous], self.request.user)
        movie_ids_and_list_ids_list: list[tuple[int, int]] = list(
            user.get_records().filter(movie_id__in=movie_ids).values_list("movie_id", "list_id")
        )
        movie_and_list_ids: dict[int, int] = {}
        for movie_id, list_id in movie_ids_and_list_ids_list:
            movie_and_list_ids[movie_id] = list_id

        list_data: dict[int, int] = {}
        for record_id, movie_id in record_and_movie_ids.items():
            # 0 means no list id.
            list_data[record_id] = movie_and_list_ids.get(movie_id, 0)
        return list_data

    def _filter_out_provider_records_for_other_countries(self, provider_records: list[ProviderRecord]) -> None:
        for provider_record in list(provider_records):
            user: User = cast(User, self.request.user)
            if user.country != provider_record.country:
                provider_records.remove(provider_record)

    def _get_provider_records(self, movie: Movie) -> list[ProviderRecord]:
        user: User = cast(User, self.request.user)
        if user.is_authenticated and user.is_country_supported and movie.is_released:
            provider_records = list(movie.provider_records.all())
            self._filter_out_provider_records_for_other_countries(provider_records)
            return provider_records
        return []

    @staticmethod
    def _get_provider_record_objects(provider_records: list[ProviderRecord]) -> list[ProviderRecordObject]:
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

    @staticmethod
    def _get_options_object(record: Record) -> OptionsObject:
        """Get options object."""
        return {
            "original": record.watched_original,
            "extended": record.watched_extended,
            "theatre": record.watched_in_theatre,
            "hd": record.watched_in_hd,
            "fullHd": record.watched_in_full_hd,
            "ultraHd": record.watched_in_4k,
            "ignoreRewatch": record.ignore_rewatch,
        }

    def _get_record_objects(self, records: QuerySet[Record]) -> list[RecordObject]:
        """Get record objects."""
        record_objects: list[RecordObject] = []
        for record in records:
            provider_records = self._get_provider_records(record.movie)
            record_object: RecordObject = {
                "id": record.pk,
                "order": record.order,
                "comment": record.comment,
                "commentArea": bool(record.comment),
                "rating": record.rating,
                "providerRecords": self._get_provider_record_objects(provider_records),
                "movie": self._get_movie_object(record.movie),
                "options": self._get_options_object(record),
                "listId": record.list.pk,
                "additionDate": record.date.timestamp(),
            }
            record_objects.append(record_object)
        return record_objects

    def _inject_list_ids(self, records: QuerySet[Record], record_objects: list[RecordObject]) -> None:
        list_data = self._get_list_data(records)
        for record_object in record_objects:
            record_object["listId"] = list_data.get(record_object["id"])

    @staticmethod
    def _get_records(user: Union[User, UserAnonymous]) -> QuerySet[Record]:
        """Get records for certain user."""
        return user.get_records().select_related("movie")

    @staticmethod
    def _get_users() -> list["User"]:
        """Get users."""
        users = User.objects.exclude(hidden=True)
        return list(users)

    def check_if_allowed(self, request: Request, username: Optional[str] = None) -> None:
        """Check if user is allowed to see the page."""
        if username is None and request.user.is_anonymous:  # pylint: disable=duplicate-code
            raise Http404  # pylint: disable=duplicate-code
        user: User = cast(User, request.user)  # pylint: disable=duplicate-code
        if user.username == username:  # pylint: disable=duplicate-code
            return  # pylint: disable=duplicate-code
        self.anothers_account = get_anothers_account(username)
        if self.anothers_account:
            if User.objects.get(username=username) not in self._get_users():
                raise PermissionDenied

    def get(self, request: Request, **kwargs: Any) -> Response:
        """Get data for the list view."""
        username: Optional[str] = kwargs.get("username")
        self.check_if_allowed(request, username)
        anothers_account = self.anothers_account
        user: User = cast(User, request.user) if anothers_account is None else anothers_account
        records = self._get_records(user)
        records = self._sort_records(records)

        actual_user: User = cast(User, request.user)
        if actual_user.is_authenticated and actual_user.is_country_supported:
            prefetch_related_objects(records, "movie__provider_records__provider")

        # if anothers_account:
        #     self._inject_list_ids(records, record_objects)
        record_objects = self._get_record_objects(records)

        return Response(record_objects)


class SaveRecordsOrderView(APIView):
    """
    Save records order view.

    This view is used on the list and gallery pages.
    """

    def put(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Save records order."""
        try:
            records = request.data["records"]
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)

        user: User = cast(User, request.user)
        for record in records:
            try:
                # If record id is not found we silently ignore it
                Record.objects.filter(pk=record["id"], user=user).update(order=record["order"])
            except KeyError:
                # Handle invalid record structure gracefully
                return Response(status=HTTPStatus.BAD_REQUEST)
        return Response()
