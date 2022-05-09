import json
from typing import Any, Dict, List as ListType, Optional, Tuple, Union

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.db.models import Q, QuerySet
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from ..http import AjaxAuthenticatedHttpRequest, AjaxHttpRequest, AuthenticatedHttpRequest, HttpRequest
from ..models import Action, ActionRecord, List, Movie, Record, User, UserAnonymous
from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView, TemplateView
from .utils import add_movie_to_list, get_records, paginate, sort_by_rating


class ChangeRatingView(AjaxView):
    def put(self, request: AjaxAuthenticatedHttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
        try:
            rating = int(request.PUT["rating"])
        except (KeyError, ValueError):
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        record = get_object_or_404(Record, user=request.user, pk=record_id)

        if record.rating != rating:
            if not record.rating:
                ActionRecord(
                    action_id=Action.ADDED_RATING, user=request.user, movie=record.movie, rating=rating
                ).save()
            record.rating = rating
            record.save()
        return self.success()


class AddToListView(AjaxView):
    def post(self, request: AjaxAuthenticatedHttpRequest, movie_id: int) -> (HttpResponse | HttpResponseBadRequest):
        try:
            list_id = int(request.POST["listId"])
        except (KeyError, ValueError):
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        if not List.is_valid_id(list_id):
            raise Http404

        get_object_or_404(Movie, pk=movie_id)
        add_movie_to_list(movie_id, list_id, request.user)
        return self.success()


class RemoveRecordView(AjaxView):
    def delete(self, request: AjaxAuthenticatedHttpRequest, record_id: int) -> HttpResponse:
        record = get_object_or_404(Record, user=request.user, pk=record_id)
        record.delete()
        return self.success()


class SaveSettingsView(AjaxAnonymousView):
    def put(self, request: AjaxHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        try:
            session_settings = request.PUT["settings"]
        except KeyError:
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        for setting in session_settings:
            request.session[setting] = session_settings[setting]
        return self.success()


class SaveOptionsView(AjaxView):
    def put(self, request: AjaxAuthenticatedHttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
        record = get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            options = request.PUT["options"]
            watched_original = options["original"]
            watched_extended = options["extended"]
            watched_in_theatre = options["theatre"]
            watched_in_4k = options["4k"]
            watched_in_hd = options["hd"]
            watched_in_full_hd = options["fullHd"]
        except KeyError:
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        record.watched_original = watched_original
        record.watched_extended = watched_extended
        record.watched_in_theatre = watched_in_theatre
        record.watched_in_4k = watched_in_4k
        record.watched_in_hd = watched_in_hd
        record.watched_in_full_hd = watched_in_full_hd
        record.save()
        return self.success()


class SaveCommentView(AjaxView):
    def put(self, request: AjaxAuthenticatedHttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
        record = get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            comment = request.PUT["comment"]
        except KeyError:
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response

        if record.comment != comment:
            if not record.comment:
                ActionRecord(
                    action_id=Action.ADDED_COMMENT, user=request.user, movie=record.movie, comment=comment
                ).save()
            record.comment = comment
            record.save()
        return self.success()


class ListView(TemplateAnonymousView):
    template_name = "list/list.html"
    session: Optional[SessionBase] = None

    @staticmethod
    def _filter_records_for_recommendation(
        records: QuerySet[Record], user: Union[User, UserAnonymous]
    ) -> QuerySet[Record]:
        """Keep movies only with 3+ rating, removes watched movies."""
        return records.filter(rating__gte=3).exclude(movie__in=user.get_movie_ids())

    def _get_comments_and_ratings(
        self, records_ids_and_movies_ids_list: ListType[Tuple[int, int]], user: Union[User, UserAnonymous]
    ) -> "Dict[int, Optional[ListType[Dict[str, Any]]]]":
        movies, records_ids_and_movies_ids = self._get_record_movie_data(records_ids_and_movies_ids_list)
        records: QuerySet[Record] = Record.objects.filter(list_id=List.WATCHED, movie_id__in=movies)
        friends = user.get_friends()
        records = records.filter(user__in=friends)

        comments_and_ratings: Dict[int, ListType[Dict[str, Any]]] = {}
        for record in records:
            if record.comment or record.rating:
                data: Dict[str, Any] = {"user": record.user}
                movie_id: int = record.movie.pk
                if movie_id not in comments_and_ratings:
                    comments_and_ratings[movie_id] = []
                if record.comment:
                    data["comment"] = record.comment
                if record.rating:
                    data["rating"] = record.rating
                comments_and_ratings[movie_id].append(data)
        result = {}
        for record_id, movie_id in records_ids_and_movies_ids.items():
            result[record_id] = comments_and_ratings.get(movie_id, None)
        return result

    @staticmethod
    def _filter_records(records: QuerySet[Record], query: str) -> QuerySet[Record]:
        return records.filter(Q(movie__title_en__icontains=query) | Q(movie__title_ru__icontains=query))

    @staticmethod
    def _sort_records(
        records: QuerySet[Record], sort: str, username: Optional[str], list_name: str
    ) -> QuerySet[Record]:
        if sort == "release_date":
            return records.order_by("-movie__release_date")
        if sort == "rating":
            return sort_by_rating(records, username, list_name)
        if sort == "addition_date":
            return records.order_by("-date")
        raise Exception("Unsupported sort type")

    @staticmethod
    def _get_record_movie_data(
        records_ids_and_movies_ids_list: ListType[Tuple[int, int]]
    ) -> Tuple[ListType[int], Dict[int, int]]:
        movies_ids = [x[1] for x in records_ids_and_movies_ids_list]
        records_ids_and_movies_ids = {x[0]: x[1] for x in records_ids_and_movies_ids_list}
        return (movies_ids, records_ids_and_movies_ids)

    def _get_list_data(self, records: QuerySet[Record]) -> Dict[int, int]:
        movies_ids, records_and_movies_ids = self._get_record_movie_data(list(records.values_list("id", "movie_id")))
        user: Union[User, UserAnonymous] = self.request.user  # type: ignore
        movies_ids_and_lists_ids_list: ListType[Tuple[int, int]] = list(
            user.get_records().filter(movie_id__in=movies_ids).values_list("movie_id", "list_id")
        )
        movies_and_lists_ids: Dict[int, int] = {}
        for movie_id_and_list_id in movies_ids_and_lists_ids_list:
            movie_id, list_id = movie_id_and_list_id
            movies_and_lists_ids[movie_id] = list_id

        list_data: Dict[int, int] = {}
        for record_id, movie_id in records_and_movies_ids.items():
            list_data[record_id] = movies_and_lists_ids.get(movie_id, 0)
        return list_data

    def _initialize_session_values(self) -> None:
        session = self.request.session
        if "sort" not in session:
            session["sort"] = "addition_date"
        if "recommendation" not in session:
            session["recommendation"] = False
        if "mode" not in session:
            session["mode"] = "full"
        self.session = session

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        list_name: str = kwargs["list_name"]
        username: Optional[str] = kwargs.get("username")
        self.check_if_allowed(username)
        request: HttpRequest = self.request  # type: ignore
        user = request.user if self.anothers_account is None else self.anothers_account
        records = get_records(list_name, user)
        # Session is supposed to be initialized at that point.
        if self.session:
            session = self.session
            query = request.GET.get("query", "")
            if query:
                query = query.strip()
                records = self._filter_records(records, query)
            records = self._sort_records(records, session["sort"], username, list_name)

            if username and session["recommendation"]:
                records = self._filter_records_for_recommendation(records, user)

            if username:
                list_data = self._get_list_data(records)
            else:
                list_data = None

            if not username and list_name == "to-watch" and records:
                comments_and_ratings = self._get_comments_and_ratings(
                    list(records.values_list("id", "movie_id")), user
                )
            else:
                comments_and_ratings = None
            records_ = paginate(records, request.GET.get("page"), settings.RECORDS_ON_PAGE)
            return {
                "records": records_,
                "reviews": comments_and_ratings,
                "list_id": List.objects.get(key_name=list_name).pk,
                "list": list_name,
                "anothers_account": self.anothers_account,
                "list_data": json.dumps(list_data),
                "sort": session["sort"],
                "query": query,
            }
        return {}

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        self._initialize_session_values()
        return super().get(request, *args, **kwargs)


class RecommendationsView(TemplateView, ListView):
    template_name = "list/recommendations.html"

    @staticmethod
    def _filter_duplicated_movies_and_limit(
        records: QuerySet[Record],
    ) -> Tuple[ListType[Record], ListType[Tuple[int, int]]]:
        records_output = []
        movies = []
        records_and_movies_ids = []
        for record in records:
            if record.movie.pk not in movies:
                records_output.append(record)
                records_and_movies_ids.append((record.pk, record.movie.pk))
                if len(records_output) == settings.MAX_RECOMMENDATIONS:
                    break
                movies.append(record.movie.pk)
        return (records_output, records_and_movies_ids)

    def _get_recommendations_from_friends(self, friends: QuerySet[User]) -> QuerySet[Record]:
        user: User = self.request.user  # type: ignore
        # Exclude own records and include only friends' records.
        records = Record.objects.exclude(user=user).filter(user__in=friends).select_related("movie")
        # Order records by user rating and by imdb rating.
        records = records.order_by("-rating", "-movie__imdb_rating", "-movie__release_date")
        return self._filter_records_for_recommendation(records, user)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:  # pylint: disable=unused-argument
        request: AuthenticatedHttpRequest = self.request  # type: ignore
        user = request.user
        friends = user.get_friends()
        records_qs = self._get_recommendations_from_friends(friends)
        records, records_and_movies_ids = self._filter_duplicated_movies_and_limit(records_qs)
        reviews = self._get_comments_and_ratings(records_and_movies_ids, user)
        return {"records": records, "reviews": reviews}

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:  # type: ignore
        has_friends = request.user.has_friends()
        if not has_friends:
            raise Http404
        return super().get(request, *args, **kwargs)
