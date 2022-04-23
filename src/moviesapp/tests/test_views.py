from http import HTTPStatus

from django.urls import reverse

from .base import BaseTestCase


class AboutTestCase(BaseTestCase):
    def test_about(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class GalleryTestCase(BaseTestCase):
    def test_gallery(self):
        url = reverse("gallery", kwargs={"username": self.USER_USERNAME, "list_name": "watched"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
