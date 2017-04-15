# coding: utf-8
from __future__ import unicode_literals

from annoying.fields import JSONField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver
from django.utils.translation import LANGUAGE_SESSION_KEY, activate


def activate_user_language_preference(request, lang):
    activate(lang)
    request.session[LANGUAGE_SESSION_KEY] = lang


def get_poster_url(size, poster):
    if size == 'small':
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == 'normal':
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == 'big':
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = None  # is not used anywhere
    if poster is not None:
        return settings.POSTER_BASE_URL + poster_size + '/' + poster
    else:
        return no_image_url


class User(AbstractUser):
    only_for_friends = models.BooleanField(default=False)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')

    def get_avatar_medium(self):
        return self.vk_profile.photo_medium or settings.VK_NO_IMAGE_MEDIUM

    def get_movie_ids(self):
        return Record.objects.filter(user=self).values_list('movie__pk')

    def is_vk_user(self):
        if self.username.isdigit():
            return True

    def __unicode__(self):
        return self.get_full_name()


class List(models.Model):
    name = models.CharField(max_length=255)
    key_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    title_original = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)
    writer = models.CharField(max_length=255, null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    actors = models.CharField(max_length=255, null=True, blank=True)
    imdb_id = models.CharField(max_length=15, unique=True)
    tmdb_id = models.IntegerField(unique=True)
    imdb_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    poster = models.CharField(max_length=255, null=True)
    release_date = models.DateField(null=True)
    runtime = models.TimeField(null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    trailers = JSONField(null=True, blank=True)

    class Meta:
        ordering = ['pk']

    def __unicode__(self):
        return self.title

    def imdb_url(self):
        return settings.IMDB_BASE_URL + self.imdb_id + '/'

    def has_trailers(self):
        for trailer_type in self.trailers:
            if len(self.trailers[trailer_type]) > 0:
                return True

    def _get_poster(self, size):
        return get_poster_url(size, self.poster)

    @property
    def poster_normal(self):
        return self._get_poster('normal')

    @property
    def poster_small(self):
        return self._get_poster('small')

    @property
    def poster_big(self):
        return self._get_poster('big')


class Record(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie, related_name='records')
    list = models.ForeignKey(List)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, default='')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.movie.title


class Action(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ActionRecord(models.Model):
    user = models.ForeignKey(User)
    action = models.ForeignKey(Action)
    movie = models.ForeignKey(Movie)
    list = models.ForeignKey(List, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} {}'.format(self.movie.title, self.action.name)


@receiver(user_logged_in)
def lang(sender, **kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
