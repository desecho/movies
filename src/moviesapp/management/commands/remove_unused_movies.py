from django.core.management.base import BaseCommand

from ...models import Movie


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):
        for movie in Movie.objects.all():
            if not movie.records.exists():
                movie.delete()
                print '{} removed'.format(movie)
