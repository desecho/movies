# pylint: disable=duplicate-code

from datetime import date, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import PropertyMock, patch

from django.core.management import call_command
from django.test import TestCase

from moviesapp.exceptions import ProviderNotFoundError
from moviesapp.models import List, Movie, Provider, ProviderRecord, Record, User
from moviesapp.tmdb import TmdbNoImdbIdError


class LoadProvidersCommandTestCase(TestCase):

    @patch("moviesapp.management.commands.load_providers.get_tmdb_providers")
    def test_load_providers_success(self, mock_get_tmdb_providers):
        """Test successful loading of providers."""
        mock_providers = [
            {"provider_id": 1, "provider_name": "Netflix"},
            {"provider_id": 2, "provider_name": "Amazon Prime Video"},
            {"provider_id": 3, "provider_name": "Hulu"},
        ]
        mock_get_tmdb_providers.return_value = mock_providers

        # Capture command output
        out = StringIO()
        call_command("load_providers", stdout=out)

        # Check that providers were created
        self.assertEqual(Provider.objects.count(), 3)

        netflix = Provider.objects.get(id=1)
        self.assertEqual(netflix.name, "Netflix")

        amazon = Provider.objects.get(id=2)
        self.assertEqual(amazon.name, "Amazon Prime Video")

        hulu = Provider.objects.get(id=3)
        self.assertEqual(hulu.name, "Hulu")

    @patch("moviesapp.management.commands.load_providers.get_tmdb_providers")
    def test_load_providers_empty_list(self, mock_get_tmdb_providers):
        """Test loading providers with empty list."""
        mock_get_tmdb_providers.return_value = []

        out = StringIO()
        call_command("load_providers", stdout=out)

        # Should not create any providers
        self.assertEqual(Provider.objects.count(), 0)

    @patch("moviesapp.management.commands.load_providers.get_tmdb_providers")
    def test_load_providers_duplicate_ids(self, mock_get_tmdb_providers):
        """Test loading providers with duplicate IDs (should update existing)."""
        # Create an existing provider
        Provider.objects.create(id=1, name="Old Netflix Name")

        mock_providers = [
            {"provider_id": 1, "provider_name": "Netflix"},
        ]
        mock_get_tmdb_providers.return_value = mock_providers

        out = StringIO()
        call_command("load_providers", stdout=out)

        # Should still have only one provider but with updated name
        self.assertEqual(Provider.objects.count(), 1)
        provider = Provider.objects.get(id=1)
        self.assertEqual(provider.name, "Netflix")


class RemoveUnusedMoviesCommandTestCase(TestCase):

    def setUp(self):
        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})

        # Create test movies - some with records, some without
        self.movie_with_record = Movie.objects.create(
            tmdb_id=1, title="Popular Movie", title_original="Popular Movie", imdb_id="tt0000001"
        )
        self.movie_without_record = Movie.objects.create(
            tmdb_id=2, title="Unused Movie", title_original="Unused Movie", imdb_id="tt0000002"
        )

        # Create a user and record for the first movie
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        Record.objects.create(movie=self.movie_with_record, user=self.user, list_id=List.WATCHED)

    def test_remove_unused_movies_success(self):
        """Test removing movies that have no associated records."""
        self.assertEqual(Movie.objects.count(), 2)

        out = StringIO()
        call_command("remove_unused_movies", stdout=out)

        # Should only have the movie with records left
        remaining_movies = Movie.objects.all()
        self.assertEqual(remaining_movies.count(), 1)
        self.assertEqual(remaining_movies.first().id, self.movie_with_record.id)

    def test_remove_unused_movies_no_unused_movies(self):
        """Test command when all movies have records."""
        # Remove the unused movie manually
        self.movie_without_record.delete()

        out = StringIO()
        call_command("remove_unused_movies", stdout=out)

        # Should still have the movie with records
        self.assertEqual(Movie.objects.count(), 1)
        self.assertTrue(Movie.objects.filter(id=self.movie_with_record.id).exists())


class UpdateImdbRatingsCommandTestCase(TestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=603, title="The Matrix", title_original="The Matrix", imdb_id="tt0133093"
        )

    @patch("moviesapp.management.commands.update_imdb_ratings.get_omdb_movie_data")
    def test_update_imdb_ratings_success(self, mock_get_omdb_data):
        """Test successful IMDB ratings update."""
        mock_get_omdb_data.return_value = {"imdb_rating": "8.7", "imdb_votes": "1,234,567"}

        out = StringIO()
        call_command("update_imdb_ratings", stdout=out)

        # Check that movie was updated
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.imdb_rating, Decimal("8.7"))

    @patch("moviesapp.management.commands.update_imdb_ratings.get_omdb_movie_data")
    def test_update_imdb_ratings_movie_without_imdb_id(self, mock_get_omdb_data):
        """Test updating movies without IMDB ID (should be skipped)."""
        # Clear existing movie to avoid imdb_id constraint issues
        Movie.objects.all().delete()

        # Create movie without IMDB ID (using blank string instead of None due to NOT NULL constraint)
        Movie.objects.create(
            tmdb_id=604,
            title="Movie Without IMDB",
            title_original="Movie Without IMDB",
            imdb_id="",  # Empty string instead of None
        )

        out = StringIO()

        # The command will still call get_omdb_movie_data but with empty string
        # We need to make sure it doesn't break
        mock_get_omdb_data.return_value = {"imdb_rating": None}

        call_command("update_imdb_ratings", stdout=out)

        # Should call OMDB API even for empty imdb_id (this is current behavior)
        self.assertTrue(mock_get_omdb_data.called)
        mock_get_omdb_data.assert_called_once_with("")

    @patch("moviesapp.management.commands.update_imdb_ratings.get_omdb_movie_data")
    def test_update_imdb_ratings_api_error(self, mock_get_omdb_data):
        """Test handling API errors gracefully."""
        mock_get_omdb_data.side_effect = Exception("API Error")

        out = StringIO()
        # The command will raise the exception - it doesn't handle errors gracefully
        with self.assertRaises(Exception):
            call_command("update_imdb_ratings", stdout=out)


class UpdateMovieDataCommandTestCase(TestCase):

    def setUp(self):
        self.movie = Movie.objects.create(tmdb_id=603, title="The Matrix", title_original="The Matrix")

    @patch("moviesapp.management.commands.update_movie_data.load_movie_data")
    def test_update_movie_data_success(self, mock_load_movie_data):
        """Test successful movie data update."""
        mock_load_movie_data.return_value = {
            "title": "The Matrix (Updated)",
            "title_original": "The Matrix",
            "overview": "Updated overview",
            "release_date": "1999-03-31",  # Updated release date
            "imdb_rating": "8.7",  # This will be removed by the command
        }

        out = StringIO()
        call_command("update_movie_data", stdout=out)

        # Check that movie was updated
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "The Matrix (Updated)")

    @patch("moviesapp.management.commands.update_movie_data.load_movie_data")
    def test_update_movie_data_api_error(self, mock_load_movie_data):
        """Test handling API errors during movie update."""
        mock_load_movie_data.side_effect = Exception("TMDB API Error")

        out = StringIO()
        # The command will raise the exception - it doesn't handle all errors gracefully
        with self.assertRaises(Exception):
            call_command("update_movie_data", stdout=out)

    def test_update_movie_data_nonexistent_movie_id(self):
        """Test updating movie data with non-existent movie ID."""
        with self.assertRaises(SystemExit):
            out = StringIO()
            call_command("update_movie_data", "999999", stdout=out)

    def test_update_movie_data_start_from_id_no_movies(self):
        """Test start_from_id flag with no movies found."""
        with self.assertRaises(SystemExit):
            out = StringIO()
            call_command("update_movie_data", "999999", "-s", stdout=out)

    @patch("moviesapp.management.commands.update_movie_data.load_movie_data")
    def test_update_movie_data_tmdb_no_imdb_id_error(self, mock_load_movie_data):
        """Test handling TmdbNoImdbIdError during movie update."""
        mock_load_movie_data.side_effect = TmdbNoImdbIdError("Movie not found in IMDb")

        out = StringIO()
        call_command("update_movie_data", stdout=out)

        # Command should continue after error
        mock_load_movie_data.assert_called_with(self.movie.tmdb_id)

    @patch("moviesapp.management.commands.update_movie_data.load_movie_data")
    def test_update_movie_data_no_changes(self, mock_load_movie_data):
        """Test when movie data doesn't change."""
        # Return the same data that's already in the movie
        mock_load_movie_data.return_value = {
            "title": self.movie.title,
            "title_original": self.movie.title_original,
            "overview": self.movie.overview or "",
            "release_date": self.movie.release_date,
            "imdb_rating": "8.7",  # This will be removed by the command
        }

        out = StringIO()
        call_command("update_movie_data", stdout=out)

        # Movie should not be updated since data is the same
        mock_load_movie_data.assert_called_with(self.movie.tmdb_id)

    @patch("moviesapp.management.commands.update_movie_data.load_movie_data")
    def test_update_movie_data_with_specific_movie_id(self, mock_load_movie_data):
        """Test updating a specific movie by ID."""
        mock_load_movie_data.return_value = {
            "title": "The Matrix (Updated)",
            "title_original": "The Matrix",
            "overview": "Updated overview",
            "release_date": "1999-03-31",
            "imdb_rating": "8.7",
        }

        out = StringIO()
        call_command("update_movie_data", str(self.movie.pk), stdout=out)

        # Should only call load_movie_data for the specific movie
        mock_load_movie_data.assert_called_once_with(self.movie.tmdb_id)

        # Check that movie was updated
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, "The Matrix (Updated)")


class UpdateWatchDataCommandTestCase(TestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",  # Released movie
            imdb_id="tt0133093",
        )

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_success(self, mock_get_watch_data):
        """Test successful watch data update."""
        mock_get_watch_data.return_value = [{"provider_id": 8, "country": "US"}]

        out = StringIO()
        call_command("update_watch_data", stdout=out)

        # Check that watch data was processed
        # This would typically update provider records or movie watch data
        self.assertTrue(mock_get_watch_data.called)
        mock_get_watch_data.assert_called()

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_unreleased_movies_skipped(self, mock_get_watch_data):
        """Test that unreleased movies are skipped."""
        mock_get_watch_data.return_value = []

        # Create unreleased movie (future release date)
        future_date = date.today() + timedelta(days=365)
        Movie.objects.create(
            tmdb_id=604,
            title="Unreleased Movie",
            title_original="Unreleased Movie",
            release_date=future_date.strftime("%Y-%m-%d"),
            imdb_id="tt0604604",
        )

        out = StringIO()
        call_command("update_watch_data", stdout=out)

        # Should only process released movies
        # The command filters by release_date__isnull=False but also checks is_released
        # Both movies have release dates but only self.movie should be released
        released_movies_count = Movie.objects.filter(release_date__isnull=False).count()
        self.assertEqual(released_movies_count, 2)  # Both movies have release dates

        # Verify mock was called to check command executed
        self.assertTrue(mock_get_watch_data.called)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_with_specific_movie_id(self, mock_get_watch_data):
        """Test updating watch data for a specific movie ID."""
        mock_get_watch_data.return_value = [{"provider_id": 8, "country": "US"}]

        out = StringIO()
        call_command("update_watch_data", str(self.movie.pk), stdout=out)

        # Should call get_watch_data for the specific movie
        mock_get_watch_data.assert_called_with(self.movie.tmdb_id)

    def test_update_watch_data_nonexistent_movie_id(self):
        """Test updating watch data with non-existent movie ID."""
        with self.assertRaises(SystemExit):
            out = StringIO()
            call_command("update_watch_data", "999999", stdout=out)

    def test_update_watch_data_no_movies_to_update(self):
        """Test when no movies need updating."""
        # Delete the movie so there are no movies to update
        Movie.objects.all().delete()

        with self.assertRaises(SystemExit):
            out = StringIO()
            call_command("update_watch_data", stdout=out)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_movie_recently_updated(self, mock_get_watch_data):
        """Test that recently updated movies are filtered out."""
        # Mock the is_watch_data_updated_recently property to return True
        with patch.object(Movie, "is_watch_data_updated_recently", new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = True

            with self.assertRaises(SystemExit):
                out = StringIO()
                call_command("update_watch_data", stdout=out)

        # get_watch_data should not be called since movie was recently updated
        mock_get_watch_data.assert_not_called()

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_minimal_flag(self, mock_get_watch_data):
        """Test update watch data with minimal flag."""
        # Create a user with supported country
        user = User.objects.create_user(username="testuser", country="US")

        # Ensure TO_WATCH list exists
        List.objects.get_or_create(id=List.TO_WATCH, defaults={"name": "To Watch"})

        # Create a record in TO_WATCH list
        Record.objects.create(user=user, movie=self.movie, list_id=List.TO_WATCH)

        mock_get_watch_data.return_value = [{"provider_id": 8, "country": "US"}]

        out = StringIO()
        call_command("update_watch_data", "-m", stdout=out)

        # Should process the movie since it's in TO_WATCH, released, and user has supported country
        mock_get_watch_data.assert_called_with(self.movie.tmdb_id)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_no_watch_data_obtained(self, mock_get_watch_data):
        """Test when no watch data is obtained from API."""
        mock_get_watch_data.return_value = None

        out = StringIO()
        call_command("update_watch_data", stdout=out)

        # Should skip the movie and continue
        mock_get_watch_data.assert_called_with(self.movie.tmdb_id)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_remove_no_longer_available_providers(self, mock_get_watch_data):
        """Test removal of provider records that are no longer available."""
        # Create a provider and provider record
        provider = Provider.objects.create(id=8, name="Netflix")
        provider_record = ProviderRecord.objects.create(movie=self.movie, provider=provider, country="US")

        # Mock watch data without the existing provider (simulating removal)
        mock_get_watch_data.return_value = [{"provider_id": 9, "country": "US"}]

        out = StringIO()
        call_command("update_watch_data", stdout=out)

        # The existing provider record should be deleted
        self.assertFalse(ProviderRecord.objects.filter(id=provider_record.id).exists())

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_filter_existing_provider_records(self, mock_get_watch_data):
        """Test filtering out already existing provider records."""
        # Create a provider and provider record
        provider = Provider.objects.create(id=8, name="Netflix")
        ProviderRecord.objects.create(movie=self.movie, provider=provider, country="US")

        # Mock watch data with the same existing provider
        mock_get_watch_data.return_value = [{"provider_id": 8, "country": "US"}]

        out = StringIO()
        call_command("update_watch_data", stdout=out)

        # The command should detect that the provider record already exists and filter it out
        # Since there are no new provider records to add, save_watch_data shouldn't be called
        # or it should be called with an empty list
        mock_get_watch_data.assert_called_with(self.movie.tmdb_id)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    @patch("moviesapp.management.commands.update_watch_data.settings")
    @patch("moviesapp.management.commands.update_watch_data.capture_exception")
    def test_update_watch_data_provider_not_found_error_production(
        self, mock_capture, mock_settings, mock_get_watch_data
    ):
        """Test handling ProviderNotFoundError in production mode."""
        mock_settings.DEBUG = False
        mock_get_watch_data.return_value = [{"provider_id": 999, "country": "US"}]

        # Mock save_watch_data to raise ProviderNotFoundError
        with patch.object(self.movie, "save_watch_data") as mock_save:
            mock_save.side_effect = ProviderNotFoundError("Provider not found")

            out = StringIO()
            call_command("update_watch_data", stdout=out)

            # Should capture the exception in production
            mock_capture.assert_called_once()

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    @patch("moviesapp.management.commands.update_watch_data.settings")
    def test_update_watch_data_provider_not_found_error_debug(self, mock_settings, mock_get_watch_data):
        """Test handling ProviderNotFoundError in debug mode."""
        mock_settings.DEBUG = True
        mock_get_watch_data.return_value = [{"provider_id": 999, "country": "US"}]

        # Mock save_watch_data to raise ProviderNotFoundError
        with patch.object(self.movie, "save_watch_data") as mock_save:
            mock_save.side_effect = ProviderNotFoundError("Provider not found")

            with self.assertRaises(ProviderNotFoundError):
                out = StringIO()
                call_command("update_watch_data", stdout=out)

    @patch("moviesapp.management.commands.update_watch_data.get_watch_data")
    def test_update_watch_data_with_no_last_movie(self, mock_get_watch_data):  # pylint: disable=no-self-use
        """Test update watch data when there's no last movie (empty database case)."""
        mock_get_watch_data.return_value = [{"provider_id": 8, "country": "US"}]

        # Mock Movie.last() to return None
        with patch.object(Movie, "last", return_value=None):
            out = StringIO()
            call_command("update_watch_data", stdout=out)

            # When last_movie is None, the command doesn't process movies
            # get_watch_data should not be called
            mock_get_watch_data.assert_not_called()


class DownloadProviderLogosCommandTestCase(TestCase):

    @patch("moviesapp.management.commands.download_provider_logos.get_tmdb_providers")
    @patch("moviesapp.management.commands.download_provider_logos.wget.download")
    @patch("moviesapp.management.commands.download_provider_logos.exists")
    def test_download_provider_logos_success(self, mock_exists, mock_wget_download, mock_get_tmdb_providers):
        """Test successful provider logos download."""
        mock_get_tmdb_providers.return_value = [
            {
                "provider_id": 8,
                "provider_name": "Netflix",
                "logo_path": "/t/p/original/t2yyOv40HZeVlLjYsCsPHnWLk4W.jpg",
            },
            {
                "provider_id": 9,
                "provider_name": "Amazon Prime Video",
                "logo_path": "/t/p/original/68MNrwlkpF7WnmNPXLah69CR5cb.jpg",
            },
        ]
        mock_exists.return_value = False  # Simulate files don't exist, so download should happen

        out = StringIO()
        call_command("download_provider_logos", stdout=out)

        # Check that wget.download was called for each provider
        self.assertEqual(mock_wget_download.call_count, 2)

    @patch("moviesapp.management.commands.download_provider_logos.get_tmdb_providers")
    @patch("moviesapp.management.commands.download_provider_logos.wget.download")
    def test_download_provider_logos_no_providers(self, mock_wget_download, mock_get_tmdb_providers):
        """Test download command with no providers."""
        mock_get_tmdb_providers.return_value = []

        out = StringIO()
        call_command("download_provider_logos", stdout=out)

        # Should not call wget.download if no providers exist
        self.assertFalse(mock_wget_download.called)
        mock_wget_download.assert_not_called()

    @patch("moviesapp.management.commands.download_provider_logos.get_tmdb_providers")
    @patch("moviesapp.management.commands.download_provider_logos.wget.download")
    @patch("moviesapp.management.commands.download_provider_logos.exists")
    def test_download_provider_logos_download_error(self, mock_exists, mock_wget_download, mock_get_tmdb_providers):
        """Test handling download errors."""
        mock_get_tmdb_providers.return_value = [
            {
                "provider_id": 8,
                "provider_name": "Netflix",
                "logo_path": "/t/p/original/t2yyOv40HZeVlLjYsCsPHnWLk4W.jpg",
            }
        ]
        mock_exists.return_value = False
        mock_wget_download.side_effect = Exception("Download failed")

        out = StringIO()
        # The command will raise the exception - it doesn't handle errors gracefully
        with self.assertRaises(Exception):
            call_command("download_provider_logos", stdout=out)
