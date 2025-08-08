"""Test additional user views."""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from moviesapp.models import User

from ..base import BaseTestCase


class UserCheckEmailAvailabilityViewTestCase(TestCase):
    """Test UserCheckEmailAvailabilityView."""

    def setUp(self):
        """Set up test environment."""
        self.client = APIClient()
        # Create a user with existing email
        self.existing_user = User.objects.create_user(
            username="existing", email="existing@example.com", password="testpass123"
        )

    def test_email_availability_available_email(self):
        """Test email availability check with available email."""
        response = self.client.post(
            "/user/check-email-availability/", {"email": "available@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)  # Email is available

    def test_email_availability_taken_email(self):
        """Test email availability check with taken email."""
        response = self.client.post(
            "/user/check-email-availability/", {"email": "existing@example.com"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)  # Email is not available

    def test_email_availability_missing_email(self):
        """Test email availability check without email parameter."""
        response = self.client.post("/user/check-email-availability/", {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_availability_empty_email(self):
        """Test email availability check with empty email."""
        response = self.client.post("/user/check-email-availability/", {"email": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data)  # Empty email is "available"

    def test_email_availability_get_method_not_allowed(self):
        """Test that GET method is not allowed."""
        response = self.client.get("/user/check-email-availability/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserPreferencesViewTestCase(BaseTestCase):
    """Test UserPreferencesView."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

    def test_get_preferences(self):
        """Test getting user preferences."""
        # Set user preferences
        self.user.hidden = True
        self.user.country = "US"
        self.user.save()

        response = self.client.get("/user/preferences/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["hidden"], True)
        self.assertEqual(response.data["country"], "US")

    def test_get_preferences_default_values(self):
        """Test getting user preferences with default values."""
        response = self.client.get("/user/preferences/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["hidden"], False)  # Default value
        self.assertIsNone(response.data["country"])  # Default value

    def test_put_preferences_valid_data(self):
        """Test updating user preferences with valid data."""
        response = self.client.put("/user/preferences/", {"hidden": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.hidden)

    def test_put_preferences_false_value(self):
        """Test updating user preferences with false value."""
        # Set to true first
        self.user.hidden = True
        self.user.save()

        response = self.client.put("/user/preferences/", {"hidden": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.hidden)

    def test_put_preferences_empty_data(self):
        """Test updating user preferences with empty data."""
        response = self.client.put("/user/preferences/", {}, format="json")

        # With serializer, empty data should be OK since fields are optional
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_preferences_invalid_hidden_value(self):
        """Test updating user preferences with invalid hidden value."""
        response = self.client.put("/user/preferences/", {"hidden": "invalid"}, format="json")

        # Serializer should handle string conversion appropriately
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_preferences_boolean_true(self):
        """Test updating user preferences with boolean true."""
        response = self.client.put("/user/preferences/", {"hidden": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.hidden)

    def test_put_preferences_boolean_false(self):
        """Test updating user preferences with boolean false."""
        response = self.client.put("/user/preferences/", {"hidden": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.hidden)

    def test_preferences_unauthenticated_access(self):
        """Test that unauthenticated users cannot access preferences."""
        self.client.force_authenticate(user=None)

        # GET request
        response = self.client.get("/user/preferences/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # PUT request
        response = self.client.put("/user/preferences/", {"hidden": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_preferences_with_country(self):
        """Test updating user preferences with country."""
        response = self.client.put("/user/preferences/", {"hidden": False, "country": "CA"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user was updated
        self.user.refresh_from_db()
        self.assertFalse(self.user.hidden)
        self.assertEqual(str(self.user.country), "CA")

    def test_put_preferences_with_invalid_country(self):
        """Test updating user preferences with invalid country code."""
        response = self.client.put("/user/preferences/", {"country": "INVALID"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("country", response.data)

    def test_put_preferences_clear_country(self):
        """Test clearing country field by setting to null."""
        # First set a country
        self.user.country = "US"
        self.user.save()

        response = self.client.put("/user/preferences/", {"country": None}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify country was cleared
        self.user.refresh_from_db()
        self.assertIsNone(self.user.country.code if self.user.country else None)

    def test_put_preferences_empty_country_string(self):
        """Test updating with empty string country."""
        response = self.client.put("/user/preferences/", {"country": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify country was cleared/set to None
        self.user.refresh_from_db()
        self.assertIsNone(self.user.country.code if self.user.country else None)

    def test_put_preferences_country_only(self):
        """Test updating only country field."""
        response = self.client.put("/user/preferences/", {"country": "GB"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify country was updated, hidden should remain default
        self.user.refresh_from_db()
        self.assertEqual(str(self.user.country), "GB")
        self.assertFalse(self.user.hidden)  # Should remain default

    def test_put_preferences_partial_update(self):
        """Test partial update of preferences."""
        # Set initial values
        self.user.hidden = True
        self.user.country = "DE"
        self.user.save()

        # Update only hidden field
        response = self.client.put("/user/preferences/", {"hidden": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify hidden was updated but country remained
        self.user.refresh_from_db()
        self.assertFalse(self.user.hidden)
        self.assertEqual(str(self.user.country), "DE")
