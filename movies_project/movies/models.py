# -*- coding: utf8 -*-
from django.db import models
from annoying.fields import JSONField
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    preferences = JSONField('настройки', default='{"titles": "russian"}')

def get_avatar_medium(self):
    return self.vk_profile.photo_medium or settings.VK_NO_IMAGE_MEDIUM

User.add_to_class('get_avatar_medium', get_avatar_medium)

def get_movie_ids(self):
    return Record.objects.filter(user=self).values_list('movie__pk')

User.add_to_class('get_movie_ids', get_movie_ids)

def is_vk_user(self):
    if self.username.isdigit():
        return True

User.add_to_class('is_vk_user', is_vk_user)

def user_unicode(self):
    return self.get_full_name()

User.__unicode__ = user_unicode


class List(models.Model):
    title = models.CharField('название', max_length=255)
    key_name = models.CharField('ключевое имя', max_length=255)

    class Meta:
        verbose_name = 'список'
        verbose_name_plural = 'списки'

    def __unicode__(self):
        return self.title


class Movie(models.Model):
    title = models.CharField('оригинальное название', max_length=255)
    title_ru = models.CharField('название', max_length=255)
    overview = models.TextField('описание (рус)', null=True)
    plot = models.TextField('описание (англ)', null=True)
    director = models.CharField('режиссёр', max_length=255, null=True)
    writer = models.CharField('сценарист', max_length=255, null=True)
    genre = models.CharField('жанр', max_length=255, null=True)
    actors = models.CharField('актёры', max_length=255, null=True)
    imdb_id = models.CharField('IMDB id', max_length=15, unique=True)
    tmdb_id = models.IntegerField('TMDB id', unique=True)
    imdb_rating = models.DecimalField('IMDB рейтинг', max_digits=2, decimal_places=1, null=True)
    poster = models.CharField('постер', max_length=255, null=True)
    release_date = models.DateField('дата выпуска', null=True)
    runtime = models.TimeField('длительность', null=True)
    homepage = models.URLField('сайт', null=True)
    trailers = JSONField('трейлеры', null=True)

    class Meta:
        verbose_name = 'фильм'
        verbose_name_plural = 'фильмы'

    def __unicode__(self):
        return self.title

    def imdb_url(self):
        return settings.IMDB_BASE_URL + self.imdb_id + '/'

    def poster_url(self, size):
        return settings.POSTER_BASE_URL + size + '/' + self.poster

    def has_trailers(self):
        number_of_trailers = 0
        for i in self.trailers:
            number_of_trailers += len(self.trailers[i])
        return number_of_trailers

    def poster_normal_url(self):
        if self.poster:
            url = self.poster_url(settings.POSTER_SIZE_NORMAL)
        else:
            url = settings.NO_POSTER_NORMAL_IMAGE_URL
        return url

    def poster_small_url(self):
        if self.poster:
            url = self.poster_url(settings.POSTER_SIZE_SMALL)
        else:
            url = settings.NO_POSTER_SMALL_IMAGE_URL
        return url

    def poster_big_url(self):
        if self.poster:
            return self.poster_url(settings.POSTER_SIZE_BIG)

    def torrent_search_title(self):
        title = self.title.replace("'", r"\'") + ' '
        if self.release_date:
            title += str(self.release_date.year) + ' '
        return title + '720p'


class Record(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь')
    movie = models.ForeignKey(Movie, verbose_name='фильм')
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
