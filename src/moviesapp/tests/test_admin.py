"""Admin tests."""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from moviesapp.admin import ActionAdmin, ListAdmin, ProviderAdmin
from moviesapp.models import Action, List, Provider


class AdminTestCase(TestCase):
    """Admin test case."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = AnonymousUser()

    def test_list_admin_has_no_delete_permission(self):
        """Test that ListAdmin doesn't allow delete permission."""
        admin = ListAdmin(List, None)

        # Test without object
        self.assertFalse(admin.has_delete_permission(self.request))

        # Test with object
        list_obj = List(id=1, name="Test List")
        self.assertFalse(admin.has_delete_permission(self.request, list_obj))

    def test_action_admin_has_no_delete_permission(self):
        """Test that ActionAdmin doesn't allow delete permission."""
        admin = ActionAdmin(Action, None)

        # Test without object
        self.assertFalse(admin.has_delete_permission(self.request))

        # Test with object
        action_obj = Action(id=1, name="Test Action")
        self.assertFalse(admin.has_delete_permission(self.request, action_obj))

    def test_provider_admin_has_no_delete_permission(self):
        """Test that ProviderAdmin doesn't allow delete permission."""
        admin = ProviderAdmin(Provider, None)

        # Test without object
        self.assertFalse(admin.has_delete_permission(self.request))

        # Test with object
        provider_obj = Provider(id=1, name="Test Provider")
        self.assertFalse(admin.has_delete_permission(self.request, provider_obj))
