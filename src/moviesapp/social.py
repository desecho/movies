import facebook
import vkontakte
from django.conf import settings

from .models import User


class Vk:
    def __init__(self, user):
        vk_account = user.get_vk_account()
        self.vk = vkontakte.API(*settings.VK_BACKENDS_CREDENTIALS[vk_account.provider])
        self.vk_id = vk_account.uid
        self.user = user

    def get_friends(self):
        friends = self.vk.friends.get(uid=self.vk_id)
        friends_ids = map(str, friends)
        friends = User.objects.filter(social_auth__provider__in=settings.VK_BACKENDS,
                                      social_auth__uid__in=friends_ids)
        return friends

    def get_data(self, fields):
        return self.vk.getProfiles(uids=self.vk_id, fields=','.join(fields))[0]


class Fb:
    def __init__(self, user):
        access_token = user.get_fb_account().extra_data['access_token']
        self.fb = facebook.GraphAPI(access_token=access_token, version='2.7')

    def get_friends(self):
        friends = self.fb.get_connections(id='me', connection_name='friends')['data']
        friends_ids = [f['id'] for f in friends]
        friends = User.objects.filter(social_auth__provider='facebook', social_auth__uid__in=friends_ids)
        return friends


def load_user_data(backend, user, response, *args, **kwargs):
    if user.loaded_initial_data:
        return

    if backend.name in settings.VK_BACKENDS:
        # we don't need the username and email because they are already loaded
        FIELDS = ('first_name', 'last_name')
        data = Vk(user).get_data(FIELDS)
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.language = 'ru'
        user.loaded_initial_data = True
        user.save()
