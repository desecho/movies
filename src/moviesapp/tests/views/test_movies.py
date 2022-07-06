from http import HTTPStatus

from django.urls import reverse

from ..base import BaseTestCase


class AboutTestCase(BaseTestCase):
    def test_about(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
