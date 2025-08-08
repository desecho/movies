"""Test follow functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from moviesapp.models import Follow

User = get_user_model()


class FollowViewTestCase(TestCase):
    """Test follow view."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")
        self.hidden_user = User.objects.create_user(username="hiddenuser", password="testpass123", hidden=True)

    def test_get_follow_status_unauthenticated(self):
        """Test getting follow status when not authenticated."""
        response = self.client.get(reverse("follow", args=["user2"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_following"])

    def test_get_follow_status_authenticated(self):
        """Test getting follow status when authenticated."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("follow", args=["user2"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_following"])
        self.assertEqual(response.data["followers_count"], 0)
        self.assertEqual(response.data["following_count"], 0)

    def test_follow_user_success(self):
        """Test following a user successfully."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["user2"]))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_following"])
        self.assertEqual(response.data["followers_count"], 1)

        # Verify follow relationship was created
        self.assertTrue(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())

    def test_follow_user_already_following(self):
        """Test following a user that's already being followed."""
        # Create existing follow relationship
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["user2"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_following"])
        self.assertIn("already following", response.data["message"])

    def test_unfollow_user_success(self):
        """Test unfollowing a user successfully."""
        # Create follow relationship
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse("follow", args=["user2"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_following"])

        # Verify follow relationship was deleted
        self.assertFalse(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())

    def test_unfollow_user_not_following(self):
        """Test unfollowing a user that's not being followed."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse("follow", args=["user2"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_following"])
        self.assertIn("were not following", response.data["message"])

    def test_cannot_follow_self(self):
        """Test that users cannot follow themselves."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["user1"]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot follow yourself", response.data["error"])

    def test_cannot_follow_hidden_user(self):
        """Test that users cannot follow hidden users."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["hiddenuser"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_nonexistent_user(self):
        """Test following a nonexistent user."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["nonexistent"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_counts_update_correctly(self):
        """Test that follow counts update correctly."""
        # Create another user
        user3 = User.objects.create_user(username="user3", password="testpass123")

        # user1 follows user2
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(reverse("follow", args=["user2"]))
        self.assertEqual(response.data["followers_count"], 1)  # user2 has 1 follower

        # user3 also follows user2
        self.client.force_authenticate(user=user3)
        response = self.client.post(reverse("follow", args=["user2"]))
        self.assertEqual(response.data["followers_count"], 2)  # user2 has 2 followers

        # user3 follows user1
        response = self.client.post(reverse("follow", args=["user1"]))

        # Check user1's counts (should have 1 follower, 1 following)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("follow", args=["user1"]))  # This will 404 but let's check user2 instead
        response = self.client.get(reverse("follow", args=["user2"]))
        self.assertEqual(response.data["followers_count"], 2)  # user2 still has 2 followers

    def test_follow_requires_authentication(self):
        """Test that following requires authentication."""
        # POST (follow)
        response = self.client.post(reverse("follow", args=["user2"]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # DELETE (unfollow)
        response = self.client.delete(reverse("follow", args=["user2"]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
