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

    USER_NAME = 'neo'
    USER_PWD = 'password'
    # Superuser - admin/adminpassword
    # Another user - fox/password

    def get_soup(self, response):
        return BeautifulSoup(response.content)

    def get_json(self, response):
        return json.loads(response.content)

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.get(username='neo')

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


class BaseTestLoginCase(BaseTestCase):
    def setUp(self):
        super(BaseTestLoginCase, self).setUp()
        self.login()
