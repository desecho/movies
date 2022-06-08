from http import HTTPStatus

from django.urls import reverse

from ..base import BaseTestLoginCase


class PeopleTestCase(BaseTestLoginCase):
    def setUp(self):
        super().setUp()
        self.login("fox")

    def test_people(self):
        url = reverse("people")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        soup = self.get_soup(response)
        records = soup.findAll("div", {"class": "person"})
        users = []
        for record in records:
            users.append(record.find("a", {"class": "people-user"}).get_text())
        self.assertListEqual(users, ["admin", "neo"])

    def test_feed_people(self):
        url = reverse("feed", args=("people",))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        soup = self.get_soup(response)
        records = soup.findAll("tr", {"class": "feed-record"})
        self.assertEqual(len(records), 7)
        records_data = []
        for record in records:
            user = record.find("td", {"class": "test-feed-user"}).find("a").find("img").attrs["title"].strip()
            movie = record.find("td", {"class": "test-feed-movie"}).get_text().strip()
            action = record.find("td", {"class": "feed-action-data"}).get_text().strip()
            records_data.append({"user": user, "movie": movie, "action": action})
        self.assertIn({"user": "neo", "movie": "The X Files", "action": "Watched"}, records_data)
        self.assertIn({"user": "neo", "movie": "Pulp Fiction", "action": "To Watch"}, records_data)
        self.assertIn({"user": "neo", "movie": "Dogma", "action": "Watched"}, records_data)
        self.assertIn({"user": "neo", "movie": "The Matrix", "action": "Watched"}, records_data)


class FriendsTestCase(BaseTestLoginCase):
    def test_friends(self):
        url = reverse("friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
