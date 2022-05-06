import json
from typing import Optional

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from sentry_sdk import capture_exception

from moviesapp.exceptions import MovieNotInDb, NotAvailableSearchType
from moviesapp.http import AjaxAuthenticatedHttpRequest, AjaxHttpRequest
from moviesapp.models import List, Movie, User
from moviesapp.tmdb import get_movies_from_tmdb
from moviesapp.utils import add_movie_to_db

from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView
from .utils import add_movie_to_list


class SearchView(TemplateAnonymousView):
    template_name = "search.html"


class SearchMovieView(AjaxAnonymousView):
    def get(self, request: AjaxHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        AVAILABLE_SEARCH_TYPES = [
            "actor",
            "movie",
            "director",
        ]
        try:
            GET = request.GET
            query = GET["query"]
            options = json.loads(GET["options"])
            type_ = GET["type"]
            if type_ not in AVAILABLE_SEARCH_TYPES:
                raise NotAvailableSearchType
        except (KeyError, NotAvailableSearchType):
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response
        language_code = self.request.LANGUAGE_CODE  # type: ignore
        movies = get_movies_from_tmdb(query, type_, options, request.user, language_code)
        return self.success(movies=movies)


class AddToListFromDbView(AjaxView):
    @staticmethod
    def _get_movie_id(tmdb_id: int) -> Optional[int]:
        """Return movie id or None if movie is not found."""
        try:
            movie: Movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.pk
        except Movie.DoesNotExist:
            return None

    @staticmethod
    def _add_to_list_from_db(movie_id: Optional[int], tmdb_id: int, list_id: int, user: User) -> bool:
        """Return True on success and None of failure."""
        # If we don't find the movie in the db we add it to the database.
        if movie_id is None:
            try:
                movie_id = add_movie_to_db(tmdb_id)
            except MovieNotInDb as e:
                capture_exception(e)
                return False
        add_movie_to_list(movie_id, list_id, user)
        return True

    def post(self, request: AjaxAuthenticatedHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        try:
            POST = request.POST
            tmdb_id = int(POST["movieId"])
            list_id = int(POST["listId"])
        except (KeyError, ValueError):
            response_bad: HttpResponseBadRequest = self.render_bad_request_response()
            return response_bad

        if not List.is_valid_id(list_id):
            raise Http404

        movie_id = self._get_movie_id(tmdb_id)
        result = self._add_to_list_from_db(movie_id, tmdb_id, list_id, request.user)
        if not result:
            output = {"status": "not_found"}
            response: HttpResponse = self.render_json_response(output)
            return response
        return self.success()
