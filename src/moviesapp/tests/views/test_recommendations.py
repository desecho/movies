# pylint: disable=duplicate-code,protected-access,unused-argument,too-many-public-methods

from datetime import date
from http import HTTPStatus
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from moviesapp.models import List, Movie, Record, User
from moviesapp.openai.exceptions import OpenAIError
from moviesapp.openai.types import RecommendationRequest
from moviesapp.views.recommendations import RecommendationsView, _get_tmdb_movie_from_imdb_id

from ..base import BaseTestCase


class GetTmdbMovieFromImdbIdTestCase(TestCase):
    """Test cases for _get_tmdb_movie_from_imdb_id function."""

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_success(self, mock_find_class):
        """Test successful TMDB movie retrieval from IMDB ID."""
        # Mock the Find class and its methods
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.return_value = {
            "movie_results": [
                {
                    "id": 603,
                    "title": "The Matrix",
                    "original_title": "The Matrix",
                    "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                    "release_date": "1999-03-30",
                    "popularity": 41.769,
                }
            ]
        }

        result = _get_tmdb_movie_from_imdb_id("tt0133093")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 603)
        self.assertEqual(result["title"], "The Matrix")
        self.assertEqual(result["title_original"], "The Matrix")
        self.assertEqual(result["poster_path"], "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg")
        self.assertEqual(result["release_date"], date(1999, 3, 30))
        self.assertEqual(result["popularity"], 41.769)

        # Verify the mock was called correctly
        mock_find_class.assert_called_once_with("tt0133093")
        mock_find.info.assert_called_once_with(external_source="imdb_id")

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_no_results(self, mock_find_class):
        """Test when TMDB returns no movie results."""
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.return_value = {"movie_results": []}

        result = _get_tmdb_movie_from_imdb_id("tt9999999")

        self.assertIsNone(result)

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_invalid_date(self, mock_find_class):
        """Test handling of invalid release date format."""
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.return_value = {
            "movie_results": [
                {
                    "id": 603,
                    "title": "The Matrix",
                    "original_title": "The Matrix",
                    "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                    "release_date": "invalid-date",
                    "popularity": 41.769,
                }
            ]
        }

        result = _get_tmdb_movie_from_imdb_id("tt0133093")

        self.assertIsNotNone(result)
        self.assertIsNone(result["release_date"])

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_no_release_date(self, mock_find_class):
        """Test handling of missing release date."""
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.return_value = {
            "movie_results": [
                {
                    "id": 603,
                    "title": "The Matrix",
                    "original_title": "The Matrix",
                    "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                    "release_date": None,
                    "popularity": 41.769,
                }
            ]
        }

        result = _get_tmdb_movie_from_imdb_id("tt0133093")

        self.assertIsNotNone(result)
        self.assertIsNone(result["release_date"])

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_exception(self, mock_find_class):
        """Test handling of exceptions during TMDB API call."""
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.side_effect = KeyError("Missing key")

        result = _get_tmdb_movie_from_imdb_id("tt0133093")

        self.assertIsNone(result)

    @patch("moviesapp.views.recommendations.tmdb.Find")
    def test_get_tmdb_movie_from_imdb_id_malformed_response(self, mock_find_class):
        """Test handling of malformed TMDB response."""
        mock_find = Mock()
        mock_find_class.return_value = mock_find
        mock_find.info.return_value = {
            "movie_results": [
                {
                    "id": 603,
                    # Missing required fields to trigger exception
                }
            ]
        }

        result = _get_tmdb_movie_from_imdb_id("tt0133093")

        self.assertIsNone(result)


class RecommendationsViewTestCase(BaseTestCase):
    """Test cases for RecommendationsView."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.url = "/recommendations/"
        self.login()  # Authenticate the test client

        # Create movies for testing user preferences
        self.movie1 = Movie.objects.create(
            tmdb_id=90001, imdb_id="tt9000001", title="Movie 1", title_original="Movie 1 Original"
        )
        self.movie2 = Movie.objects.create(
            tmdb_id=90002, imdb_id="tt9000002", title="Movie 2", title_original="Movie 2 Original"
        )
        self.movie3 = Movie.objects.create(
            tmdb_id=90003, imdb_id="tt9000003", title="Movie 3", title_original="Movie 3 Original"
        )

        # Create records for user preferences testing
        Record.objects.create(user=self.user, movie=self.movie1, list_id=List.WATCHED, rating=5)  # Liked movie
        Record.objects.create(user=self.user, movie=self.movie2, list_id=List.WATCHED, rating=1)  # Disliked movie
        Record.objects.create(user=self.user, movie=self.movie3, list_id=List.WATCHED, rating=0)  # Unrated movie

    def test_parse_year_range_valid(self):
        """Test parsing valid year range."""
        result = RecommendationsView._parse_year_range("2000", "2020")
        self.assertEqual(result, {"start": 2000, "end": 2020})

    def test_parse_year_range_missing_params(self):
        """Test parsing year range with missing parameters."""
        self.assertIsNone(RecommendationsView._parse_year_range("2000", None))
        self.assertIsNone(RecommendationsView._parse_year_range(None, "2020"))
        self.assertIsNone(RecommendationsView._parse_year_range(None, None))

    def test_parse_year_range_invalid_values(self):
        """Test parsing year range with invalid values."""
        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_year_range("invalid", "2020")
        self.assertEqual(str(context.exception), "Invalid year range values")

    @override_settings(AI_MIN_RATING=1, AI_MAX_RATING=10)
    def test_parse_min_rating_valid(self):
        """Test parsing valid minimum rating."""
        result = RecommendationsView._parse_min_rating("5")
        self.assertEqual(result, 5)

    def test_parse_min_rating_none(self):
        """Test parsing None minimum rating."""
        result = RecommendationsView._parse_min_rating(None)
        self.assertIsNone(result)

    @override_settings(AI_MIN_RATING=1, AI_MAX_RATING=10)
    def test_parse_min_rating_out_of_bounds(self):
        """Test parsing minimum rating out of bounds."""
        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_min_rating("11")
        self.assertIn("must be between", str(context.exception))

        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_min_rating("0")
        self.assertIn("must be between", str(context.exception))

    def test_parse_min_rating_invalid_value(self):
        """Test parsing invalid minimum rating value."""
        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_min_rating("invalid")
        self.assertEqual(str(context.exception), "Invalid minimum rating value")

    @override_settings(AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10)
    def test_parse_recommendations_number_valid(self):
        """Test parsing valid recommendations number."""
        result = RecommendationsView._parse_recommendations_number("5")
        self.assertEqual(result, 5)

    def test_parse_recommendations_number_none(self):
        """Test parsing None recommendations number."""
        result = RecommendationsView._parse_recommendations_number(None)
        self.assertIsNone(result)

    @override_settings(AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10)
    def test_parse_recommendations_number_out_of_bounds(self):
        """Test parsing recommendations number out of bounds."""
        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_recommendations_number("11")
        self.assertIn("must be between", str(context.exception))

        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_recommendations_number("0")
        self.assertIn("must be between", str(context.exception))

    def test_parse_recommendations_number_invalid_value(self):
        """Test parsing invalid recommendations number value."""
        with self.assertRaises(ValueError) as context:
            RecommendationsView._parse_recommendations_number("invalid")
        self.assertEqual(str(context.exception), "Invalid recommendations number value")

    def test_get_user_movie_preferences(self):
        """Test getting user movie preferences based on ratings."""
        liked, disliked, unrated = RecommendationsView._get_user_movie_preferences(self.user)

        self.assertEqual(liked, ["Movie 1"])
        self.assertEqual(disliked, ["Movie 2"])
        self.assertEqual(unrated, ["Movie 3"])

    def test_get_user_movie_preferences_no_movies(self):
        """Test getting preferences for user with no movie records."""
        new_user = User.objects.create_user(username="newuser", password="testpass")
        liked, disliked, unrated = RecommendationsView._get_user_movie_preferences(new_user)

        self.assertEqual(liked, [])
        self.assertEqual(disliked, [])
        self.assertEqual(unrated, [])

    @patch("moviesapp.views.recommendations.get_movie_list_result")
    @patch("moviesapp.views.recommendations._get_tmdb_movie_from_imdb_id")
    def test_convert_recommendations_to_movies_success(self, mock_get_tmdb, mock_get_result):
        """Test converting recommendations to movie list results."""
        # Mock TMDB movie data
        mock_tmdb_movie = {
            "id": 603,
            "title": "The Matrix",
            "title_original": "The Matrix",
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "release_date": date(1999, 3, 30),
            "popularity": 41.769,
        }
        mock_get_tmdb.return_value = mock_tmdb_movie

        # Mock movie list result
        mock_movie_result = {
            "id": 603,
            "title": "The Matrix",
            "tmdbLink": "https://www.themoviedb.org/movie/603",
            "releaseDate": "1999-03-30",
            "titleOriginal": "The Matrix",
            "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "poster2x": "https://image.tmdb.org/t/p/w1000/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "isReleased": True,
        }
        mock_get_result.return_value = mock_movie_result

        recommendations = [{"imdb_id": "tt0133093", "reason": "Great sci-fi movie"}]

        result = RecommendationsView._convert_recommendations_to_movies(recommendations, "en")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 603)
        self.assertEqual(result[0]["title"], "The Matrix")

        mock_get_tmdb.assert_called_once_with("tt0133093")
        mock_get_result.assert_called_once_with(mock_tmdb_movie, "en")

    @patch("moviesapp.views.recommendations.capture_exception")
    @patch("moviesapp.views.recommendations._get_tmdb_movie_from_imdb_id")
    def test_convert_recommendations_to_movies_tmdb_failure(self, mock_get_tmdb, mock_capture):
        """Test handling of TMDB API failures during conversion."""
        mock_get_tmdb.return_value = None

        recommendations = [{"imdb_id": "tt0133093", "reason": "Great sci-fi movie"}]

        result = RecommendationsView._convert_recommendations_to_movies(recommendations, "en")

        self.assertEqual(len(result), 0)

    @patch("moviesapp.views.recommendations.capture_exception")
    @patch("moviesapp.views.recommendations._get_tmdb_movie_from_imdb_id")
    def test_convert_recommendations_to_movies_exception(self, mock_get_tmdb, mock_capture):
        """Test handling of exceptions during conversion."""
        mock_get_tmdb.side_effect = ValueError("Test error")

        recommendations = [{"imdb_id": "tt0133093", "reason": "Great sci-fi movie"}]

        result = RecommendationsView._convert_recommendations_to_movies(recommendations, "en")

        self.assertEqual(len(result), 0)
        mock_capture.assert_called_once()

    def test_get_recommendations_unauthenticated(self):
        """Test recommendations endpoint without authentication."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    @patch("moviesapp.views.recommendations.filter_out_movies_user_already_has_in_lists")
    @patch("moviesapp.views.recommendations.RecommendationsView._convert_recommendations_to_movies")
    @patch("moviesapp.views.recommendations.OpenAIClient")
    @override_settings(AI_MAX_RECOMMENDATIONS=10)
    def test_get_recommendations_success(self, mock_client_class, mock_convert, mock_filter):
        """Test successful recommendations request."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_movie_recommendations.return_value = [{"imdb_id": "tt0133093", "reason": "Great sci-fi movie"}]

        # Mock conversion
        mock_movie_result = {
            "id": 603,
            "title": "The Matrix",
            "tmdbLink": "https://www.themoviedb.org/movie/603",
            "releaseDate": "1999-03-30",
            "titleOriginal": "The Matrix",
            "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "poster2x": "https://image.tmdb.org/t/p/w1000/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "isReleased": True,
        }
        mock_convert.return_value = [mock_movie_result]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

        # Verify OpenAI client was called with correct parameters
        mock_client.get_movie_recommendations.assert_called_once()
        args = mock_client.get_movie_recommendations.call_args[0][0]
        self.assertIsInstance(args, RecommendationRequest)
        self.assertEqual(args.liked_movies, ["Movie 1"])
        self.assertEqual(args.disliked_movies, ["Movie 2"])
        self.assertEqual(args.unrated_movies, ["Movie 3"])
        self.assertEqual(args.recommendations_number, 10)

        # Verify filter was called
        mock_filter.assert_called_once_with([mock_movie_result], self.user)

    @patch("moviesapp.views.recommendations.OpenAIClient")
    def test_get_recommendations_with_all_parameters(self, mock_client_class):
        """Test recommendations request with all parameters."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_movie_recommendations.return_value = []

        params = {
            "preferredGenre": "sci-fi",
            "yearStart": "2000",
            "yearEnd": "2020",
            "minRating": "7",
            "recommendationsNumber": "5",
        }

        with override_settings(AI_MIN_RATING=1, AI_MAX_RATING=10, AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10):
            response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Verify OpenAI client was called with correct parameters
        args = mock_client.get_movie_recommendations.call_args[0][0]
        self.assertEqual(args.preferred_genre, "sci-fi")
        self.assertEqual(args.year_range, {"start": 2000, "end": 2020})
        self.assertEqual(args.min_rating, 7)
        self.assertEqual(args.recommendations_number, 5)

    def test_get_recommendations_invalid_year_range(self):
        """Test recommendations with invalid year range."""
        params = {"yearStart": "invalid", "yearEnd": "2020"}

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Invalid year range values")

    @override_settings(AI_MIN_RATING=1, AI_MAX_RATING=10)
    def test_get_recommendations_invalid_min_rating(self):
        """Test recommendations with invalid minimum rating."""
        params = {"minRating": "11"}

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("must be between", data["error"])

    @override_settings(AI_MIN_RECOMMENDATIONS=1, AI_MAX_RECOMMENDATIONS=10)
    def test_get_recommendations_invalid_recommendations_number(self):
        """Test recommendations with invalid recommendations number."""
        params = {"recommendationsNumber": "11"}

        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        data = response.json()
        self.assertIn("error", data)
        self.assertIn("must be between", data["error"])

    @patch("moviesapp.views.recommendations.capture_exception")
    @patch("moviesapp.views.recommendations.OpenAIClient")
    def test_get_recommendations_openai_error(self, mock_client_class, mock_capture):
        """Test handling of OpenAI API errors."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_movie_recommendations.side_effect = OpenAIError("API Error")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Failed to get AI recommendations. Please try again later.")
        mock_capture.assert_called_once()

    @patch("moviesapp.views.recommendations.capture_exception")
    @patch("moviesapp.views.recommendations.OpenAIClient")
    def test_get_recommendations_unexpected_error(self, mock_client_class, mock_capture):
        """Test handling of unexpected errors."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_movie_recommendations.side_effect = AttributeError("Unexpected error")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "An unexpected error occurred")
        mock_capture.assert_called_once()

    def test_recommendations_view_permission_classes(self):
        """Test that the view requires authentication."""
        view = RecommendationsView()
        self.assertIn("IsAuthenticated", [cls.__name__ for cls in view.permission_classes])
