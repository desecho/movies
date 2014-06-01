from movies.models import Movie
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):
        for movie in Movie.objects.all():
            if not movie.records.exists():
                movie.delete()
                print movie.title
