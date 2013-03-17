from django.db import models
from annoying.fields import JSONField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings


class List(models.Model):
    title = models.CharField(max_length=255)
    key_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.title


class Movie(models.Model):
    title = models.CharField(max_length=255)
    plot = models.TextField(null=True)
    director = models.CharField(max_length=255, null=True)
    writer = models.CharField(max_length=255, null=True)
    genre = models.CharField(max_length=255, null=True)
    actors = models.CharField(max_length=255, null=True)
    imdb_id = models.CharField(max_length=15, unique=True)
    tmdb_id = models.IntegerField(unique=True)
    imdb_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    poster = models.URLField(max_length=255, null=True)
    release_date = models.DateField(null=True)
    homepage = models.URLField(null=True)
    trailers = JSONField(null=True)

    def __unicode__(self):
        return self.title

    def imdb_url(self):
        return settings.IMDB_BASE_URL + self.imdb_id + '/'

    def poster_url(self, size):
        if self.poster:
            url = settings.POSTER_BASE_URL + size + '/' + self.poster
        else:
            url = settings.NO_POSTER_IMAGE_URL
        return url

    def poster_big_url(self):
        return self.poster_url(settings.POSTER_SIZE_BIG)

    def poster_small_url(self):
        return self.poster_url(settings.POSTER_SIZE_SMALL)


class Record(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)
    list = models.ForeignKey(List)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.movie.title