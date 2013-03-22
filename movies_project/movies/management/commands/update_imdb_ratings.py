import urllib2
import json
from django.core.management.base import BaseCommand
from movies.models import Movie


class Command(BaseCommand):
    help = 'Updates the IMDB ratings'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        for movie in movies:
            html = urllib2.urlopen("http://www.imdbapi.com/?i=%s" % movie.imdb_id).read()
            imdb_data = json.loads(html)
            rating = imdb_data.get('imdbRating')
            if rating == 'N/A':
                rating = None
            movie.imdb_rating = rating
            movie.save()
