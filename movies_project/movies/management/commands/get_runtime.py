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
            if runtime != 'N/A':
                try:
                    runtime = datetime.strptime(runtime, '%H h %M min')
                except:
                    try:
                        runtime = datetime.strptime(runtime, '%H h')
                    except:
                        try:
                            runtime = datetime.strptime(runtime, '%M min')
                        except:
                            return
                return runtime

        for movie in Movie.objects.all():
            runtime = get_runtime(movie.imdb_id)
            movie.runtime = runtime
            movie.save()
