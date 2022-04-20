import pytest
import tmdbsimple
from django.urls import reverse
from flexmock import flexmock

from .base import BaseTestCase


class SearchMoviesAnonymousTestCase(BaseTestCase):
    response_type_movie = None
    response_type_movie_popular = None
    response_type_movie_sorted = None
    response_type_actor = None
    response_type_director = None

    def test_search_view(self):
        url = reverse("search")
        self.client.get(url)

    @pytest.fixture(autouse=True)
    def run_requests(self, mocker, client):
        def get_response(type_, options):
            if type_ == "movie":
                query = "Matrix"
                mockfile = "search_movies-movie-tmdb.json"
            elif type_ == "actor":
                mockfile_movies = "search_movies-cast-tmdb.json"
                mockfile_person = "search_movies-person-actor-tmdb.json"
                query = "David Duchovny"
            elif type_ == "director":
                mockfile_movies = "search_movies-crew-tmdb.json"
                mockfile_person = "search_movies-person-director-tmdb.json"
                query = "Kevin Smith"

            params = {
                "options": options,
                "query": query,
                "type": type_,
            }
            if type_ == "movie":
                tmdbsimple_movie = mocker.patch("tmdbsimple.search.Search.movie")
                tmdbsimple_movie.return_value = self.load_json(mockfile)
            else:
                tmdbsimple_person = mocker.patch("tmdbsimple.search.Search.person")
                tmdbsimple_person.return_value = self.load_json(mockfile_person)

                if type_ == "actor":
                    people_mock = flexmock()
                    people_mock.cast = self.load_json(mockfile_movies)
                    people_mock.combined_credits = lambda: None
                    flexmock(tmdbsimple.people.People).new_instances(people_mock)
                if type_ == "director":
                    people_mock = flexmock()
                    people_mock.crew = self.load_json(mockfile_movies)
                    people_mock.combined_credits = lambda: None
                    flexmock(tmdbsimple.people.People).new_instances(people_mock)

                # Don't send API requests which don't make sense.
                tmdbsimple_get = mocker.patch("tmdbsimple.base.TMDB._GET")
                tmdbsimple_get.return_value = None

            # We can't use self.client here because mocker breaks it.
            response = client.get(url, params)
            return response.json()

        url = reverse("search_movie")
        self.response_type_movie = get_response("movie", '{"popularOnly":false,"sortByDate":false}')
        self.response_type_movie_popular = get_response("movie", '{"popularOnly":true,"sortByDate":false}')
        self.response_type_movie_sorted = get_response("movie", '{"popularOnly":false,"sortByDate":true}')
        self.response_type_actor = get_response("actor", '{"popularOnly":false,"sortByDate":false}')
        self.response_type_director = get_response("director", '{"popularOnly":false,"sortByDate":false}')

    def test_type_movie(self):
        self.assertEqual(self.response_type_movie["status"], "success")
        self.assertEqual(self.response_type_movie["movies"], self.load_json("search_movies-type_movie.json"))

    def test_type_movie_popular(self):
        self.assertEqual(self.response_type_movie_popular["status"], "success")
        self.assertEqual(
            self.response_type_movie_popular["movies"], self.load_json("search_movies-type_movie-popular.json")
        )

    def test_type_movie_sorted(self):
        self.assertEqual(self.response_type_movie_sorted["status"], "success")
        self.assertEqual(
            self.response_type_movie_sorted["movies"], self.load_json("search_movies-type_movie-sorted.json")
        )

    def test_type_actor(self):
        self.assertEqual(self.response_type_actor["status"], "success")
        self.assertEqual(self.response_type_actor["movies"], self.load_json("search_movies-type_actor.json"))

    def test_type_director(self):
        self.assertEqual(self.response_type_director["status"], "success")
        self.assertEqual(self.response_type_director["movies"], self.load_json("search_movies-type_director.json"))


# class AddMoviesTestCase(BaseTestLoginCase):
#     def test_add_movie(self):
#         list_id = List.WATCHED
#         movie_id = 603
#         url = reverse('add_to_list_from_db')
#         params = {
#             'movieId': movie_id,
#             'listId': list_id,
#         }
#         # TODO Mock tmdbsimple
#         response = self.client.post(url, params)
#         assert False
#         response = self.get_json(response)
#         self.assertEqual(response['status'], 'success')
#         record = self.user.get_records().first()
#         self.assertEqual(record.list.pk, list_id)
#         movie = record.movie
#         self.assertEqual(json.loads(self.dump_instance(movie)), self.load_json('add_movies_matrix.json'))
#         action = self.user.actions.first()
#         self.assertEqual(movie, action.movie)
#         self.assertEqual(Action.ADDED_MOVIE, action.action_id)
#         self.assertEqual(list_id, action.list_id)
