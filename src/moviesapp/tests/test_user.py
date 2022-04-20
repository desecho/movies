from http import HTTPStatus

from django.urls import reverse

from .base import BaseTestCase


class LoginErrorTestCase(BaseTestCase):
    def test_login_error(self):
        url = reverse("login_error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
