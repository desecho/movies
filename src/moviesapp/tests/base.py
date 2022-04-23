import json
import os
from datetime import datetime

import pytz
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.test import TestCase

from moviesapp.models import ActionRecord, User


class BaseTestCase(TestCase):
    fixtures = [
        "lists.json",
        "actions.json",
        "users.json",
    ]

    USER_USERNAME = "neo"
    USER_PASSWORD = "password"
    # Superuser - admin/adminpassword
    # Another user - fox/password

    @staticmethod
    def get_soup(response):
        return BeautifulSoup(response.content, features="html.parser")

    def setUp(self):
        self.user = User.objects.get(username=self.USER_USERNAME)

        # Make sure we have current dates in action
        action_records = ActionRecord.objects.all()
        for action_record in action_records:
            action_record.date = datetime.now(pytz.utc)
            action_record.save()

    def login(self, username=None):
        if username is None:
            username = self.USER_USERNAME
        self.client.logout()
        self.client.login(username=username, password=self.USER_PASSWORD)

    @staticmethod
    def load_json(filename):
        base_path = os.path.join(settings.SRC_DIR, "moviesapp", "tests", "files")
        path = os.path.join(base_path, filename)
        with open(path, encoding="utf8") as f:
            return json.load(f)

    @staticmethod
    def dump_instance(instance):
        return json.dumps(model_to_dict(instance), cls=DjangoJSONEncoder)

    @property
    def is_authenticated(self):
        return "_auth_user_id" in self.client.session.keys()


class BaseTestLoginCase(BaseTestCase):
    fixtures = [
        "users.json",
        "lists.json",
        "actions.json",
        "movies.json",
        "records.json",
        "action_records.json",
    ]

    def setUp(self):
        super().setUp()
        self.login()
