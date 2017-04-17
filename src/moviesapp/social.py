from django.conf import settings

import vkontakte
import facebook

from .models import User


class Vk:
    def __init__(self, user):
        self.vk_account = user.get_vk_account()
        self.vk = vkontakte.API(*settings.VK_BACKENDS_CREDENTIALS[self.vk_account.provider])
        self.user = user

    def get_friends(self):
        friends = self.vk.friends.get(uid=self.vk_account.uid)
        friends_ids = map(str, friends)
        friends = User.objects.filter(social_auth__provider__in=settings.VK_BACKENDS,
                                      social_auth__uid__in=friends_ids)
        return friends


class Fb:
    def __init__(self, user):
        access_token = user.get_fb_account().extra_data['access_token']
        self.fb = facebook.GraphAPI(access_token=access_token, version='2.7')

    def get_friends(self):
        friends = self.fb.get_connections(id='me', connection_name='friends')['data']
        friends_ids = [f['id'] for f in friends]
        friends = User.objects.filter(social_auth__provider='facebook', social_auth__uid__in=friends_ids)
        return friends
