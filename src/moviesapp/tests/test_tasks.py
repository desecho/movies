"""Test tasks."""

from unittest.mock import patch

from django.test import override_settings

from moviesapp.exceptions import ProviderNotFoundError
from moviesapp.models import Movie
from moviesapp.tasks import load_and_save_watch_data_task

from .base import BaseTestCase


class TasksTestCase(BaseTestCase):
    """Test Celery tasks."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.movie = Movie.objects.create(
            tmdb_id=123, title="Test Movie", title_original="Test Movie Original", release_date="2020-01-01"
        )

    @patch("moviesapp.tasks.get_watch_data")
    @patch("moviesapp.models.Movie.save_watch_data")
    def test_load_and_save_watch_data_task_success(self, mock_save_watch_data, mock_get_watch_data):
        """Test successful execution of load_and_save_watch_data_task."""
        # Set up mocks
        mock_watch_data = [{"provider_id": 1, "country": "US"}]
        mock_get_watch_data.return_value = mock_watch_data
        mock_save_watch_data.return_value = None

        # Call task
        load_and_save_watch_data_task(self.movie.pk)

        # Verify calls
        mock_get_watch_data.assert_called_once_with(self.movie.tmdb_id)
        mock_save_watch_data.assert_called_once_with(mock_watch_data)

    @patch("moviesapp.tasks.get_watch_data")
    @patch("moviesapp.models.Movie.save_watch_data")
    @override_settings(DEBUG=True)
    def test_load_and_save_watch_data_task_provider_not_found_debug(self, mock_save_watch_data, mock_get_watch_data):
        """Test task when ProviderNotFoundError is raised in DEBUG mode."""
        # Set up mocks
        mock_watch_data = [{"provider_id": 999, "country": "US"}]
        mock_get_watch_data.return_value = mock_watch_data
        mock_save_watch_data.side_effect = ProviderNotFoundError("Provider not found")

        # Should raise exception in DEBUG mode
        with self.assertRaises(ProviderNotFoundError):
            load_and_save_watch_data_task(self.movie.pk)

    @patch("moviesapp.tasks.get_watch_data")
    @patch("moviesapp.models.Movie.save_watch_data")
    @patch("moviesapp.tasks.capture_exception")
    @override_settings(DEBUG=False)
    def test_load_and_save_watch_data_task_provider_not_found_production(
        self, mock_capture_exception, mock_save_watch_data, mock_get_watch_data
    ):
        """Test task when ProviderNotFoundError is raised in production mode."""
        # Set up mocks
        mock_watch_data = [{"provider_id": 999, "country": "US"}]
        mock_get_watch_data.return_value = mock_watch_data
        exception = ProviderNotFoundError("Provider not found")
        mock_save_watch_data.side_effect = exception

        # Should not raise exception in production mode
        load_and_save_watch_data_task(self.movie.pk)

        # Should capture exception
        mock_capture_exception.assert_called_once_with(exception)

    @patch("moviesapp.tasks.get_watch_data")
    def test_load_and_save_watch_data_task_movie_not_found(self, mock_get_watch_data):
        """Test task when movie doesn't exist."""
        nonexistent_id = 99999

        with self.assertRaises(Movie.DoesNotExist):
            load_and_save_watch_data_task(nonexistent_id)

        # get_watch_data should not be called if movie doesn't exist
        mock_get_watch_data.assert_not_called()
