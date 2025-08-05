"""OpenAI client for movie recommendations."""

import json
from datetime import datetime
from typing import Dict, List, Optional

from django.conf import settings
from openai import OpenAI

from .exceptions import OpenAIConfigurationError, OpenAIError
from .types import RecommendationRequest, RecommendationResponse

SYSTEM_PROMPT = """You are a movie recommendation expert.
Provide personalized movie recommendations based on user preferences and viewing history.

If the user has no specific preferences, recommend popular and critically acclaimed movies.
If the user has specific preferences, tailor recommendations to those preferences.
Ensure recommendations are diverse in genre and style if the user doesn't specify genre.
Avoid recommending movies that the user has already seen.
If the user has a minimum rating preference, ensure all recommendations meet that threshold.
If the user has a preferred year range, recommend movies within that range.
If the user has preferred genres, prioritize those genres in recommendations.
If the user has liked or disliked specific movies, use that information to refine recommendations.
If the user has neutral/unrated movies, use them as context for what they've watched but don't treat them as positive or negative preferences - they provide viewing history context without preference signals.
If the user has a specific number of recommendations in mind, provide that many.
Focus on movies that match their preferences while introducing some variety.

Provide results as a json array of IMDB IDs with the following structure:
```json
[
    {
        "imdb_id": "tt1234567"
    }
]
```
Provide only the json array without any additional text or explanation. No markdown or formatting.
"""

MIN_YEAR = 1888  # The year the first movie was made


class OpenAIClient:
    """Client for OpenAI API interactions."""

    def __init__(self) -> None:
        """Initialize OpenAI client with API key from settings."""
        if not settings.OPENAI_API_KEY:
            raise OpenAIConfigurationError("OPENAI_API_KEY is not configured in settings")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def get_movie_recommendations(self, user_preferences: RecommendationRequest) -> RecommendationResponse:
        """
        Get movie recommendations based on user preferences.

        Args:
            user_preferences: User's movie preferences and history

        Returns:
            RecommendationResponse with recommended movies

        Raises:
            OpenAIError: If API call fails
        """
        try:
            OpenAIClient._validate_user_preferences(user_preferences)
            prompt = OpenAIClient._build_recommendation_prompt(user_preferences)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            content = response.choices[0].message.content
            if content is None:
                raise OpenAIError("OpenAI API returned empty content")
            parsed_content = OpenAIClient._parse_recommendation_response(content)
            self._filter_out_duplicated_ids(parsed_content)
            return parsed_content

        except Exception as e:
            if hasattr(e, "__module__") and "openai" in e.__module__:
                raise OpenAIError(f"OpenAI API error: {str(e)}") from e
            raise OpenAIError(f"Unexpected error: {str(e)}") from e

    @staticmethod
    def _convert_rating(rating: float) -> float:
        """Convert a 5-star rating to a 10-star rating."""
        return rating * 2

    @staticmethod
    def _validate_user_preferences(preferences: RecommendationRequest) -> None:
        """
        Validate user preferences against settings constraints.

        Args:
            preferences: User's movie preferences to validate

        Raises:
            ValueError: If preferences are invalid
        """
        OpenAIClient._validate_recommendations_number(preferences.recommendations_number)
        OpenAIClient._validate_rating(preferences.min_rating)
        OpenAIClient._validate_movie_list(preferences.liked_movies, "liked")
        OpenAIClient._validate_movie_list(preferences.disliked_movies, "disliked")
        OpenAIClient._validate_movie_list(preferences.unrated_movies, "unrated")
        OpenAIClient._validate_genre(preferences.preferred_genre)
        OpenAIClient._validate_year_range(preferences.year_range)

    @staticmethod
    def _validate_recommendations_number(recommendations_number: Optional[int]) -> None:
        """Validate recommendations number."""
        if recommendations_number is not None:
            if not settings.AI_MIN_RECOMMENDATIONS <= recommendations_number <= settings.AI_MAX_RECOMMENDATIONS:
                raise ValueError(
                    f"Number of recommendations must be between {settings.AI_MIN_RECOMMENDATIONS} "
                    f"and {settings.AI_MAX_RECOMMENDATIONS}"
                )

    @staticmethod
    def _validate_rating(min_rating: Optional[int]) -> None:
        """Validate rating."""
        if min_rating is not None:
            if not settings.AI_MIN_RATING <= min_rating <= settings.AI_MAX_RATING:
                raise ValueError(
                    f"Minimum rating must be between {settings.AI_MIN_RATING} " f"and {settings.AI_MAX_RATING}"
                )

    @staticmethod
    def _validate_movie_list(movies: Optional[List[str]], movie_type: str) -> None:
        """Validate movie list (liked or disliked)."""
        if movies is not None:
            for movie in movies:
                if not isinstance(movie, str):
                    raise ValueError(f"All {movie_type} movies must be strings")
                if len(movie.strip()) == 0:
                    raise ValueError(f"{movie_type.capitalize()} movie titles cannot be empty")
                if len(movie) > settings.AI_MAX_MOVIE_TITLE_LENGTH:
                    raise ValueError(
                        f"{movie_type.capitalize()} movie title '{movie[:50]}...' exceeds maximum length of "
                        f"{settings.AI_MAX_MOVIE_TITLE_LENGTH} characters"
                    )

    @staticmethod
    def _validate_genre(preferred_genre: Optional[str]) -> None:
        """Validate preferred genre."""
        if preferred_genre is not None:
            all_valid_genres = settings.MAIN_GENRES + settings.SUBGENRES
            if preferred_genre not in all_valid_genres:
                raise ValueError(
                    f"Preferred genre '{preferred_genre}' is not valid. "
                    f"Valid genres are: {', '.join(all_valid_genres)}"
                )

    @staticmethod
    def _validate_year_range(year_range: Optional[Dict[str, int]]) -> None:
        """Validate year range."""
        if year_range is None:
            return

        if not isinstance(year_range, dict):
            raise ValueError("Year range must be a dictionary with 'start' and 'end' keys")

        if "start" not in year_range or "end" not in year_range:
            raise ValueError("Year range must contain both 'start' and 'end' keys")

        start_year = year_range["start"]
        end_year = year_range["end"]

        if not isinstance(start_year, int) or not isinstance(end_year, int):
            raise ValueError("Year range values must be integers")

        if start_year > end_year:
            raise ValueError("Start year cannot be greater than end year")

        current_year = datetime.now().year
        if start_year < MIN_YEAR or end_year > current_year:
            raise ValueError(f"Year range must be between {MIN_YEAR} and {current_year}")

    @staticmethod
    def _build_recommendation_prompt(preferences: RecommendationRequest) -> str:
        """Build the prompt for movie recommendations."""
        prompt_parts = ["Recommend movies based on the following user preferences:"]

        if preferences.liked_movies:
            liked_movies_str = ", ".join(preferences.liked_movies)
            prompt_parts.append(f"Movies they liked: {liked_movies_str}")

        if preferences.disliked_movies:
            disliked_movies_str = ", ".join(preferences.disliked_movies)
            prompt_parts.append(f"Movies they disliked: {disliked_movies_str}")

        if preferences.unrated_movies:
            unrated_movies_str = ", ".join(preferences.unrated_movies)
            prompt_parts.append(f"Movies they watched but didn't rate (neutral): {unrated_movies_str}")

        if preferences.preferred_genre:
            prompt_parts.append(f"Preferred genre: {preferences.preferred_genre}")

        if preferences.year_range:
            prompt_parts.append(
                f"Preferred year range: {preferences.year_range['start']}-{preferences.year_range['end']}"
            )

        if preferences.min_rating:
            # Converting the rating to the most commonly used IMDB rating scale (0-10)
            min_rating = OpenAIClient._convert_rating(preferences.min_rating)
            prompt_parts.append(f"Minimum rating: {min_rating}/10")

        if preferences.recommendations_number:
            prompt_parts.append(f"Number of recommendations: {preferences.recommendations_number}")
        else:
            prompt_parts.append(f"Number of recommendations: {settings.AI_MAX_RECOMMENDATIONS}")

        return "\n\n".join(prompt_parts)

    @staticmethod
    def _parse_recommendation_response(content: str) -> RecommendationResponse:
        """Parse the OpenAI response into structured data."""
        try:
            parsed_data = json.loads(content.strip())
            if not isinstance(parsed_data, list):
                raise ValueError("Expected a list of recommendations")

            # Validate each item has the required structure
            for item in parsed_data:
                if not isinstance(item, dict) or "imdb_id" not in item:
                    raise ValueError("Each recommendation must have an 'imdb_id' field")

            return parsed_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from OpenAI: {str(e)}") from e

    @staticmethod
    def _filter_out_duplicated_ids(recommendations: RecommendationResponse) -> None:
        """
        Remove duplicate IMDb IDs from recommendations list in-place.

        Args:
            recommendations: List of recommendation items to filter
        """
        seen_ids = set()
        filtered_recommendations = []

        for item in recommendations:
            imdb_id = item.get("imdb_id")
            if imdb_id and imdb_id not in seen_ids:
                seen_ids.add(imdb_id)
                filtered_recommendations.append(item)

        # Clear and update the original list in-place
        recommendations.clear()
        recommendations.extend(filtered_recommendations)
