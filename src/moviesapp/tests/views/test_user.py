from http import HTTPStatus

from django.urls import reverse

from moviesapp.models import User

from ..base import BaseTestCase, BaseTestLoginCase


class LoginErrorTestCase(BaseTestCase):
    def test_login_error(self):
        url = reverse("login_error")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PreferencesTestCase(BaseTestLoginCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("preferences")

    def test_preferences(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_save_preferences(self):
        language = "ru"
        first_name = "Ivan"
        last_name = "Petrov"
        username = "ivan"

        response = self.client.post(
            self.url,
            {
                "language": language,
                "only_for_friends": "1",
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.language, language)
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.only_for_friends)


class LogoutTestCase(BaseTestLoginCase):
    def test_logout(self):
        url = reverse("logout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.is_authenticated)


class AccountDeletedTestCase(BaseTestLoginCase):
    def test_account_deleted(self):
        url = reverse("account_deleted")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class AccountDeleteTestCase(BaseTestLoginCase):
    def test_account_delete(self):
        url = reverse("delete_account")
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
