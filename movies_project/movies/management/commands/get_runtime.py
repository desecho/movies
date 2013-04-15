import urllib2
import json
from django.core.management.base import BaseCommand
from movies.models import Movie
from datetime import datetime

class Command(BaseCommand):
    help = 'Gets runtime'

    def handle(self, *args, **options):
        def get_runtime(id):
            html = urllib2.urlopen("http://www.imdbapi.com/?i=%s" % id).read()
            imdb_data = json.loads(html)
            runtime = imdb_data.get('Runtime')
            print(runtime)
            if runtime != 'N/A':
                runtime = datetime.strptime(runtime, '%H h %M min')
                print(runtime)
                return runtime

        for movie in Movie.objects.all()[:5]:
            print (movie.pk)
            runtime = get_runtime(movie.imdb_id)
            movie.runtime = runtime
            movie.save()
