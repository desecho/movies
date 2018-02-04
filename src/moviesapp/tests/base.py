import json
import os

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.test import TestCase


class BaseTestCase(TestCase):
    fixtures = [
        'lists.json',
        'actions.json',
        'users.json',
    ]

    USER_USERNAME = 'neo'
    USER_PASSWORD = 'password'
    # Superuser - admin/adminpassword
    # Another user - fox/password

    @staticmethod
    def get_content(response):
        return response.content.decode('utf-8')

    @staticmethod
    def get_soup(response):
        return BeautifulSoup(response.content)

    def get_json(self, response):
        return json.loads(self.get_content(response))

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username=self.USER_USERNAME)

    def login(self, username=None):
        if username is None:
            username = self.USER_USERNAME
        self.client.logout()
        self.client.login(username=username, password=self.USER_PASSWORD)

    def load_json(self, filename):
        base_path = os.path.join(settings.BASE_DIR, 'moviesapp', 'tests', 'files')
        path = os.path.join(base_path, filename)
        with open(path) as f:
            return json.load(f)

    def dump_instance(self, instance):
        return json.dumps(model_to_dict(instance), cls=DjangoJSONEncoder)


class BaseTestLoginCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login()
