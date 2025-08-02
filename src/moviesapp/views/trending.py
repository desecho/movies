"""Trending view."""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import User
from ..tmdb import get_trending
from .utils import filter_out_movies_user_already_has_in_lists, get_movie_list_result


class TrendingView(APIView):
    """Trending view."""

    def get(self, request: Request) -> Response:  # pylint: disable=no-self-use
        """Return a list of trending movies."""
        tmdb_movies = get_trending()
        movies = [get_movie_list_result(tmdb_movie, request.LANGUAGE_CODE) for tmdb_movie in tmdb_movies]
        if request.user.is_authenticated:
            user: User = request.user  # type: ignore
            filter_out_movies_user_already_has_in_lists(movies, user)
        return Response(movies)
