"""Search views."""
import json
from typing import Optional

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from sentry_sdk import capture_exception

from ..exceptions import NotAvailableSearchTypeError
from ..http import AjaxAuthenticatedHttpRequest, AjaxHttpRequest
from ..models import List, Movie, User
from ..tasks import load_and_save_watch_data_task
from ..tmdb import TmdbNoImdbIdError, get_movies_from_tmdb
from ..utils import load_movie_data
from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView
from .utils import add_movie_to_list


class SearchView(TemplateAnonymousView):
    """Search view."""

    template_name = "search.html"


class SearchMovieView(AjaxAnonymousView):
    """Search movie view."""

    def get(self, request: AjaxHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        """Return a list of movies based on the search query."""
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
                raise NotAvailableSearchTypeError
        except (KeyError, NotAvailableSearchTypeError):
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response
        language_code = request.LANGUAGE_CODE
        movies = get_movies_from_tmdb(query, type_, options, request.user, language_code)
        return self.success(movies=movies)


class AddToListFromDbView(AjaxView):
    """Add to list from DB view."""

    @staticmethod
    def add_movie_to_db(tmdb_id: int) -> int:
        """
        Add a movie to the database.

        Return movie ID.
        """
        movie_data = load_movie_data(tmdb_id)
        movie = Movie(**movie_data)
        movie.save()
        if movie.is_released:
            load_and_save_watch_data_task.delay(movie.pk)
        return movie.pk

    @staticmethod
    def _get_movie_id(tmdb_id: int) -> Optional[int]:
        """
        Get movie ID.

        Return movie ID or None if movie is not found.
        """
        try:
            movie: Movie = Movie.objects.get(tmdb_id=tmdb_id)
            return movie.pk
        except Movie.DoesNotExist:
            return None

    def _add_to_list_from_db(self, movie_id: Optional[int], tmdb_id: int, list_id: int, user: User) -> bool:
        """
        Add a movie to a list from database.

        Return True on success or None on failure.
        """
        # If we don't find the movie in the db we add it to the database.
        if movie_id is None:
            try:
                movie_id = self.add_movie_to_db(tmdb_id)
            except TmdbNoImdbIdError as e:
                capture_exception(e)
                return False
        add_movie_to_list(movie_id, list_id, user)
        return True

    def post(self, request: AjaxAuthenticatedHttpRequest) -> (HttpResponse | HttpResponseBadRequest):
        """Add a movie to a list."""
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
