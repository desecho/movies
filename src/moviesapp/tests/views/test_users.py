"""Users view tests."""

from django.test import TestCase
from rest_framework.test import APIClient

from moviesapp.models import User


class UsersViewTestCase(TestCase):
    """Users view test case."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test users
        self.visible_user1 = User.objects.create_user(username="visible1", hidden=False)
        self.visible_user2 = User.objects.create_user(username="visible2", hidden=False)
        self.hidden_user = User.objects.create_user(username="hidden", hidden=True)

    def test_get_users_excludes_hidden_users(self):
        """Test that hidden users are excluded from the response."""
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        usernames = response.data

        # Should include visible users but not hidden users
        self.assertIn("visible1", usernames)
        self.assertIn("visible2", usernames)
        self.assertNotIn("hidden", usernames)

    def test_get_users_returns_usernames_only(self):
        """Test that only usernames are returned."""
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        usernames = response.data

        # Should be a list of strings (usernames)
        for username in usernames:
            self.assertIsInstance(username, str)

    def test_get_users_no_authentication_required(self):
        """Test that no authentication is required."""
        # The view has empty permission_classes, so anyone can access it
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)

    def test_get_users_empty_when_all_hidden(self):
        """Test that empty list is returned when all users are hidden."""
        # Hide all existing users
        User.objects.all().update(hidden=True)

        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
