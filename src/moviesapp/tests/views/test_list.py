from http import HTTPStatus

from django.urls import reverse

from moviesapp.models import Action, List, Movie, Record

from ..base import BaseTestLoginCase


class ListTestCase(BaseTestLoginCase):
    """
    Test case for List views.

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

    def test_add_to_list_bad_request(self):
        movie_id = Movie.objects.get(title="The Avengers").pk
        url = reverse("add_to_list", args=(movie_id,))
        response = self.client.post_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_add_to_list_movie_does_not_exist(self):
        url = reverse("add_to_list", args=(99,))
        response = self.client.post_ajax(url, {"listId": List.WATCHED})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_add_to_list_wrong_list(self):
        url = reverse("add_to_list", args=(1,))
        response = self.client.post_ajax(url, {"listId": 9})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


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

    def test_change_rating_bad_request(self):
        url = reverse("change_rating", args=(1,))
        response = self.client.put_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_change_rating_record_not_found(self):
        url = reverse("change_rating", args=(99,))
        response = self.client.put_ajax(url, {"rating": 3})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


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


class SaveSettingsTestCase(BaseTestLoginCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("save_settings")

    def test_save_settings(self):
        mode = "minimal"
        sort = "rating"
        settings = {"mode": mode, "sort": sort, "recommendation": True}
        response = self.client.put_ajax(self.url, {"settings": settings})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.client.session.get("recommendation"))
        self.assertEqual(self.client.session.get("mode"), mode)
        self.assertEqual(self.client.session.get("sort"), sort)

    def test_save_settings_bad_request(self):
        response = self.client.put_ajax(self.url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class SaveOptionsTestCase(BaseTestLoginCase):
    def test_save_options(self):
        record_id = 1
        url = reverse("save_options", args=(record_id,))
        options = {
            "original": True,
            "extended": True,
            "theatre": True,
            "4k": True,
            "hd": True,
            "fullHd": True,
        }

        response = self.client.put_ajax(url, {"options": options})

        self.assertEqual(response.status_code, HTTPStatus.OK)

        record = Record.objects.get(pk=record_id)
        self.assertTrue(record.watched_original)
        self.assertTrue(record.watched_extended)
        self.assertTrue(record.watched_in_theatre)
        self.assertTrue(record.watched_in_hd)
        self.assertTrue(record.watched_in_full_hd)
        self.assertTrue(record.watched_in_4k)

    def test_save_options_auto_set_hd_to_true_when_full_hd_is_true(self):
        record_id = 1
        url = reverse("save_options", args=(record_id,))
        options = {
            "original": False,
            "extended": False,
            "theatre": False,
            "4k": False,
            "hd": False,
            "fullHd": True,
        }

        response = self.client.put_ajax(url, {"options": options})

        self.assertEqual(response.status_code, HTTPStatus.OK)

        record = Record.objects.get(pk=record_id)
        self.assertTrue(record.watched_in_hd)

    def test_save_options_auto_set_hd_and_full_hd_to_true_when_4k_is_true(self):
        record_id = 1
        url = reverse("save_options", args=(record_id,))
        options = {
            "original": False,
            "extended": False,
            "theatre": False,
            "4k": True,
            "hd": False,
            "fullHd": False,
        }

        response = self.client.put_ajax(url, {"options": options})

        self.assertEqual(response.status_code, HTTPStatus.OK)

        record = Record.objects.get(pk=record_id)
        self.assertTrue(record.watched_in_full_hd)
        self.assertTrue(record.watched_in_hd)

    def test_save_options_bad_request(self):
        url = reverse("save_options", args=(1,))
        response = self.client.put_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_save_options_record_does_not_exist(self):
        url = reverse("save_options", args=(99,))
        response = self.client.put_ajax(url, {"options": {}})
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class SaveCommentTestCase(BaseTestLoginCase):
    def test_save_comment(self):
        record_id = 1
        comment = "comment"
        url = reverse("save_comment", args=(record_id,))
        response = self.client.put_ajax(url, {"comment": comment})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.user.records.filter(pk=record_id, comment=comment).exists())

        # Comment unchanged
        response = self.client.put_ajax(url, {"comment": comment})
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Change comment again
        response = self.client.put_ajax(url, {"comment": "comment2"})
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_save_comment_record_not_found(self):
        url = reverse("save_comment", args=(99,))
        response = self.client.put_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_save_comment_bad_request(self):
        url = reverse("save_comment", args=(1,))
        response = self.client.put_ajax(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
