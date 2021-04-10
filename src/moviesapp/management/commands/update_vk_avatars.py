# -*- coding: utf-8 -*-

from django_tqdm import BaseCommand

from moviesapp.models import User
from moviesapp.vk import get_vk_avatar


class Command(BaseCommand):
    help = "Updates vk avatars"

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        users = User.objects.all()
        t = self.tqdm(total=users.count())
        for user in users:
            vk = user.get_vk()
            if vk is not None:
                FIELDS = (
                    "photo_100",
                    "photo_200",
                )
                data = vk.get_data(FIELDS)
                avatar_small = get_vk_avatar(data["photo_100"])
                if avatar_small:
                    user.avatar_small = avatar_small
                avatar_big = get_vk_avatar(data["photo_200"])
                if avatar_big:
                    user.avatar_big = avatar_big
                user.save()
                t.set_description(str(user))
                t.update()
