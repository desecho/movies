import json
from typing import Any, Dict, Optional, Tuple  # pylint: disable=unused-import

from django.conf import settings
from django.db.models import Q, QuerySet
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from moviesapp.models import Action, ActionRecord, List, Movie, Record, User

from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView, TemplateView
from .utils import add_movie_to_list, get_records, paginate, sort_by_rating


class ChangeRatingView(AjaxView):
    def put(self, request: HttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
        try:
            rating = int(request.PUT["rating"])
        except (KeyError, ValueError):
            return self.render_bad_request_response()

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
    def post(self, request: HttpRequest, movie_id: int) -> (HttpResponse | HttpResponseBadRequest):
        try:
            list_id = int(request.POST["listId"])
        except (KeyError, ValueError):
            return self.render_bad_request_response()

        if not List.is_valid_id(list_id):
            raise Http404

        get_object_or_404(Movie, pk=movie_id)
        add_movie_to_list(movie_id, list_id, request.user)
        return self.success()


class RemoveRecordView(AjaxView):
    def delete(self, request: HttpRequest, record_id: int) -> HttpResponse:
        record = get_object_or_404(Record, user=request.user, pk=record_id)
        record.delete()
        return self.success()


class SaveSettingsView(AjaxAnonymousView):
    def put(self, request: HttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        try:
            session_settings = request.PUT["settings"]
        except KeyError:
            return self.render_bad_request_response()

        for setting in session_settings:
            request.session[setting] = session_settings[setting]
        return self.success()


class SaveOptionsView(AjaxView):
    def put(self, request: HttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
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
            return self.render_bad_request_response()

        record.watched_original = watched_original
        record.watched_extended = watched_extended
        record.watched_in_theatre = watched_in_theatre
        record.watched_in_4k = watched_in_4k
        record.watched_in_hd = watched_in_hd
        record.watched_in_full_hd = watched_in_full_hd
        record.save()
        return self.success()


class SaveCommentView(AjaxView):
    def put(self, request: HttpRequest, record_id: int) -> (HttpResponse | HttpResponseBadRequest):
        record = get_object_or_404(Record, user=request.user, pk=record_id)

        try:
            comment = request.PUT["comment"]
        except KeyError:
            return self.render_bad_request_response()

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
    session = None

    @staticmethod
    def _filter_records_for_recommendation(records: QuerySet[Record], user: User) -> QuerySet[Record]:
        """Keep movies only with 3+ rating, removes watched movies."""
        return records.filter(rating__gte=3).exclude(movie__in=user.get_movie_ids())

    def _get_comments_and_ratings(
        self, records_and_movies_ids: QuerySet, user: User
    ) -> "Dict[int, Optional[List[Dict[str, Any]]]]":
        movies, record_ids_and_movies_dict = self._get_record_movie_data(records_and_movies_ids)
        records = Record.objects.filter(list_id=List.WATCHED, movie_id__in=movies)
        friends = user.get_friends()
        if friends is None:
            records = []
        else:
            records = records.filter(user__in=friends)

        comments_and_ratings = {}
        for record in records:
            if record.comment or record.rating:
                data = {"user": record.user}
                if record.movie.pk not in comments_and_ratings:
                    comments_and_ratings[record.movie.pk] = []
                if record.comment:
                    data["comment"] = record.comment
                if record.rating:
                    data["rating"] = record.rating
                comments_and_ratings[record.movie.pk].append(data)
        data = {}
        for record_id, value in record_ids_and_movies_dict.items():
            data[record_id] = comments_and_ratings.get(value, None)
        return data

    @staticmethod
    def _filter_records(records: QuerySet[Record], query: str) -> QuerySet[Record]:
        return records.filter(Q(movie__title_en__icontains=query) | Q(movie__title_ru__icontains=query))

    @staticmethod
    def _sort_records(records: QuerySet[Record], sort: str, username: str, list_name: str) -> QuerySet[Record]:
        if sort == "release_date":
            return records.order_by("-movie__release_date")
        if sort == "rating":
            return sort_by_rating(records, username, list_name)
        if sort == "addition_date":
            return records.order_by("-date")
        raise Exception("Unsupported sort type")

    @staticmethod
    def _get_record_movie_data(records_and_movies_ids: QuerySet) -> "Tuple[List[int], Dict[int, int]]":
        movies = [x[1] for x in records_and_movies_ids]
        return (movies, {x[0]: x[1] for x in records_and_movies_ids})

    def _get_list_data(self, records: QuerySet[Record]):
        movies, record_ids_and_movies_dict = self._get_record_movie_data(records.values_list("id", "movie_id"))
        movie_ids_and_list_ids = (
            self.request.user.get_records().filter(movie_id__in=movies).values_list("movie_id", "list_id")
        )
        movie_id_and_list_id_dict = {}
        for movie_id_and_list_id in movie_ids_and_list_ids:
            movie_id_and_list_id_dict[movie_id_and_list_id[0]] = movie_id_and_list_id[1]

        list_data = {}
        for record_id, value in record_ids_and_movies_dict.items():
            list_data[record_id] = movie_id_and_list_id_dict.get(value, 0)
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

    def get_context_data(self, list_name: str, username: Optional[str] = None) -> Dict[str, Any]:
        self.check_if_allowed(username)
        records = get_records(list_name, self.request.user, self.anothers_account)
        request = self.request
        session = self.session
        query = request.GET.get("query", False)
        if query:
            query = query.strip()
            records = self._filter_records(records, query)
        records = self._sort_records(records, session["sort"], username, list_name)

        if username and session["recommendation"]:
            records = self._filter_records_for_recommendation(records, request.user)

        if username:
            list_data = self._get_list_data(records)
        else:
            list_data = None

        if not username and list_name == "to-watch" and records:
            comments_and_ratings = self._get_comments_and_ratings(records.values_list("id", "movie_id"), request.user)
        else:
            comments_and_ratings = None
        records = paginate(records, request.GET.get("page"), settings.RECORDS_ON_PAGE)
        return {
            "records": records,
            "reviews": comments_and_ratings,
            "list_id": List.objects.get(key_name=list_name).pk,
            "list": list_name,
            "anothers_account": self.anothers_account,
            "list_data": json.dumps(list_data),
            "sort": session["sort"],
            "query": query,
        }

    def get(self, *args, **kwargs):
        self._initialize_session_values()
        return super().get(*args, **kwargs)


class RecommendationsView(TemplateView, ListView):
    template_name = "list/recommendations.html"

    @staticmethod
    def _filter_duplicated_movies_and_limit(records: QuerySet[Record]) -> "Tuple[List[Record], List[Tuple[int, int]]]":
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
        # Exclude own records and include only friends' records.
        records = Record.objects.exclude(user=self.request.user).filter(user__in=friends).select_related("movie")
        # Order records by user rating and by imdb rating.
        records = records.order_by("-rating", "-movie__imdb_rating", "-movie__release_date")
        return self._filter_records_for_recommendation(records, self.request.user)

    def get_context_data(self) -> Dict[str, Any]:
        friends = self.request.user.get_friends()
        records = self._get_recommendations_from_friends(friends)
        records, records_and_movies_ids = self._filter_duplicated_movies_and_limit(records)
        reviews = self._get_comments_and_ratings(records_and_movies_ids, self.request.user)
        return {"records": records, "reviews": reviews}

    def get(self, *args: Any, **kwargs: Any) -> HttpResponse:
        has_friends = self.request.user.has_friends()
        if not has_friends:
            raise Http404
        return super().get(*args, **kwargs)
