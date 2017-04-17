from django.conf import settings

import vkontakte
import facebook

from .models import User


class Vk:
    def __init__(self, user):
        self.vk = vkontakte.API(settings.SOCIAL_AUTH_VK_APP_KEY, settings.SOCIAL_AUTH_VK_APP_SECRET)
        self.user = user

    def get_friends(self):
        friends = self.vk.friends.get(uid=self.user.get_vk_uid())
        friends = map(str, friends)
        return User.objects.filter(username__in=friends)


class Fb:
    def __init__(self, user):
        access_token = user.get_fb_account().extra_data['access_token']
        self.fb = facebook.GraphAPI(access_token=access_token, version='2.7')

    def get_friends(self):
        friends = self.fb.get_connections(id='me', connection_name='friends')['data']
        friends_ids = [f['id'] for f in friends]
        friends = User.objects.filter(social_auth__provider='facebook', social_auth__uid__in=friends_ids)
        return friends
