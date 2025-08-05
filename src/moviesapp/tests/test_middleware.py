"""Middleware tests."""

from unittest.mock import Mock, patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from moviesapp.middleware import TimezoneMiddleware


class TimezoneMiddlewareTestCase(TestCase):
    """Timezone middleware test case."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=Mock())
        self.middleware = TimezoneMiddleware(self.get_response)

    def test_authenticated_user_with_timezone(self):
        """Test middleware with authenticated user having a timezone."""
        request = self.factory.get("/")
        user = Mock()
        user.is_authenticated = True
        user.timezone.key = "America/New_York"
        request.user = user

        with patch("moviesapp.middleware.timezone.activate") as mock_activate:
            self.middleware(request)
            mock_activate.assert_called_once()

    def test_authenticated_user_without_timezone(self):
        """Test middleware with authenticated user without timezone."""
        request = self.factory.get("/")
        user = Mock()
        user.is_authenticated = True
        user.timezone.key = None  # No timezone set
        request.user = user

        with patch("moviesapp.middleware.timezone.deactivate") as mock_deactivate:
            self.middleware(request)
            mock_deactivate.assert_called_once()

    def test_unauthenticated_user(self):
        """Test middleware with unauthenticated user."""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        with (
            patch("moviesapp.middleware.timezone.activate") as mock_activate,
            patch("moviesapp.middleware.timezone.deactivate") as mock_deactivate,
        ):
            self.middleware(request)
            # Neither should be called for unauthenticated users
            mock_activate.assert_not_called()
            mock_deactivate.assert_not_called()

    def test_middleware_calls_get_response(self):
        """Test that middleware calls the get_response function."""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        result = self.middleware(request)

        self.get_response.assert_called_once_with(request)
        self.assertEqual(result, self.get_response.return_value)
