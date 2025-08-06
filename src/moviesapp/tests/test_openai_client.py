"""Tests for OpenAI client functionality."""

# pylint: disable=protected-access,no-self-use

from datetime import datetime
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from openai import OpenAIError as OpenAIAPIError

from moviesapp.openai.client import OpenAIClient
from moviesapp.openai.exceptions import OpenAIConfigurationError, OpenAIError
from moviesapp.openai.types import RecommendationRequest


class OpenAIClientInitializationTestCase(TestCase):
    """Test cases for OpenAI client initialization."""

    @override_settings(OPENAI_API_KEY=None)
    def test_init_without_api_key_raises_configuration_error(self):
        """Test that initializing without API key raises OpenAIConfigurationError."""
        with self.assertRaises(OpenAIConfigurationError) as context:
            OpenAIClient()

        self.assertEqual(str(context.exception), "OPENAI_API_KEY is not configured in settings")

    @override_settings(OPENAI_API_KEY="")
    def test_init_with_empty_api_key_raises_configuration_error(self):
        """Test that initializing with empty API key raises OpenAIConfigurationError."""
        with self.assertRaises(OpenAIConfigurationError) as context:
            OpenAIClient()

        self.assertEqual(str(context.exception), "OPENAI_API_KEY is not configured in settings")

    @override_settings(OPENAI_API_KEY="test-api-key", OPENAI_MODEL="gpt-4")
    @patch("moviesapp.openai.client.OpenAI")
    def test_init_with_valid_api_key_creates_client(self, mock_openai):
        """Test that initializing with valid API key creates OpenAI client."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        client = OpenAIClient()

        mock_openai.assert_called_once_with(api_key="test-api-key")
        self.assertEqual(client.client, mock_client_instance)
        self.assertEqual(client.model, "gpt-4")


class OpenAIClientValidationTestCase(TestCase):
    """Test cases for OpenAI client validation methods."""

    @override_settings(AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10)
    def test_validate_recommendations_number_valid(self):
        """Test validation of valid recommendations number."""
        OpenAIClient._validate_recommendations_number(5)
        OpenAIClient._validate_recommendations_number(1)
        OpenAIClient._validate_recommendations_number(10)
        OpenAIClient._validate_recommendations_number(None)

    @override_settings(AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10)
    def test_validate_recommendations_number_invalid(self):
        """Test validation of invalid recommendations number."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_recommendations_number(0)
        self.assertIn("Number of recommendations must be between 1 and 10", str(context.exception))

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_recommendations_number(11)
        self.assertIn("Number of recommendations must be between 1 and 10", str(context.exception))

    @override_settings(AI_MIN_RATING=1, AI_MAX_RATING=5)
    def test_validate_rating_valid(self):
        """Test validation of valid ratings."""
        OpenAIClient._validate_rating(3)
        OpenAIClient._validate_rating(1)
        OpenAIClient._validate_rating(5)
        OpenAIClient._validate_rating(None)

    @override_settings(AI_MIN_RATING=1, AI_MAX_RATING=5)
    def test_validate_rating_invalid(self):
        """Test validation of invalid ratings."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_rating(0)
        self.assertIn("Minimum rating must be between 1 and 5", str(context.exception))

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_rating(6)
        self.assertIn("Minimum rating must be between 1 and 5", str(context.exception))

    @override_settings(AI_MAX_MOVIE_TITLE_LENGTH=100)
    def test_validate_movie_list_valid(self):
        """Test validation of valid movie lists."""
        OpenAIClient._validate_movie_list(["Movie 1", "Movie 2"], "liked")
        OpenAIClient._validate_movie_list([], "liked")
        OpenAIClient._validate_movie_list(None, "liked")

    @override_settings(AI_MAX_MOVIE_TITLE_LENGTH=100)
    def test_validate_movie_list_non_string_items(self):
        """Test validation fails for non-string movie items."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_movie_list([123, "Movie 2"], "liked")
        self.assertEqual(str(context.exception), "All liked movies must be strings")

    @override_settings(AI_MAX_MOVIE_TITLE_LENGTH=100)
    def test_validate_movie_list_empty_titles(self):
        """Test validation fails for empty movie titles."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_movie_list(["", "Movie 2"], "disliked")
        self.assertEqual(str(context.exception), "Disliked movie titles cannot be empty")

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_movie_list(["   ", "Movie 2"], "disliked")
        self.assertEqual(str(context.exception), "Disliked movie titles cannot be empty")

    @override_settings(AI_MAX_MOVIE_TITLE_LENGTH=10)
    def test_validate_movie_list_long_titles(self):
        """Test validation fails for overly long movie titles."""
        long_title = "A" * 11
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_movie_list([long_title], "unrated")

        expected_message = f"Unrated movie title '{long_title[:50]}...' exceeds maximum length of 10 characters"
        self.assertEqual(str(context.exception), expected_message)

    @override_settings(MAIN_GENRES=["Action", "Comedy"], SUBGENRES=["Thriller", "Romance"])
    def test_validate_genre_valid(self):
        """Test validation of valid genres."""
        OpenAIClient._validate_genre("Action")
        OpenAIClient._validate_genre("Comedy")
        OpenAIClient._validate_genre("Thriller")
        OpenAIClient._validate_genre("Romance")
        OpenAIClient._validate_genre(None)

    @override_settings(MAIN_GENRES=["Action", "Comedy"], SUBGENRES=["Thriller", "Romance"])
    def test_validate_genre_invalid(self):
        """Test validation fails for invalid genres."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_genre("Horror")

        expected_message = "Preferred genre 'Horror' is not valid. Valid genres are: Action, Comedy, Thriller, Romance"
        self.assertEqual(str(context.exception), expected_message)

    def test_validate_year_range_valid(self):
        """Test validation of valid year ranges."""
        current_year = datetime.now().year

        OpenAIClient._validate_year_range({"start": 2000, "end": 2020})
        OpenAIClient._validate_year_range({"start": 1888, "end": current_year})
        OpenAIClient._validate_year_range({"start": 2010, "end": 2010})
        OpenAIClient._validate_year_range(None)

    def test_validate_year_range_invalid_structure(self):
        """Test validation fails for invalid year range structure."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range("not_a_dict")
        self.assertEqual(str(context.exception), "Year range must be a dictionary with 'start' and 'end' keys")

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": 2000})
        self.assertEqual(str(context.exception), "Year range must contain both 'start' and 'end' keys")

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"end": 2020})
        self.assertEqual(str(context.exception), "Year range must contain both 'start' and 'end' keys")

    def test_validate_year_range_invalid_types(self):
        """Test validation fails for invalid year range types."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": "2000", "end": 2020})
        self.assertEqual(str(context.exception), "Year range values must be integers")

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": 2000, "end": "2020"})
        self.assertEqual(str(context.exception), "Year range values must be integers")

    def test_validate_year_range_invalid_order(self):
        """Test validation fails when start year is greater than end year."""
        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": 2020, "end": 2010})
        self.assertEqual(str(context.exception), "Start year cannot be greater than end year")

    def test_validate_year_range_invalid_bounds(self):
        """Test validation fails for years outside valid bounds."""
        current_year = datetime.now().year

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": 1887, "end": 2020})
        self.assertEqual(str(context.exception), f"Year range must be between 1888 and {current_year}")

        with self.assertRaises(ValueError) as context:
            OpenAIClient._validate_year_range({"start": 2000, "end": current_year + 1})
        self.assertEqual(str(context.exception), f"Year range must be between 1888 and {current_year}")


class OpenAIClientPromptBuildingTestCase(TestCase):
    """Test cases for prompt building functionality."""

    def test_build_recommendation_prompt_empty_preferences(self):
        """Test building prompt with empty preferences."""
        preferences = RecommendationRequest()
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        expected_lines = [
            "Recommend movies based on the following user preferences:",
            f"Number of recommendations: {settings.AI_MAX_RECOMMENDATIONS}",
        ]
        self.assertEqual(prompt, "\n\n".join(expected_lines))

    def test_build_recommendation_prompt_with_liked_movies(self):
        """Test building prompt with liked movies."""
        preferences = RecommendationRequest(liked_movies=["Movie A", "Movie B"])
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Movies they liked: Movie A, Movie B", prompt)

    def test_build_recommendation_prompt_with_disliked_movies(self):
        """Test building prompt with disliked movies."""
        preferences = RecommendationRequest(disliked_movies=["Movie C", "Movie D"])
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Movies they disliked: Movie C, Movie D", prompt)

    def test_build_recommendation_prompt_with_unrated_movies(self):
        """Test building prompt with unrated movies."""
        preferences = RecommendationRequest(unrated_movies=["Movie E"])
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Movies they watched but didn't rate (neutral): Movie E", prompt)

    def test_build_recommendation_prompt_with_preferred_genre(self):
        """Test building prompt with preferred genre."""
        preferences = RecommendationRequest(preferred_genre="Action")
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Preferred genre: Action", prompt)

    def test_build_recommendation_prompt_with_year_range(self):
        """Test building prompt with year range."""
        preferences = RecommendationRequest(year_range={"start": 2000, "end": 2010})
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Preferred year range: 2000-2010", prompt)

    def test_build_recommendation_prompt_with_min_rating(self):
        """Test building prompt with minimum rating."""
        preferences = RecommendationRequest(min_rating=4)
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        # Rating should be converted from 5-star to 10-star scale
        self.assertIn("Minimum rating: 8/10", prompt)

    def test_build_recommendation_prompt_with_recommendations_number(self):
        """Test building prompt with specific number of recommendations."""
        preferences = RecommendationRequest(recommendations_number=5)
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn("Number of recommendations: 5", prompt)

    def test_build_recommendation_prompt_without_recommendations_number(self):
        """Test building prompt without recommendations number uses default."""
        preferences = RecommendationRequest(recommendations_number=None)
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        self.assertIn(f"Number of recommendations: {settings.AI_MAX_RECOMMENDATIONS}", prompt)

    def test_build_recommendation_prompt_comprehensive(self):
        """Test building prompt with all preferences."""
        preferences = RecommendationRequest(
            liked_movies=["Movie A", "Movie B"],
            disliked_movies=["Movie C"],
            unrated_movies=["Movie D"],
            preferred_genre="Comedy",
            year_range={"start": 1990, "end": 2000},
            min_rating=3,
            recommendations_number=7,
        )
        prompt = OpenAIClient._build_recommendation_prompt(preferences)

        expected_content = [
            "Recommend movies based on the following user preferences:",
            "Movies they liked: Movie A, Movie B",
            "Movies they disliked: Movie C",
            "Movies they watched but didn't rate (neutral): Movie D",
            "Preferred genre: Comedy",
            "Preferred year range: 1990-2000",
            "Minimum rating: 6/10",
            "Number of recommendations: 7",
        ]

        for content in expected_content:
            self.assertIn(content, prompt)

    def test_convert_rating(self):
        """Test rating conversion from 5-star to 10-star scale."""
        self.assertEqual(OpenAIClient._convert_rating(1.0), 2.0)
        self.assertEqual(OpenAIClient._convert_rating(2.5), 5.0)
        self.assertEqual(OpenAIClient._convert_rating(5.0), 10.0)


class OpenAIClientResponseParsingTestCase(TestCase):
    """Test cases for response parsing functionality."""

    def test_parse_recommendation_response_valid(self):
        """Test parsing valid recommendation response."""
        json_response = '[{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]'
        result = OpenAIClient._parse_recommendation_response(json_response)

        expected = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]
        self.assertEqual(result, expected)

    def test_parse_recommendation_response_with_whitespace(self):
        """Test parsing response with leading/trailing whitespace."""
        json_response = '  [{"imdb_id": "tt1234567"}]  '
        result = OpenAIClient._parse_recommendation_response(json_response)

        expected = [{"imdb_id": "tt1234567"}]
        self.assertEqual(result, expected)

    def test_parse_recommendation_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        invalid_json = '{"imdb_id": "tt1234567"'  # Missing closing brace

        with self.assertRaises(ValueError) as context:
            OpenAIClient._parse_recommendation_response(invalid_json)

        self.assertIn("Invalid JSON response from OpenAI", str(context.exception))

    def test_parse_recommendation_response_not_list(self):
        """Test parsing response that's not a list."""
        json_response = '{"imdb_id": "tt1234567"}'

        with self.assertRaises(ValueError) as context:
            OpenAIClient._parse_recommendation_response(json_response)

        self.assertEqual(str(context.exception), "Expected a list of recommendations")

    def test_parse_recommendation_response_missing_imdb_id(self):
        """Test parsing response with missing imdb_id field."""
        json_response = '[{"title": "Some Movie"}]'

        with self.assertRaises(ValueError) as context:
            OpenAIClient._parse_recommendation_response(json_response)

        self.assertEqual(str(context.exception), "Each recommendation must have an 'imdb_id' field")

    def test_parse_recommendation_response_invalid_item_structure(self):
        """Test parsing response with invalid item structure."""
        json_response = '["tt1234567"]'  # String instead of dict

        with self.assertRaises(ValueError) as context:
            OpenAIClient._parse_recommendation_response(json_response)

        self.assertEqual(str(context.exception), "Each recommendation must have an 'imdb_id' field")

    def test_parse_recommendation_response_empty_list(self):
        """Test parsing empty response list."""
        json_response = "[]"
        result = OpenAIClient._parse_recommendation_response(json_response)

        self.assertEqual(result, [])


class OpenAIClientDeduplicationTestCase(TestCase):
    """Test cases for deduplication functionality."""

    def test_filter_out_duplicated_ids_no_duplicates(self):
        """Test filtering when there are no duplicates."""
        recommendations = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}, {"imdb_id": "tt9999999"}]
        original_data = recommendations.copy()

        OpenAIClient._filter_out_duplicated_ids(recommendations)

        self.assertEqual(recommendations, original_data)

    def test_filter_out_duplicated_ids_with_duplicates(self):
        """Test filtering when there are duplicates."""
        recommendations = [
            {"imdb_id": "tt1234567"},
            {"imdb_id": "tt7654321"},
            {"imdb_id": "tt1234567"},  # Duplicate
            {"imdb_id": "tt9999999"},
            {"imdb_id": "tt7654321"},  # Another duplicate
        ]

        OpenAIClient._filter_out_duplicated_ids(recommendations)

        expected = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}, {"imdb_id": "tt9999999"}]
        self.assertEqual(recommendations, expected)

    def test_filter_out_duplicated_ids_empty_list(self):
        """Test filtering empty list."""
        recommendations = []
        OpenAIClient._filter_out_duplicated_ids(recommendations)
        self.assertEqual(recommendations, [])

    def test_filter_out_duplicated_ids_missing_imdb_id(self):
        """Test filtering with missing imdb_id values."""
        recommendations = [
            {"imdb_id": "tt1234567"},
            {"other_field": "value"},  # Missing imdb_id
            {"imdb_id": "tt7654321"},
            {"imdb_id": None},  # None imdb_id
        ]

        OpenAIClient._filter_out_duplicated_ids(recommendations)

        expected = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]
        self.assertEqual(recommendations, expected)

    def test_filter_out_duplicated_ids_modifies_in_place(self):
        """Test that filtering modifies the original list in place."""
        original_list = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt1234567"}]  # Duplicate
        list_id = id(original_list)

        OpenAIClient._filter_out_duplicated_ids(original_list)

        # List object should be the same
        self.assertEqual(id(original_list), list_id)
        # But content should be filtered
        self.assertEqual(original_list, [{"imdb_id": "tt1234567"}])


class OpenAIClientIntegrationTestCase(TestCase):
    """Integration test cases for the main OpenAI client functionality."""

    @override_settings(
        OPENAI_API_KEY="test-api-key",
        OPENAI_MODEL="gpt-4",
        OPENAI_MAX_TOKENS=1000,
        OPENAI_TEMPERATURE=0.7,
        AI_MIN_RECOMMENDATIONS=1,
        AI_MAX_RECOMMENDATIONS=10,
        AI_MIN_RATING=1,
        AI_MAX_RATING=5,
        AI_MAX_MOVIE_TITLE_LENGTH=100,
        MAIN_GENRES=["Action"],
        SUBGENRES=["Thriller"],
    )
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_success(self, mock_openai):
        """Test successful movie recommendations flow."""
        # Setup mock OpenAI client
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = '[{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_response

        # Create client and request
        client = OpenAIClient()
        preferences = RecommendationRequest(liked_movies=["Movie A"], recommendations_number=2)

        # Make request
        result = client.get_movie_recommendations(preferences)

        # Verify API call
        mock_client_instance.chat.completions.create.assert_called_once()
        call_args = mock_client_instance.chat.completions.create.call_args

        self.assertEqual(call_args.kwargs["model"], "gpt-4")
        self.assertEqual(call_args.kwargs["max_tokens"], 1000)
        self.assertEqual(call_args.kwargs["temperature"], 0.7)

        messages = call_args.kwargs["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertIn("Movie A", messages[1]["content"])

        # Verify result
        expected_result = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]
        self.assertEqual(result, expected_result)

    @override_settings(
        OPENAI_API_KEY="test-api-key", OPENAI_MODEL="gpt-4", AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10
    )
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_validation_error(self, mock_openai):
        """Test that validation errors are properly raised."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        client = OpenAIClient()
        preferences = RecommendationRequest(recommendations_number=20)  # Invalid

        with self.assertRaises(OpenAIError) as context:
            client.get_movie_recommendations(preferences)

        self.assertIn("Unexpected error:", str(context.exception))
        self.assertIn("Number of recommendations must be between 1 and 10", str(context.exception))

    @override_settings(OPENAI_API_KEY="test-api-key")
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_empty_content(self, mock_openai):
        """Test handling of empty content from OpenAI API."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock response with empty content
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = None
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_response

        client = OpenAIClient()
        preferences = RecommendationRequest()

        with self.assertRaises(OpenAIError) as context:
            client.get_movie_recommendations(preferences)

        self.assertEqual(str(context.exception), "OpenAI API error: OpenAI API returned empty content")

    @override_settings(OPENAI_API_KEY="test-api-key")
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_invalid_json_response(self, mock_openai):
        """Test handling of invalid JSON response."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock response with invalid JSON
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Invalid JSON response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_response

        client = OpenAIClient()
        preferences = RecommendationRequest()

        with self.assertRaises(OpenAIError) as context:
            client.get_movie_recommendations(preferences)

        self.assertIn("Unexpected error:", str(context.exception))

    @override_settings(OPENAI_API_KEY="test-api-key")
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_openai_api_error(self, mock_openai):
        """Test handling of OpenAI API errors."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Create a mock OpenAI API error
        api_error = OpenAIAPIError("Rate limit exceeded")
        api_error.__module__ = "openai.exceptions"

        mock_client_instance.chat.completions.create.side_effect = api_error

        client = OpenAIClient()
        preferences = RecommendationRequest()

        with self.assertRaises(OpenAIError) as context:
            client.get_movie_recommendations(preferences)

        self.assertIn("OpenAI API error:", str(context.exception))

    @override_settings(OPENAI_API_KEY="test-api-key")
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_with_duplicates(self, mock_openai):
        """Test that duplicate recommendations are filtered out."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock response with duplicates
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = '[{"imdb_id": "tt1234567"}, {"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_response

        client = OpenAIClient()
        preferences = RecommendationRequest()

        result = client.get_movie_recommendations(preferences)

        # Should have duplicates filtered out
        expected_result = [{"imdb_id": "tt1234567"}, {"imdb_id": "tt7654321"}]
        self.assertEqual(result, expected_result)

    @override_settings(OPENAI_API_KEY="test-api-key")
    @patch("moviesapp.openai.client.OpenAI")
    def test_get_movie_recommendations_generic_exception(self, mock_openai):
        """Test handling of generic exceptions."""
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance

        # Mock a generic exception
        mock_client_instance.chat.completions.create.side_effect = RuntimeError("Something went wrong")

        client = OpenAIClient()
        preferences = RecommendationRequest()

        with self.assertRaises(OpenAIError) as context:
            client.get_movie_recommendations(preferences)

        self.assertIn("Unexpected error: Something went wrong", str(context.exception))
