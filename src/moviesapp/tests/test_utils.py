"""Test utils."""

from datetime import date
from unittest.mock import patch

from django.test import TestCase

from moviesapp.utils import is_movie_released, load_movie_data, merge_movie_data


class UtilsTestCase(TestCase):
    """Test utils functions."""

    def setUp(self):
        """Set up test environment."""
        self.sample_tmdb_data = {
            "tmdb_id": 123,
            "imdb_id": "tt1234567",
            "release_date": "2020-01-01",
            "title_original": "Original Title",
            "poster": "/poster.jpg",
            "homepage": "https://example.com",
            "trailers": [],
            "title": "Movie Title",
            "overview": "Movie overview",
            "runtime": "02:00:00",
        }

        self.sample_omdb_data = {
            "writer": "John Writer",
            "director": "Jane Director",
            "actors": "Actor One, Actor Two",
            "genre": "Action, Adventure",
            "country": "USA",
            "imdb_rating": 8.5,
        }

    def test_merge_movie_data(self):
        """Test merge_movie_data function."""
        merged_data = merge_movie_data(self.sample_tmdb_data, self.sample_omdb_data)

        # Check that all TMDB fields are present
        self.assertEqual(merged_data["tmdb_id"], 123)
        self.assertEqual(merged_data["imdb_id"], "tt1234567")
        self.assertEqual(merged_data["title"], "Movie Title")
        self.assertEqual(merged_data["title_original"], "Original Title")
        self.assertEqual(merged_data["overview"], "Movie overview")
        self.assertEqual(merged_data["poster"], "/poster.jpg")
        self.assertEqual(merged_data["homepage"], "https://example.com")
        self.assertEqual(merged_data["runtime"], "02:00:00")
        self.assertEqual(merged_data["release_date"], "2020-01-01")
        self.assertEqual(merged_data["trailers"], [])

        # Check that all OMDb fields are present
        self.assertEqual(merged_data["writer"], "John Writer")
        self.assertEqual(merged_data["director"], "Jane Director")
        self.assertEqual(merged_data["actors"], "Actor One, Actor Two")
        self.assertEqual(merged_data["genre"], "Action, Adventure")
        self.assertEqual(merged_data["country"], "USA")
        self.assertEqual(merged_data["imdb_rating"], 8.5)

    @patch("moviesapp.utils.get_tmdb_movie_data")
    @patch("moviesapp.utils.get_omdb_movie_data")
    def test_load_movie_data(self, mock_get_omdb, mock_get_tmdb):
        """Test load_movie_data function."""
        # Set up mocks
        mock_get_tmdb.return_value = self.sample_tmdb_data
        mock_get_omdb.return_value = self.sample_omdb_data

        # Call function
        result = load_movie_data(123)

        # Verify mocks were called correctly
        mock_get_tmdb.assert_called_once_with(123)
        mock_get_omdb.assert_called_once_with("tt1234567")

        # Verify result contains merged data
        self.assertEqual(result["tmdb_id"], 123)
        self.assertEqual(result["writer"], "John Writer")
        self.assertEqual(result["director"], "Jane Director")

    def test_is_movie_released_with_past_date(self):
        """Test is_movie_released with past date."""
        past_date = date(2020, 1, 1)
        self.assertTrue(is_movie_released(past_date))

    def test_is_movie_released_with_future_date(self):
        """Test is_movie_released with future date."""
        future_date = date(2030, 1, 1)
        self.assertFalse(is_movie_released(future_date))

    def test_is_movie_released_with_today(self):
        """Test is_movie_released with today's date."""
        today = date.today()
        self.assertTrue(is_movie_released(today))

    def test_is_movie_released_with_none(self):
        """Test is_movie_released with None."""
        self.assertFalse(is_movie_released(None))
