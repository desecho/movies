import time

import vkontakte
from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import User

FIELDS = (
    'first_name',
    'last_name',
    'nickname',
    'domain',
    'sex',
    'city',
    'country',
    'timezone',
    'photo',
    'photo_medium',
    'photo_big',
    'photo_rec',
)


# TODO REDO
class Command(BaseCommand):
    help = 'Updates VK profiles'

    def handle(self, *args, **options):
        vk = vkontakte.API(settings.VK_APP_ID, settings.VK_APP_SECRET)
        for user in User.objects.all():
            if user.is_vk_user():
                vk_profile = user.vk_profile
                new_data = vk.getProfiles(uids=str(user.username),
                                          fields=','.join(FIELDS))[0]
                for field in FIELDS:
                    if field == 'city':
                        try:
                            vk_profile.city = new_data[field]
                        except:
                            pass
                    elif field == 'country':
                        try:
                            vk_profile.country = new_data[field]
                        except:
                            pass
                    elif field == 'first_name' or field == 'last_name':
                        try:
                            setattr(user, field, new_data[field])
                        except:
                            pass
                    else:
                        try:
                            setattr(vk_profile, field, new_data[field])
                        except:
                            pass
                vk_profile.save()
                user.save()
                time.sleep(0.34)
