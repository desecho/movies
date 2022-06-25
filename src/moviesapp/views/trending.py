"""Trending view."""
import json
from typing import Any

from ..http import HttpRequest
from ..models import User
from ..tmdb import get_trending
from .mixins import TemplateAnonymousView
from .types import TrendingViewContextData
from .utils import filter_out_movies_user_already_has_in_lists, get_movie_list_result


class TrendingView(TemplateAnonymousView):
    """Trending view."""

    template_name = "trending.html"

    def get_context_data(self, **kwargs: Any) -> TrendingViewContextData:  # type: ignore
        """Get context data."""
        tmdb_movies = get_trending()
        request: HttpRequest = self.request  # type: ignore
        movies = [get_movie_list_result(tmdb_movie, request.LANGUAGE_CODE) for tmdb_movie in tmdb_movies]
        if request.user.is_authenticated:
            user: User = request.user
            filter_out_movies_user_already_has_in_lists(movies, user)
        return {
            "movies": json.dumps(movies),
        }
