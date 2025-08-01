"""List views."""

from http import HTTPStatus
from typing import Optional, Union

from django.db.models import Q, QuerySet, prefetch_related_objects
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..http import AjaxHttpRequest, AuthenticatedHttpRequest, HttpRequest
from ..models import Action, ActionRecord, List, Movie, ProviderRecord, Record, User, UserAnonymous
from .mixins import AjaxAnonymousView
from .types import MovieObject, OptionsObject, ProviderObject, ProviderRecordObject, RecordObject, SortType
from .utils import add_movie_to_list


class ChangeRatingView(APIView):
    """Change rating view."""

    def put(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Change rating."""
        try:
            rating = int(request.PUT["rating"])
        except (KeyError, ValueError):
            return Response(status=HTTPStatus.BAD_REQUEST)

        record = get_object_or_404(Record, user=request.user, pk=record_id)

        user: User = request.user  # type: ignore
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
        user: User = request.user  # type: ignore
        add_movie_to_list(movie_id, list_id, user)
        return Response()


class RemoveRecordView(APIView):
    """Remove record view."""

    def delete(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Remove record."""
        record = get_object_or_404(Record, user=request.user, pk=record_id)
        record.delete()
        return Response()


class SaveSettingsView(AjaxAnonymousView):
    """Save settings view."""

    def put(self, request: AjaxHttpRequest) -> HttpResponse | HttpResponseBadRequest:
        """Save settings."""
        try:
            session_settings = request.PUT["settings"]
        except KeyError:
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        sort_settings = session_settings.pop("sort", {})
        if "sort" not in request.session:
            request.session["sort"] = {}
        for list_name, sort_type in sort_settings.items():
            request.session["sort"][list_name] = sort_type
        for setting in session_settings:
            request.session[setting] = session_settings[setting]
        return self.success()


class SaveOptionsView(APIView):
    """Save options view."""

    def put(self, request: Request, record_id: int) -> Response:  # pylint: disable=no-self-use
        """Save options."""
        get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            options_object: OptionsObject = request.PUT["options"]
            options = {
                "watched_original": options_object["original"],
                "watched_extended": options_object["extended"],
                "watched_in_theatre": options_object["theatre"],
                "watched_in_4k": options_object["ultraHd"],
                "watched_in_hd": options_object["hd"],
                "watched_in_full_hd": options_object["fullHd"],
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
            comment = request.PUT["comment"]
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)

        user: User = request.user  # type: ignore
        if record.comment != comment:
            if not record.comment:
                ActionRecord(action_id=Action.ADDED_COMMENT, user=user, movie=record.movie, comment=comment).save()
            record.comment = comment
            record.save()
        return Response()


class RecordsView(APIView):
    """Records view."""

    anothers_account: Optional[User] = None

    @staticmethod
    def _filter_records_for_recommendations(
        records: QuerySet[Record], user: Union[User, UserAnonymous]
    ) -> QuerySet[Record]:
        """Keep movies only with 3+ rating, remove watched movies."""
        return records.filter(rating__gte=3).exclude(movie__in=user.get_movie_ids())

    @staticmethod
    def _filter_records(records: QuerySet[Record], query: str) -> QuerySet[Record]:
        """Filter records."""
        return records.filter(Q(movie__title_en__icontains=query) | Q(movie__title_ru__icontains=query))

    @staticmethod
    def _sort_by_rating(records: QuerySet[Record], username: Optional[str], list_name: str) -> QuerySet[Record]:
        """Sort records by rating."""
        if not username and list_name == "to-watch":
            # Sorting is changing here because there is no user rating yet.
            return records.order_by("-movie__imdb_rating", "-movie__release_date")
        return records.order_by("-rating", "-movie__release_date")

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
        user: Union[User, UserAnonymous] = self.request.user  # type: ignore
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

    def _sanitize_session_values(self) -> None:
        """
        Sanitize session values.

        We want to make sure that the session values are valid.
        We need to do this in case a user manually set the wrong session values
        or if the code changes resulted in invalid values.
        """
        SORT_TYPES: list[SortType] = ["releaseDate", "rating", "additionDate", "custom"]
        MODES = ["full", "compact", "minimal", "gallery"]
        LIST_NAMES = ["watched", "to-watch"]
        session = self.request.session

        sort = session.get("sort", {})
        if isinstance(sort, dict):
            for list_, sort_type in dict(sort).items():
                if list_ not in LIST_NAMES or sort_type not in SORT_TYPES:
                    session["sort"].pop(list_)
        else:
            session.pop("sort")

        mode = session.get("mode")
        if mode not in MODES:
            session.pop("mode", None)

    def _initialize_session_values(self) -> None:
        """Initialize session values."""
        session = self.request.session
        if "sort" not in session:
            session["sort"] = {}
        if "watched" not in session["sort"]:
            session["sort"]["watched"] = "additionDate"
        if "to-watch" not in session["sort"]:
            session["sort"]["to-watch"] = "custom"
        if "recommendations" not in session:
            session["recommendations"] = False
        if "mode" not in session:
            session["mode"] = "full"

    def _filter_out_provider_records_for_other_countries(self, provider_records: list[ProviderRecord]) -> None:
        request: AuthenticatedHttpRequest = self.request  # type: ignore
        for provider_record in list(provider_records):
            if request.user.country != provider_record.country:
                provider_records.remove(provider_record)

    def _get_provider_records(self, movie: Movie) -> list[ProviderRecord]:
        request: HttpRequest = self.request  # type: ignore
        if request.user.is_authenticated and request.user.is_country_supported and movie.is_released:
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

    # def check_if_allowed(self, request: Request, username: Optional[str] = None) -> None:
    #     """Check if user is allowed to see the page."""
    #     if username is None and request.user.is_anonymous:  # pylint: disable=duplicate-code
    #         raise Http404  # pylint: disable=duplicate-code
    #     user: User = request.user  # type: ignore  # pylint: disable=duplicate-code
    #     if user.username == username:  # pylint: disable=duplicate-code
    #         return  # pylint: disable=duplicate-code
    #     self.anothers_account = get_anothers_account(username)
    #     if self.anothers_account:
    #         if User.objects.get(username=username) not in user.get_users():
    #             raise PermissionDenied

    def get(self, request: Request) -> Response:
        """Get data for the list view."""
        # self._sanitize_session_values()
        # self._initialize_session_values()

        # username: Optional[str] = kwargs.get("username")
        # self.check_if_allowed(request, username)
        anothers_account = self.anothers_account
        user: User = request.user if anothers_account is None else anothers_account  # type: ignore
        records = self._get_records(user)
        # Session is supposed to be initialized at that point.
        # session = self.request.session
        # query = request.GET.get("query", "")
        # if query:
        #     query = query.strip()
        #     records = self._filter_records(records, query)
        records = self._sort_records(records)

        # if anothers_account and session["recommendations"]:
        #     records = self._filter_records_for_recommendations(records, request.user)
        actual_user: User = request.user  # type: ignore
        if actual_user.is_authenticated and actual_user.is_country_supported:
            prefetch_related_objects(records, "movie__provider_records__provider")

        # list_id = List.objects.get(key_name=list_name).pk
        # if list_id == List.TO_WATCH:
        #     records_on_page = records.count()
        # else:  # List - watched
        #     records_on_page = settings.RECORDS_ON_PAGE
        # records_paginated: Page[Record] | list[Record] = paginate(  # type: ignore
        #     records, request.GET.get("page"), records_on_page
        # )
        # records_paginated_ids = [record.pk for record in records_paginated]
        # record_objects = self._get_record_objects(records.filter(pk__in=records_paginated_ids))
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

        user: User = request.user  # type: ignore
        for record in records:
            # If record id is not found we silently ignore it
            Record.objects.filter(pk=record["id"], user=user).update(order=record["order"])
        return Response()
