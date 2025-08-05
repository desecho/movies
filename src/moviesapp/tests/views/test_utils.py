from datetime import date

from django.http import Http404
from django.test import TestCase

from moviesapp.models import Action, ActionRecord, List, Movie, Record, User
from moviesapp.views.utils import (
    _format_date,
    add_movie_to_list,
    filter_out_movies_user_already_has_in_lists,
    get_anothers_account,
    get_movie_list_result,
)

from ..base import BaseTestCase


class AddMovieToListTestCase(TestCase):

    def setUp(self):
        super().setUp()
        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})
        List.objects.get_or_create(id=List.TO_WATCH, defaults={"name": "To Watch", "key_name": "to-watch"})

        # Create Action objects
        Action.objects.get_or_create(id=Action.ADDED_MOVIE, defaults={"name": "Added Movie"})
        Action.objects.get_or_create(id=Action.CHANGED_LIST, defaults={"name": "Changed List"})
        Action.objects.get_or_create(id=Action.ADDED_RATING, defaults={"name": "Added Rating"})
        Action.objects.get_or_create(id=Action.ADDED_COMMENT, defaults={"name": "Added Comment"})

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.movie = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",
            imdb_id="tt0133093",
        )

    def test_add_movie_to_list_new_record(self):
        """Test adding a movie to a list when user doesn't have any records for it."""
        initial_record_count = self.user.get_records().count()
        initial_action_count = ActionRecord.objects.filter(user=self.user).count()

        add_movie_to_list(self.movie.pk, 1, self.user)

        # Should create a new record
        self.assertEqual(self.user.get_records().count(), initial_record_count + 1)

        record = self.user.get_records().get(movie=self.movie)
        self.assertEqual(record.list_id, 1)
        self.assertEqual(record.movie, self.movie)

        # Should create an action record for ADDED_MOVIE
        self.assertEqual(ActionRecord.objects.filter(user=self.user).count(), initial_action_count + 1)
        action = ActionRecord.objects.filter(user=self.user, movie=self.movie).latest("date")
        self.assertEqual(action.action_id, Action.ADDED_MOVIE)
        self.assertEqual(action.list_id, 1)

    def test_add_movie_to_list_change_existing_list(self):
        """Test changing a movie from one list to another."""
        # Create an existing record
        existing_record = Record.objects.create(movie=self.movie, list_id=1, user=self.user)  # WATCHED
        original_date = existing_record.date

        initial_record_count = self.user.get_records().count()
        initial_action_count = ActionRecord.objects.filter(user=self.user).count()

        # Change to TO_WATCH list
        add_movie_to_list(self.movie.pk, 2, self.user)

        # Should not create a new record, just update existing
        self.assertEqual(self.user.get_records().count(), initial_record_count)

        # Check that record was updated
        existing_record.refresh_from_db()
        self.assertEqual(existing_record.list_id, 2)
        self.assertNotEqual(existing_record.date, original_date)  # Date should be updated

        # Should create an action record for CHANGED_LIST
        self.assertEqual(ActionRecord.objects.filter(user=self.user).count(), initial_action_count + 1)
        action = ActionRecord.objects.filter(user=self.user, movie=self.movie).latest("date")
        self.assertEqual(action.action_id, Action.CHANGED_LIST)
        self.assertEqual(action.list_id, 2)

    def test_add_movie_to_list_same_list_no_action(self):
        """Test adding a movie to the same list it's already in (should not create action)."""
        # Create an existing record
        Record.objects.create(movie=self.movie, list_id=1, user=self.user)  # WATCHED

        initial_action_count = ActionRecord.objects.filter(user=self.user).count()

        # Add to same list
        add_movie_to_list(self.movie.pk, 1, self.user)

        # Should not create any new action records
        self.assertEqual(ActionRecord.objects.filter(user=self.user).count(), initial_action_count)


class GetAnothersAccountTestCase(BaseTestCase):

    def test_get_anothers_account_existing_user(self):
        """Test getting an existing user by username."""
        user = get_anothers_account("neo")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "neo")

    def test_get_anothers_account_nonexistent_user(self):
        """Test getting a non-existent user raises 404."""
        with self.assertRaises(Http404):
            get_anothers_account("nonexistent_user")

    def test_get_anothers_account_none_username(self):
        """Test passing None as username returns None."""
        result = get_anothers_account(None)
        self.assertIsNone(result)

    def test_get_anothers_account_empty_string(self):
        """Test passing empty string as username."""
        # Empty string is falsy, so it should return None like None username
        result = get_anothers_account("")
        self.assertIsNone(result)


class FormatDateTestCase(TestCase):

    def test_format_date_with_valid_date(self):
        """Test formatting a valid date."""
        test_date = date(2020, 1, 15)
        formatted = _format_date(test_date, "en")
        self.assertIsNotNone(formatted)
        self.assertIsInstance(formatted, str)

    def test_format_date_with_none(self):
        """Test formatting None date returns None."""
        result = _format_date(None, "en")
        self.assertIsNone(result)

    def test_format_date_with_different_locales(self):
        """Test formatting dates with different locales."""
        test_date = date(2020, 1, 15)

        en_formatted = _format_date(test_date, "en")
        ru_formatted = _format_date(test_date, "ru")

        self.assertIsNotNone(en_formatted)
        self.assertIsNotNone(ru_formatted)
        # Different locales should produce different formats
        self.assertNotEqual(en_formatted, ru_formatted)


class GetMovieListResultTestCase(TestCase):

    def test_get_movie_list_result_complete_data(self):
        """Test converting TMDB movie data to MovieListResult with complete data."""
        tmdb_movie = {
            "id": 603,
            "title": "The Matrix",
            "title_original": "The Matrix",
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "release_date": date(1999, 3, 30),
        }

        result = get_movie_list_result(tmdb_movie, "en")

        self.assertEqual(result["id"], 603)
        self.assertEqual(result["title"], "The Matrix")
        self.assertEqual(result["titleOriginal"], "The Matrix")
        self.assertIn("tmdbLink", result)
        self.assertIn("poster", result)
        self.assertIn("poster2x", result)
        self.assertIn("releaseDate", result)
        self.assertIn("isReleased", result)

    def test_get_movie_list_result_none_poster(self):
        """Test converting TMDB movie data with None poster."""
        tmdb_movie = {
            "id": 603,
            "title": "The Matrix",
            "title_original": "The Matrix",
            "poster_path": None,
            "release_date": date(1999, 3, 30),
        }

        result = get_movie_list_result(tmdb_movie, "en")

        self.assertEqual(result["id"], 603)
        self.assertIn("poster", result)  # Should handle None gracefully
        self.assertIn("poster2x", result)

    def test_get_movie_list_result_none_release_date(self):
        """Test converting TMDB movie data with None release date."""
        tmdb_movie = {
            "id": 603,
            "title": "The Matrix",
            "title_original": "The Matrix",
            "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "release_date": None,
        }

        result = get_movie_list_result(tmdb_movie, "en")

        self.assertEqual(result["id"], 603)
        self.assertIn("releaseDate", result)
        self.assertIn("isReleased", result)


class FilterOutMoviesUserAlreadyHasInListsTestCase(TestCase):

    def setUp(self):
        super().setUp()
        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})
        List.objects.get_or_create(id=List.TO_WATCH, defaults={"name": "To Watch", "key_name": "to-watch"})

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.movie1 = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",
            imdb_id="tt0133093",
        )
        self.movie2 = Movie.objects.create(
            tmdb_id=604,
            title="The Matrix Reloaded",
            title_original="The Matrix Reloaded",
            release_date="2003-05-15",
            imdb_id="tt0234215",
        )

        # User has movie1 in their records
        Record.objects.create(movie=self.movie1, list_id=List.WATCHED, user=self.user)

    def test_filter_out_movies_user_already_has(self):
        """Test filtering out movies user already has in lists."""
        movies = [
            {"id": 603, "title": "The Matrix"},  # User has this
            {"id": 604, "title": "The Matrix Reloaded"},  # User doesn't have this
            {"id": 605, "title": "Some Other Movie"},  # User doesn't have this
        ]

        filter_out_movies_user_already_has_in_lists(movies, self.user)

        # Should only have movies user doesn't have
        self.assertEqual(len(movies), 2)
        movie_ids = [movie["id"] for movie in movies]
        self.assertNotIn(603, movie_ids)  # Should be filtered out
        self.assertIn(604, movie_ids)
        self.assertIn(605, movie_ids)

    def test_filter_out_movies_empty_list(self):
        """Test filtering with empty movie list."""
        movies = []
        filter_out_movies_user_already_has_in_lists(movies, self.user)
        self.assertEqual(len(movies), 0)

    def test_filter_out_movies_user_has_no_records(self):
        """Test filtering when user has no movie records."""
        # Create a user with no records
        new_user = User.objects.create_user(username="newuser", email="newuser@example.com", password="password")

        movies = [
            {"id": 603, "title": "The Matrix"},
            {"id": 604, "title": "The Matrix Reloaded"},
        ]

        filter_out_movies_user_already_has_in_lists(movies, new_user)

        # Should not filter out any movies
        self.assertEqual(len(movies), 2)

    def test_filter_out_movies_all_movies_filtered(self):
        """Test case where all movies are filtered out."""
        # Add second movie to user's records
        Record.objects.create(movie=self.movie2, list_id=List.TO_WATCH, user=self.user)

        movies = [
            {"id": 603, "title": "The Matrix"},
            {"id": 604, "title": "The Matrix Reloaded"},
        ]

        filter_out_movies_user_already_has_in_lists(movies, self.user)

        # All movies should be filtered out
        self.assertEqual(len(movies), 0)
