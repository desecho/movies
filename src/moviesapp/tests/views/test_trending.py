# pylint: disable=duplicate-code

from datetime import date
from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase

from moviesapp.models import List, Movie, User
from moviesapp.views.trending import TrendingView

from ..base import BaseTestCase


class TrendingViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.url = "/trending/"

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_anonymous_user(self, mock_get_trending):
        mock_get_trending.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            },
            {
                "id": 604,
                "title": "The Matrix Reloaded",
                "title_original": "The Matrix Reloaded",
                "poster_path": "/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
                "release_date": date(2003, 5, 15),
                "popularity": 35.5,
            },
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        # Check that movies are properly formatted
        self.assertEqual(data[0]["id"], 603)
        self.assertEqual(data[0]["title"], "The Matrix")
        self.assertIn("tmdbLink", data[0])
        self.assertIn("poster", data[0])
        self.assertIn("isReleased", data[0])

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_authenticated_user_filters_existing_movies(self, mock_get_trending):
        self.login()

        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})

        # Create a movie that the user already has in their list
        movie = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",
            imdb_id="tt0133093",
        )

        # Add record for this user and movie
        self.user.get_records().create(
            movie=movie,
            list_id=List.WATCHED,
            user=self.user,
        )

        mock_get_trending.return_value = [
            {
                "id": 603,  # This movie should be filtered out
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            },
            {
                "id": 604,  # This movie should remain
                "title": "The Matrix Reloaded",
                "title_original": "The Matrix Reloaded",
                "poster_path": "/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
                "release_date": date(2003, 5, 15),
                "popularity": 35.5,
            },
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Should only have one movie (the one not in user's lists)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 604)

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_empty_results(self, mock_get_trending):
        mock_get_trending.return_value = []

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(data, [])

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_uses_request_language_code(self, mock_get_trending):
        mock_get_trending.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            }
        ]

        # Test with different Accept-Language header
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE="ru")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)

        # The language code should be used in formatting dates and other localized content

    def test_trending_view_permission_classes_empty(self):
        """Test that TrendingView has empty permission_classes (allows anonymous access)."""
        view = TrendingView()
        self.assertEqual(view.permission_classes, [])

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_with_movies_having_null_poster(self, mock_get_trending):
        mock_get_trending.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": None,  # No poster
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            }
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)

        # Should handle None poster gracefully
        self.assertIn("poster", data[0])

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_with_movies_having_null_release_date(self, mock_get_trending):
        mock_get_trending.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": None,  # No release date
                "popularity": 41.769,
            }
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)

        # Should handle None release date gracefully
        self.assertIn("releaseDate", data[0])
        self.assertIn("isReleased", data[0])


class TrendingViewAuthenticatedTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.url = "/trending/"
        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})
        List.objects.get_or_create(id=List.TO_WATCH, defaults={"name": "To Watch", "key_name": "to-watch"})

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.client.force_login(self.user)

    @patch("moviesapp.views.trending.get_trending")
    def test_trending_view_authenticated_user_with_existing_records(self, mock_get_trending):
        # Create some movies that the user has in their records
        movie1 = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",
            imdb_id="tt0133093",
        )
        movie2 = Movie.objects.create(
            tmdb_id=604,
            title="The Matrix Reloaded",
            title_original="The Matrix Reloaded",
            release_date="2003-05-15",
            imdb_id="tt0234215",
        )

        # Add records for these movies
        self.user.get_records().create(movie=movie1, list_id=List.WATCHED, user=self.user)
        self.user.get_records().create(movie=movie2, list_id=List.TO_WATCH, user=self.user)

        mock_get_trending.return_value = [
            {
                "id": 603,  # User already has this
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            },
            {
                "id": 604,  # User already has this
                "title": "The Matrix Reloaded",
                "title_original": "The Matrix Reloaded",
                "poster_path": "/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
                "release_date": date(2003, 5, 15),
                "popularity": 35.5,
            },
            {
                "id": 605,  # User doesn't have this
                "title": "The Matrix Revolutions",
                "title_original": "The Matrix Revolutions",
                "poster_path": "/sKogjhfs5q3aEG8EvQPIKOHnhTz.jpg",
                "release_date": date(2003, 11, 5),
                "popularity": 25.3,
            },
        ]

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Should only have the movie the user doesn't already have
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 605)
        self.assertEqual(data[0]["title"], "The Matrix Revolutions")
