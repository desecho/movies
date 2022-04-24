from http import HTTPStatus

from django.urls import reverse

from moviesapp.models import Action, List, Movie

from ..base import BaseTestLoginCase


class ListTestCase(BaseTestLoginCase):
    """
    Dumpdata commands:
    manage dumpdata moviesapp.Movie --indent 2 > moviesapp/fixtures/movies.json
    manage dumpdata moviesapp.Record --indent 2 > moviesapp/fixtures/records.json
    manage dumpdata moviesapp.ActionRecord --indent 2 > moviesapp/fixtures/action_records.json

    User actions in fixtures:
    neo:
        - Added "The Matrix" to his "Watched" list
        - Added "Dogma" to his "Watched" list
        - Added "Pulp Fiction" to his "To watch" list
    fox:
        - Added "Avengers" to his "Watched" list
    """

    def test_list_watched(self):
        url = reverse("list", args=("watched",))
        response = self.client.get(url)
        records = response.context_data["records"]
        titles = [record.movie.title for record in records]
        self.assertListEqual(titles, ["The X Files", "Dogma", "The Matrix"])
        soup = self.get_soup(response)
        counters = soup.find("div", id="movie-count").findAll("span")
        conter_watched = counters[0].get_text().strip()
        conter_to_watch = counters[1].get_text().strip()
        self.assertEqual(conter_watched, "3")
        self.assertEqual(conter_to_watch, "1")

    def test_list_search(self):
        url = reverse("list", args=("watched",))
        response = self.client.get(url, {"query": "Matrix"})
        soup = self.get_soup(response)
        titles = soup.findAll("div", {"class": "title"})
        self.assertEqual(len(titles), 1)
        title = titles[0].span.attrs["title"]
        self.assertEqual(title, "The Matrix")


class AddToListTestCase(BaseTestLoginCase):
    def test_add_to_list(self):
        LIST_ID = List.WATCHED
        movie_id = Movie.objects.get(title="The Avengers").pk
        url = reverse("add_to_list", args=(movie_id,))
        response = self.client.post_ajax(url, {"listId": LIST_ID})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user.records.filter(list_id=LIST_ID, movie_id=movie_id).exists())

    def test_add_to_list_fails(self):
        movie_id = Movie.objects.get(title="The Avengers").pk
        url = reverse("add_to_list", args=(movie_id,))
        response = self.client.post_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class ChangeRatingTestCase(BaseTestLoginCase):
    def test_change_rating(self):
        record_id = 1
        rating = 3
        url = reverse("change_rating", args=(record_id,))
        response = self.client.put_ajax(url, {"rating": rating})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user.records.filter(pk=record_id, rating=rating).exists())
        # Rating not changed
        response = self.client.put_ajax(url, {"rating": rating})
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_change_rating_action(self):
        record_id = 3
        rating = 3
        url = reverse("change_rating", args=(record_id,))
        response = self.client.put_ajax(url, {"rating": rating})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user.actions.filter(action_id=Action.ADDED_RATING, rating=rating).exists())

    def test_change_rating_fails(self):
        url = reverse("change_rating", args=(1,))
        response = self.client.put_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class RemoveRecordTestCase(BaseTestLoginCase):
    def test_remove_record(self):
        record_id = 1
        url = reverse("remove_record", args=(record_id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(self.user.records.filter(pk=record_id).exists())

    def test_remove_record_does_not_exist(self):
        record_id = 99
        url = reverse("remove_record", args=(record_id,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
