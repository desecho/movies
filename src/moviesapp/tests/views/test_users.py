"""Users view tests."""

from django.core.files.uploadedfile import SimpleUploadedFile
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
        users = response.data
        usernames = [user["username"] for user in users]

        # Should include visible users but not hidden users
        self.assertIn("visible1", usernames)
        self.assertIn("visible2", usernames)
        self.assertNotIn("hidden", usernames)

    def test_get_users_returns_user_objects(self):
        """Test that user objects with username and avatar_url are returned."""
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        users = response.data

        # Should be a list of dictionaries with username and avatar_url
        for user in users:
            self.assertIsInstance(user, dict)
            self.assertIn("username", user)
            self.assertIn("avatar_url", user)
            self.assertIsInstance(user["username"], str)

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

    def test_get_users_with_and_without_avatars(self):
        """Test that users with and without avatars return correct avatar_url values."""
        # Create a test image file
        test_image = SimpleUploadedFile(
            name="test_avatar.jpg", content=b"fake_image_content", content_type="image/jpeg"
        )

        # Create user with avatar
        user_with_avatar = User.objects.create_user(username="with_avatar", hidden=False)
        user_with_avatar.avatar = test_image
        user_with_avatar.save()

        # Create user without avatar (already exists from setUp)
        response = self.client.get("/users/")

        self.assertEqual(response.status_code, 200)
        users = response.data

        # Find users in response
        user_with_avatar_data = next((u for u in users if u["username"] == "with_avatar"), None)
        user_without_avatar_data = next((u for u in users if u["username"] == "visible1"), None)

        # User with avatar should have avatar_url
        self.assertIsNotNone(user_with_avatar_data)
        self.assertIsNotNone(user_with_avatar_data["avatar_url"])
        self.assertIn("avatars/", user_with_avatar_data["avatar_url"])

        # User without avatar should have None avatar_url
        self.assertIsNotNone(user_without_avatar_data)
        self.assertIsNone(user_without_avatar_data["avatar_url"])


class UserAvatarViewTestCase(TestCase):
    """User avatar view test case."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()

        # Create test users
        self.visible_user = User.objects.create_user(username="testuser", hidden=False)
        self.hidden_user = User.objects.create_user(username="hiddenuser", hidden=True)

    def test_get_user_avatar_success(self):
        """Test successful retrieval of user avatar information."""
        response = self.client.get(f"/users/{self.visible_user.username}/avatar/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.visible_user.username)
        self.assertIsNone(response.data["avatar_url"])  # No avatar uploaded

    def test_get_user_avatar_with_avatar(self):
        """Test retrieval of user avatar information when user has avatar."""
        # Create a test image file
        test_image = SimpleUploadedFile(
            name="test_avatar.jpg", content=b"fake_image_content", content_type="image/jpeg"
        )

        self.visible_user.avatar = test_image
        self.visible_user.save()

        response = self.client.get(f"/users/{self.visible_user.username}/avatar/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.visible_user.username)
        self.assertIsNotNone(response.data["avatar_url"])
        self.assertIn("avatars/", response.data["avatar_url"])

    def test_get_user_avatar_hidden_user(self):
        """Test that hidden users return 404."""
        response = self.client.get(f"/users/{self.hidden_user.username}/avatar/")

        self.assertEqual(response.status_code, 404)

    def test_get_user_avatar_nonexistent_user(self):
        """Test that nonexistent users return 404."""
        response = self.client.get("/users/nonexistent/avatar/")

        self.assertEqual(response.status_code, 404)

    def test_get_user_avatar_cache_headers(self):
        """Test that appropriate cache headers are set."""
        response = self.client.get(f"/users/{self.visible_user.username}/avatar/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cache-Control", response)
        self.assertIn("max-age=3600", response["Cache-Control"])
        self.assertIn("ETag", response)

    def test_get_user_avatar_no_authentication_required(self):
        """Test that no authentication is required."""
        response = self.client.get(f"/users/{self.visible_user.username}/avatar/")

        self.assertEqual(response.status_code, 200)
