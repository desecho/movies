"""Search views."""
import json
from datetime import date
from operator import itemgetter
from typing import List as ListType, Optional

from babel.dates import format_date
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from sentry_sdk import capture_exception

from ..exceptions import NotAvailableSearchTypeError
from ..http import AjaxAuthenticatedHttpRequest, AjaxHttpRequest
from ..models import List, Movie, User
from ..tasks import load_and_save_watch_data_task
from ..tmdb import TmdbMovieSearchResultProcessed, TmdbNoImdbIdError, get_poster_url, get_tmdb_url, search_movies
from ..types import MovieSearchResult, SearchOptions, SearchType
from ..utils import load_movie_data
from .mixins import AjaxAnonymousView, AjaxView, TemplateAnonymousView
from .utils import add_movie_to_list


class SearchView(TemplateAnonymousView):
    """Search view."""

    template_name = "search.html"


class SearchMovieView(AjaxAnonymousView):
    """Search movie view."""

    def _filter_out_movies_user_already_has_in_lists(self, movies: ListType[MovieSearchResult]) -> None:
        user: User = self.request.user  # type: ignore
        user_movies_tmdb_ids = list(user.get_records().values_list("movie__tmdb_id", flat=True))
        for movie in list(movies):
            if movie["id"] in user_movies_tmdb_ids:
                movies.remove(movie)

    @staticmethod
    def _is_popular_movie(popularity: float) -> bool:
        """Return True if movie is popular."""
        return popularity >= settings.MIN_POPULARITY

    @staticmethod
    def _sort_by_date(movies: ListType[TmdbMovieSearchResultProcessed]) -> ListType[TmdbMovieSearchResultProcessed]:
        """Sort movies by date."""
        movies_with_date = []
        movies_without_date = []
        for movie in movies:
            if movie["release_date"]:
                movies_with_date.append(movie)
            else:
                movies_without_date.append(movie)
        movies_with_date = sorted(movies_with_date, key=itemgetter("release_date"), reverse=True)
        movies = movies_with_date + movies_without_date
        return movies

    def _format_date(self, date_: Optional[date]) -> Optional[str]:
        """Get date."""
        request: AjaxHttpRequest = self.request  # type: ignore
        if date_:
            return format_date(date_, locale=request.LANGUAGE_CODE)
        return None

    def _get_movies_from_tmdb(
        self, query: str, search_type: SearchType, sort_by_date: bool, popular_only: bool
    ) -> ListType[MovieSearchResult]:
        """Get movies from TMDB."""
        request: AjaxHttpRequest = self.request  # type: ignore
        tmdb_movies = search_movies(query, search_type, request.LANGUAGE_CODE)
        if sort_by_date:
            tmdb_movies = self._sort_by_date(tmdb_movies)
        movies: ListType[MovieSearchResult] = []
        for tmdb_movie in tmdb_movies:
            poster = tmdb_movie["poster_path"]
            # Skip unpopular movies if this option is enabled.
            if popular_only and not self._is_popular_movie(tmdb_movie["popularity"]):
                continue
            tmdb_id = tmdb_movie["id"]
            movie: MovieSearchResult = {
                "id": tmdb_id,
                "tmdbLink": get_tmdb_url(tmdb_id),
                "elementId": f"movie{tmdb_id}",
                "releaseDate": self._format_date(tmdb_movie["release_date"]),
                "title": tmdb_movie["title"],
                "poster": get_poster_url("small", poster),
                "poster2x": get_poster_url("normal", poster),
            }
            movies.append(movie)
        return movies

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
            options: SearchOptions = json.loads(GET["options"])
            type_ = GET["type"]
            if type_ not in AVAILABLE_SEARCH_TYPES:
                raise NotAvailableSearchTypeError
            search_type: SearchType = type_  # type: ignore
        except (KeyError, NotAvailableSearchTypeError):
            response: HttpResponseBadRequest = self.render_bad_request_response()
            return response
        movies = self._get_movies_from_tmdb(query, search_type, options["sortByDate"], options["popularOnly"])
        if request.user.is_authenticated:
            self._filter_out_movies_user_already_has_in_lists(movies)
        movies = movies[: settings.MAX_RESULTS]
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
