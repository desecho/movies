"""Base code for tests."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.test import TestCase
from django.test.client import Client

from moviesapp.models import ActionRecord, User

CONTENT_TYPE = "application/json"


class BaseClient(Client):
    """Base client class."""

    def __init__(self, enforce_csrf_checks=False, **defaults):
        """Initialize client with CSRF disabled by default for tests."""
        super().__init__(enforce_csrf_checks=enforce_csrf_checks, **defaults)

    def post_ajax(  # pylint:disable=too-many-positional-arguments
        self,
        path,
        data=None,
        content_type=CONTENT_TYPE,
        follow=False,
        secure=False,
        **extra,
    ):
        """Perform an AJAX POST request."""
        return self.post(path, data, content_type, follow, secure, **extra)

    def put_ajax(  # pylint:disable=too-many-positional-arguments
        self,
        path,
        data="",
        content_type=CONTENT_TYPE,
        follow=False,
        secure=False,
        **extra,
    ):
        """Perform an AJAX PUT request."""
        return self.put(path, data, content_type, follow, secure, **extra)


class BaseTestCase(TestCase):
    """Base test class."""

    maxDiff = None
    client_class = BaseClient

    fixtures = [
        "lists.json",
        "actions.json",
        "users.json",
        "vk_countries.json",
        "providers.json",
    ]

    USER_USERNAME = "neo"
    USER_PASSWORD = "password"
    # Superuser - admin/adminpassword
    # Another user - fox/password

    @staticmethod
    def get_soup(response):
        """Get BeautifulSoup object from response."""
        return BeautifulSoup(response.content, features="html.parser")

    def setUp(self):
        """Set up test environment."""
        self.user = User.objects.get(username=self.USER_USERNAME)

        # Make sure we have current dates in action
        action_records = ActionRecord.objects.all()
        for action_record in action_records:
            action_record.date = datetime.now(timezone.utc)
            action_record.save()

    def login(self, username: Optional[str] = None):
        """Login."""
        if username is None:
            username = self.USER_USERNAME
        self.client.logout()
        self.client.login(username=username, password=self.USER_PASSWORD)

    @staticmethod
    def load_json(filename: str):
        """Load JSON from file."""
        base_path = os.path.join(settings.SRC_DIR, "moviesapp", "tests", "files")
        path = os.path.join(base_path, filename)
        with open(path, encoding="utf8") as f:
            return json.load(f)

    @staticmethod
    def dump_instance(instance):
        """Dump instance to JSON."""
        return json.dumps(model_to_dict(instance), cls=DjangoJSONEncoder)

    @property
    def is_authenticated(self):
        """Return True if user is authenticated."""
        return "_auth_user_id" in self.client.session.keys()


class BaseTestLoginCase(BaseTestCase):
    """Base test class (authenticated)."""

    fixtures = [
        "users.json",
        "lists.json",
        "actions.json",
        "movies.json",
        "records.json",
        "action_records.json",
    ]

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.login()
