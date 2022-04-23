from http import HTTPStatus

from django.urls import reverse

from .base import BaseTestCase, BaseTestLoginCase


class LoginErrorTestCase(BaseTestCase):
    def test_login_error(self):
        url = reverse("login_error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PreferencesTestCase(BaseTestLoginCase):
    def test_preferences(self):
        url = reverse("preferences")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class LogoutTestCase(BaseTestLoginCase):
    def test_logout(self):
        url = reverse("logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.is_authenticated)
