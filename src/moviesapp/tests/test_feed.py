"""Test feed functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from moviesapp.models import Action, ActionRecord, Follow, List, Movie

User = get_user_model()


class FeedViewTestCase(TestCase):  # pylint: disable=too-many-instance-attributes
    """Test feed view."""

    def setUp(self):
        """Set up test data."""

        self.client = APIClient()

        # Create users
        self.user1 = User.objects.create_user(username="user1", password="testpass123")
        self.user2 = User.objects.create_user(username="user2", password="testpass123")

        # Create lists
        self.watched_list = List.objects.create(id=1, name="Watched", key_name="watched")
        self.to_watch_list = List.objects.create(id=2, name="To Watch", key_name="to_watch")

        # Create actions
        self.added_movie_action = Action.objects.create(id=1, name="Added Movie")
        self.changed_list_action = Action.objects.create(id=2, name="Changed List")
        self.added_rating_action = Action.objects.create(id=3, name="Added Rating")
        self.added_comment_action = Action.objects.create(id=4, name="Added Comment")

        # Create a movie
        self.movie = Movie.objects.create(
            title="Test Movie", title_original="Test Movie", imdb_id="tt1234567", tmdb_id=12345
        )

    def test_anonymous_user_can_access_feed(self):
        """Test that anonymous users can access the feed."""
        response = self.client.get(reverse("feed"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_authenticated_user_with_no_follows_sees_all_activity(self):
        """Test that authenticated user with no follows sees all activity."""

        # Create some activity from user2
        ActionRecord.objects.create(
            user=self.user2, action=self.added_movie_action, movie=self.movie, list=self.watched_list
        )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("feed"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        activity = response.data["results"][0]
        self.assertEqual(activity["action"]["name"], "Added Movie")
        self.assertEqual(activity["list"]["name"], "Watched")

    def test_authenticated_user_with_follows_sees_only_followed_activity(self):
        """Test that authenticated user with follows sees only followed users' activity."""

        # Create a user that user1 doesn't follow
        user3 = User.objects.create_user(username="user3", password="testpass123")

        # Create activity from both user2 and user3
        ActionRecord.objects.create(
            user=self.user2, action=self.added_movie_action, movie=self.movie, list=self.watched_list
        )
        ActionRecord.objects.create(user=user3, action=self.added_rating_action, movie=self.movie, rating=8)

        # User1 follows user2 but not user3
        Follow.objects.create(follower=self.user1, followed=self.user2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("feed"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        # Should only see user2's activity
        activity = response.data["results"][0]
        self.assertEqual(activity["user"]["username"], "user2")
        self.assertEqual(activity["action"]["name"], "Added Movie")

    def test_feed_respects_privacy_settings(self):
        """Test that feed respects user privacy settings."""

        # Create a hidden user
        hidden_user = User.objects.create_user(username="hiddenuser", password="testpass123", hidden=True)

        # Create activity from hidden user
        ActionRecord.objects.create(
            user=hidden_user, action=self.added_movie_action, movie=self.movie, list=self.watched_list
        )

        # Anonymous user should not see hidden user's activity
        response = self.client.get(reverse("feed"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_feed_serialization_includes_all_fields(self):
        """Test that feed serialization includes all necessary fields."""

        ActionRecord.objects.create(
            user=self.user2,
            action=self.changed_list_action,
            movie=self.movie,
            list=self.to_watch_list,
            rating=9,
            comment="Great movie!",
        )

        response = self.client.get(reverse("feed"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        activity = response.data["results"][0]

        # Check all required fields are present
        self.assertIn("id", activity)
        self.assertIn("user", activity)
        self.assertIn("action", activity)
        self.assertIn("movie", activity)
        self.assertIn("date", activity)
        self.assertIn("list", activity)
        self.assertIn("rating", activity)
        self.assertIn("comment", activity)

        # Check user fields
        self.assertEqual(activity["user"]["username"], "user2")
        self.assertIn("avatar_url", activity["user"])

        # Check action fields
        self.assertEqual(activity["action"]["name"], "Changed List")

        # Check movie fields
        self.assertEqual(activity["movie"]["title"], "Test Movie")
        self.assertIn("poster_small", activity["movie"])

        # Check optional fields
        self.assertEqual(activity["list"]["name"], "To Watch")
        self.assertEqual(activity["rating"], 9)
        self.assertEqual(activity["comment"], "Great movie!")
