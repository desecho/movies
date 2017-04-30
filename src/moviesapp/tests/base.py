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
    ]

    USER_NAME = 'user'
    USER_EMAIL = 'user@test.com'
    USER_PWD = USER_NAME

    def get_soup(self, response):
        return BeautifulSoup(response.content)

    def get_json(self, response):
        return json.loads(response.content)

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            self.USER_NAME, email=self.USER_EMAIL,
            password=self.USER_PWD
        )

    def login(self):
        self.client.logout()
        self.client.login(
            username=self.USER_NAME,
            password=self.USER_PWD
        )

    def load_json(self, filename):
        base_path = os.path.join(settings.BASE_DIR, 'moviesapp', 'tests', 'files')
        path = os.path.join(base_path, filename)
        return json.loads(open(path).read())

    def dump_instance(self, instance):
        return json.dumps(model_to_dict(instance), cls=DjangoJSONEncoder)
