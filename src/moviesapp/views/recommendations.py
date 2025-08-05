"""AI Recommendations view."""

from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Dict, List, Optional

import tmdbsimple as tmdb
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_exception

from ..models import User
from ..openai.client import OpenAIClient
from ..openai.exceptions import OpenAIError
from ..openai.types import RecommendationRequest, RecommendationResponse
from ..types import TmdbMovieListResultProcessed
from .types import MovieListResult
from .utils import filter_out_movies_user_already_has_in_lists, get_movie_list_result

tmdb.API_KEY = settings.TMDB_KEY

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission


def _get_tmdb_movie_from_imdb_id(imdb_id: str) -> Optional[TmdbMovieListResultProcessed]:
    """Get TMDB movie data from IMDB ID."""
    try:
        # Use TMDB Find API to search by external IMDB ID
        find = tmdb.Find(imdb_id)
        results = find.info(external_source="imdb_id")

        # Get movie results
        movie_results = results.get("movie_results", [])
        if not movie_results:
            return None

        # Take the first result and convert to our expected format
        movie = movie_results[0]

        # Parse release date
        release_date = None
        if movie.get("release_date"):
            try:
                release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d").date()
            except ValueError:
                release_date = None

        return TmdbMovieListResultProcessed(
            id=movie["id"],
            title=movie["title"],
            title_original=movie["original_title"],
            poster_path=movie["poster_path"],
            release_date=release_date,
            popularity=movie["popularity"],
        )
    except (KeyError, ValueError, TypeError):
        return None


class RecommendationsView(APIView):
    """AI Recommendations view."""

    permission_classes: list[type["BasePermission"]] = []

    @staticmethod
    def _parse_year_range(year_start: Optional[str], year_end: Optional[str]) -> Optional[Dict[str, int]]:
        """Parse year range parameters."""
        if not year_start or not year_end:
            return None
        try:
            return {"start": int(year_start), "end": int(year_end)}
        except ValueError as exc:
            raise ValueError("Invalid year range values") from exc

    @staticmethod
    def _parse_min_rating(min_rating: Optional[str]) -> Optional[int]:
        """Parse minimum rating parameter."""
        if not min_rating:
            return None
        try:
            min_rating_int = int(min_rating)
            if not settings.AI_MIN_RATING <= min_rating_int <= settings.AI_MAX_RATING:
                raise ValueError(
                    f"Minimum rating must be between {settings.AI_MIN_RATING} " f"and {settings.AI_MAX_RATING}"
                )
            return min_rating_int
        except ValueError as exc:
            if "must be between" in str(exc):
                raise
            raise ValueError("Invalid minimum rating value") from exc

    @staticmethod
    def _parse_recommendations_number(recommendations_number: Optional[str]) -> Optional[int]:
        """Parse recommendations number parameter."""
        if not recommendations_number:
            return None
        try:
            recommendations_number_int = int(recommendations_number)
            min_recs = settings.AI_MIN_RECOMMENDATIONS
            max_recs = settings.AI_MAX_RECOMMENDATIONS
            if not min_recs <= recommendations_number_int <= max_recs:
                raise ValueError(f"Number of recommendations must be between {min_recs} and {max_recs}")
            return recommendations_number_int
        except ValueError as exc:
            if "must be between" in str(exc):
                raise
            raise ValueError("Invalid recommendations number value") from exc

    @staticmethod
    def _convert_recommendations_to_movies(
        recommendations: RecommendationResponse, lang: str
    ) -> List[MovieListResult]:
        """Convert IMDB recommendations to movie list results."""
        movies = []
        for recommendation in recommendations:
            try:
                tmdb_movie = _get_tmdb_movie_from_imdb_id(recommendation["imdb_id"])
                if tmdb_movie:
                    movie_result = get_movie_list_result(tmdb_movie, lang)
                    movies.append(movie_result)
            except (KeyError, ValueError, TypeError) as exc:
                # Log but don't fail the entire request if one movie fails
                capture_exception(exc)
                continue
        return movies

    def get(self, request: Request) -> Response:
        """Return AI-generated movie recommendations based on user preferences."""
        try:
            # Parse query parameters
            preferred_genre = request.GET.get("preferredGenre")
            year_start = request.GET.get("yearStart")
            year_end = request.GET.get("yearEnd")
            min_rating = request.GET.get("minRating")
            recommendations_number = request.GET.get("recommendationsNumber")

            # Parse and validate parameters
            try:
                year_range = self._parse_year_range(year_start, year_end)
                min_rating_int = self._parse_min_rating(min_rating)
                recommendations_number_int = self._parse_recommendations_number(recommendations_number)
            except ValueError as exc:
                return Response({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

            # Build recommendation request
            recommendation_request = RecommendationRequest(
                preferred_genre=preferred_genre,
                year_range=year_range,
                min_rating=min_rating_int,
                recommendations_number=recommendations_number_int or settings.AI_MAX_RECOMMENDATIONS,
            )

            # Get recommendations from OpenAI
            try:
                openai_client = OpenAIClient()
                recommendations = openai_client.get_movie_recommendations(recommendation_request)
            except OpenAIError as exc:
                capture_exception(exc)
                return Response(
                    {"error": "Failed to get AI recommendations. Please try again later."},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

            # Convert IMDB IDs to movie list results
            movies = RecommendationsView._convert_recommendations_to_movies(recommendations, request.LANGUAGE_CODE)

            # Filter out movies user already has in lists if authenticated
            if request.user.is_authenticated:
                user: User = request.user
                filter_out_movies_user_already_has_in_lists(movies, user)

            return Response(movies)

        except (AttributeError, TypeError, KeyError) as exc:
            capture_exception(exc)
            return Response({"error": "An unexpected error occurred"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
