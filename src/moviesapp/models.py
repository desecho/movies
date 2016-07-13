# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver

from annoying.fields import JSONField

from .utils import activate_user_language_preference, get_poster_url


class User(AbstractUser):
    only_for_friends = models.BooleanField(_('only for friends'), default=False)
    language = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        default='en',
    )

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
    name = models.CharField('название', max_length=255)
    key_name = models.CharField('ключевое имя', max_length=255)

    class Meta:
        verbose_name = 'список'
        verbose_name_plural = 'списки'

    def __unicode__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(_('title'), max_length=255)
    title_original = models.CharField(_('original title'), max_length=255)
    country = models.CharField('страна', max_length=255, null=True, blank=True)
    description = models.TextField(_('description'), null=True, blank=True)
    director = models.CharField('режиссёр', max_length=255, null=True, blank=True)
    writer = models.CharField('сценарист', max_length=255, null=True, blank=True)
    genre = models.CharField('жанр', max_length=255, null=True, blank=True)
    actors = models.CharField('актёры', max_length=255, null=True, blank=True)
    imdb_id = models.CharField('IMDB id', max_length=15, unique=True)
    tmdb_id = models.IntegerField('TMDB id', unique=True)
    imdb_rating = models.DecimalField('IMDB рейтинг', max_digits=2, decimal_places=1, null=True)
    poster = models.CharField(_('poster'), max_length=255, null=True)
    release_date = models.DateField('дата выпуска', null=True)
    runtime = models.TimeField('длительность', null=True, blank=True)
    homepage = models.URLField('сайт', null=True, blank=True)
    trailers = JSONField('трейлеры', null=True, blank=True)

    class Meta:
        verbose_name = 'фильм'
        verbose_name_plural = 'фильмы'
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
    user = models.ForeignKey(User, verbose_name='пользователь')
    movie = models.ForeignKey(Movie, verbose_name='фильм', related_name='records')
    list = models.ForeignKey(List, verbose_name='список')
    rating = models.IntegerField('рейтинг', default=0)
    comment = models.CharField('комментарий', max_length=255, default='')
    date = models.DateTimeField('дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'

    def __unicode__(self):
        return self.movie.title


class Action(models.Model):
    name = models.CharField('название', max_length=255)

    class Meta:
        verbose_name = 'действие'
        verbose_name_plural = 'действия'

    def __unicode__(self):
        return self.name


class ActionRecord(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь')
    action = models.ForeignKey(Action, verbose_name='тип действия')
    movie = models.ForeignKey(Movie, verbose_name='фильм')
    list = models.ForeignKey(List, verbose_name='список', blank=True, null=True)
    comment = models.CharField('комментарий', max_length=255, blank=True, null=True)
    rating = models.IntegerField('рейтинг', blank=True, null=True)
    date = models.DateTimeField('дата', auto_now_add=True)

    class Meta:
        verbose_name = 'запись действия'
        verbose_name_plural = 'записи действий'

    def __unicode__(self):
        return self.movie.title + ' ' + self.action.name


@receiver(user_logged_in)
def lang(sender, **kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
