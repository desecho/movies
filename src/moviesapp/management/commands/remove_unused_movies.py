from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Movie


class Command(BaseCommand):
    help = 'Removes unused movies'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        t = tqdm(total=movies.count())
        format = '{0: < %d}' % len(str(movies.last().pk))
        for movie in movies:
            info = format.format(movie.pk)
            t.set_description(info)
            if not movie.records.exists():
                movie.delete()
                t.write('{} removed'.format(movie))
            t.update()
