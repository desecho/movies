"""Search views."""

import json
from http import HTTPStatus
from operator import itemgetter
from typing import Optional

from django.conf import settings
from django.http import Http404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_exception

from ..models import List, Movie, User
from ..tasks import load_and_save_watch_data_task
from ..tmdb import TmdbInvalidSearchTypeError, TmdbNoImdbIdError, search_movies
from ..types import SearchType, TmdbMovieListResultProcessed
from ..utils import load_movie_data
from .types import MovieListResult, SearchOptions
from .utils import add_movie_to_list, filter_out_movies_user_already_has_in_lists, get_movie_list_result


class SearchMovieView(APIView):
    """Search movie view."""

    permission_classes: list[str] = []  # type: ignore

    @staticmethod
    def _is_popular_movie(popularity: float) -> bool:
        """Return True if movie is popular."""
        return popularity >= settings.MIN_POPULARITY

    @staticmethod
    def _sort_by_date(movies: list[TmdbMovieListResultProcessed]) -> list[TmdbMovieListResultProcessed]:
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

    def _filter_out_unpopular_movies(self, tmdb_movies: list[TmdbMovieListResultProcessed]) -> None:
        for tmdb_movie in list(tmdb_movies):
            if not self._is_popular_movie(tmdb_movie["popularity"]):
                tmdb_movies.remove(tmdb_movie)

    def _get_movies_from_tmdb(
        self, query: str, search_type: SearchType, sort_by_date: bool, popular_only: bool
    ) -> list[MovieListResult]:
        """Get movies from TMDB."""
        lang = self.request.LANGUAGE_CODE
        tmdb_movies = search_movies(query, search_type, lang)
        if sort_by_date:
            tmdb_movies = self._sort_by_date(tmdb_movies)

        if popular_only:
            self._filter_out_unpopular_movies(tmdb_movies)

        return [get_movie_list_result(tmdb_movie, lang) for tmdb_movie in tmdb_movies]

    def get(self, request: Request) -> Response:
        """Return a list of movies based on the search query."""
        try:
            GET = request.GET
            query = GET["query"]
            options: SearchOptions = json.loads(GET["options"])
            type_ = GET["type"]
            search_type: SearchType = type_  # type: ignore
        except KeyError:
            return Response(status=HTTPStatus.BAD_REQUEST)
        try:
            movies = self._get_movies_from_tmdb(query, search_type, options["sortByDate"], options["popularOnly"])
        except TmdbInvalidSearchTypeError:
            return Response(status=HTTPStatus.BAD_REQUEST)
        if request.user.is_authenticated:
            user: User = request.user  # type: ignore
            filter_out_movies_user_already_has_in_lists(movies, user)
        movies = movies[: settings.MAX_RESULTS]
        return Response(movies)


class AddToListFromDbView(APIView):
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

    def post(self, request: Request) -> Response:
        """Add a movie to a list."""
        try:
            tmdb_id = int(request.data["movieId"])
            list_id = int(request.data["listId"])
        except (KeyError, ValueError):
            return Response(status=HTTPStatus.BAD_REQUEST)

        if not List.is_valid_id(list_id):
            raise Http404

        movie_id = self._get_movie_id(tmdb_id)
        user: User = request.user  # type: ignore
        result = self._add_to_list_from_db(movie_id, tmdb_id, list_id, user)
        if not result:
            return Response({"status": "not_found"})
        return Response()
