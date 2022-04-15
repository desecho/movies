from django_tqdm import BaseCommand

from moviesapp.models import User
from moviesapp.vk import update_user_vk_avatar


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
                user = update_user_vk_avatar(user, data)
                user.save()
                t.set_description(str(user))
                t.update()
