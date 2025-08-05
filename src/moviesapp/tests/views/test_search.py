# pylint: disable=duplicate-code

from datetime import date
from http import HTTPStatus
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from moviesapp.models import Action, List, Movie, User
from moviesapp.tmdb import TmdbInvalidSearchTypeError, TmdbNoImdbIdError
from moviesapp.views.search import AddToListFromDbView, SearchMovieView

from ..base import BaseTestCase


class SearchMovieViewTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.url = "/search/"

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_success(self, mock_search_movies):
        mock_search_movies.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            }
        ]

        params = {
            "query": "matrix",
            "options": '{"sortByDate": false, "popularOnly": false}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 603)
        self.assertEqual(data[0]["title"], "The Matrix")

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_popular_only_filter(self, mock_search_movies):
        mock_search_movies.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 0.5,  # Below MIN_POPULARITY threshold
            },
            {
                "id": 604,
                "title": "The Matrix Reloaded",
                "title_original": "The Matrix Reloaded",
                "poster_path": "/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
                "release_date": date(2003, 5, 15),
                "popularity": 41.769,  # Above MIN_POPULARITY threshold
            },
        ]

        params = {
            "query": "matrix",
            "options": '{"sortByDate": false, "popularOnly": true}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 604)

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_sort_by_date(self, mock_search_movies):
        mock_search_movies.return_value = [
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

        params = {
            "query": "matrix",
            "options": '{"sortByDate": true, "popularOnly": false}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        # Should be sorted by date descending (newest first)
        self.assertEqual(data[0]["id"], 604)  # 2003 movie first
        self.assertEqual(data[1]["id"], 603)  # 1999 movie second

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_authenticated_user_filters_existing_movies(self, mock_search_movies):
        self.login()
        mock_search_movies.return_value = [
            {
                "id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
                "release_date": date(1999, 3, 30),
                "popularity": 41.769,
            }
        ]

        params = {
            "query": "matrix",
            "options": '{"sortByDate": false, "popularOnly": false}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        # The movie should be filtered out if user already has it in lists

    def test_search_movie_missing_query_parameter(self):
        params = {
            "options": '{"sortByDate": false, "popularOnly": false}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_search_movie_missing_options_parameter(self):
        params = {
            "query": "matrix",
            "type": "movie",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_search_movie_missing_type_parameter(self):
        params = {
            "query": "matrix",
            "options": '{"sortByDate": false, "popularOnly": false}',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_invalid_search_type(self, mock_search_movies):
        mock_search_movies.side_effect = TmdbInvalidSearchTypeError()

        params = {
            "query": "matrix",
            "options": '{"sortByDate": false, "popularOnly": false}',
            "type": "invalid_type",
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @patch("moviesapp.views.search.search_movies")
    def test_search_movie_max_results_limit(self, mock_search_movies):
        # Create more results than MAX_RESULTS
        mock_results = []
        for i in range(settings.MAX_RESULTS + 10):
            mock_results.append(
                {
                    "id": i + 1,
                    "title": f"Movie {i + 1}",
                    "title_original": f"Movie {i + 1}",
                    "poster_path": "/poster.jpg",
                    "release_date": date(2020, 1, 1),
                    "popularity": 10.0,
                }
            )
        mock_search_movies.return_value = mock_results

        params = {
            "query": "movie",
            "options": '{"sortByDate": false, "popularOnly": false}',
            "type": "movie",
        }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), settings.MAX_RESULTS)

    def test_is_popular_movie_static_method(self):
        # Test the static method through the class rather than instance
        self.assertTrue(SearchMovieView._is_popular_movie(2.0))  # pylint: disable=protected-access
        self.assertFalse(SearchMovieView._is_popular_movie(1.0))  # pylint: disable=protected-access
        self.assertTrue(SearchMovieView._is_popular_movie(settings.MIN_POPULARITY))  # pylint: disable=protected-access

    def test_sort_by_date_static_method(self):
        movies = [
            {"id": 1, "release_date": date(2020, 1, 1)},
            {"id": 2, "release_date": None},
            {"id": 3, "release_date": date(2022, 1, 1)},
        ]
        sorted_movies = SearchMovieView._sort_by_date(movies)  # pylint: disable=protected-access

        # Movies with dates should come first, sorted by date descending
        # Movies without dates should come last
        self.assertEqual(sorted_movies[0]["id"], 3)  # 2022
        self.assertEqual(sorted_movies[1]["id"], 1)  # 2020
        self.assertEqual(sorted_movies[2]["id"], 2)  # No date


class AddToListFromDbViewTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.url = "/add-to-list-from-db/"
        # Create List objects
        List.objects.get_or_create(id=List.WATCHED, defaults={"name": "Watched", "key_name": "watched"})
        List.objects.get_or_create(id=List.TO_WATCH, defaults={"name": "To Watch", "key_name": "to-watch"})

        # Create Action objects
        Action.objects.get_or_create(id=Action.ADDED_MOVIE, defaults={"name": "Added Movie"})
        Action.objects.get_or_create(id=Action.CHANGED_LIST, defaults={"name": "Changed List"})
        Action.objects.get_or_create(id=Action.ADDED_RATING, defaults={"name": "Added Rating"})
        Action.objects.get_or_create(id=Action.ADDED_COMMENT, defaults={"name": "Added Comment"})

        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password")
        self.client.force_login(self.user)

    @patch("moviesapp.views.search.load_movie_data")
    @patch("moviesapp.views.search.load_and_save_watch_data_task")
    def test_add_new_movie_to_list_success(self, mock_task, mock_load_movie_data):
        mock_load_movie_data.return_value = {
            "tmdb_id": 603,
            "title": "The Matrix",
            "title_original": "The Matrix",
            "release_date": date(1999, 3, 30),
        }

        data = {
            "movieId": 603,
            "listId": List.WATCHED,
        }
        response = self.client.post(self.url, data, content_type="application/json")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that movie was created
        movie = Movie.objects.get(tmdb_id=603)
        self.assertEqual(movie.title, "The Matrix")

        # Check that task was triggered for released movie
        mock_task.delay.assert_called_once_with(movie.pk)

    @patch("moviesapp.views.search.load_movie_data")
    def test_add_existing_movie_to_list(self, mock_load_movie_data):
        # Create a movie first
        movie = Movie.objects.create(
            tmdb_id=603,
            title="The Matrix",
            title_original="The Matrix",
            release_date="1999-03-30",
            imdb_id="tt0133093",
        )

        data = {
            "movieId": 603,
            "listId": List.TO_WATCH,
        }
        response = self.client.post(self.url, data, content_type="application/json")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # load_movie_data should not be called since movie exists
        mock_load_movie_data.assert_not_called()

        # Check that record was created
        record = self.user.get_records().filter(movie=movie).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.list_id, List.TO_WATCH)

    def test_add_to_list_missing_movie_id(self):
        data = {
            "listId": List.WATCHED,
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_missing_list_id(self):
        data = {
            "movieId": 603,
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_invalid_movie_id(self):
        data = {
            "movieId": "not_a_number",
            "listId": List.WATCHED,
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_invalid_list_id(self):
        data = {
            "movieId": 603,
            "listId": "not_a_number",
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_invalid_list_id_value(self):
        data = {
            "movieId": 603,
            "listId": 999,  # Invalid list ID
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch("moviesapp.views.search.load_movie_data")
    def test_add_to_list_tmdb_no_imdb_id_error(self, mock_load_movie_data):
        mock_load_movie_data.side_effect = TmdbNoImdbIdError()

        data = {
            "movieId": 603,
            "listId": List.WATCHED,
        }
        response = self.client.post(self.url, data, content_type="application/json")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_data = response.json()
        self.assertEqual(response_data["status"], "not_found")

    def test_add_to_list_unauthenticated(self):
        self.client.logout()
        data = {
            "movieId": 603,
            "listId": List.WATCHED,
        }
        response = self.client.post(self.url, data, content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_add_movie_to_db_static_method(self):
        view = AddToListFromDbView()

        with (
            patch("moviesapp.views.search.load_movie_data") as mock_load_movie_data,
            patch("moviesapp.views.search.load_and_save_watch_data_task") as mock_task,
        ):
            mock_load_movie_data.return_value = {
                "tmdb_id": 603,
                "title": "The Matrix",
                "title_original": "The Matrix",
                "release_date": date(1999, 3, 30),
            }

            movie_id = view.add_movie_to_db(603)

            movie = Movie.objects.get(pk=movie_id)
            self.assertEqual(movie.tmdb_id, 603)
            self.assertEqual(movie.title, "The Matrix")
            mock_task.delay.assert_called_once_with(movie.pk)

    def test_get_movie_id_static_method(self):
        # Test with non-existent movie
        movie_id = AddToListFromDbView._get_movie_id(999)  # pylint: disable=protected-access
        self.assertIsNone(movie_id)

        # Test with existing movie
        movie = Movie.objects.create(tmdb_id=603, title="The Matrix", imdb_id="tt0133093")
        movie_id = AddToListFromDbView._get_movie_id(603)  # pylint: disable=protected-access
        self.assertEqual(movie_id, movie.pk)
