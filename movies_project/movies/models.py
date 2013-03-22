# -*- coding: utf8 -*-
from django.db import models
from annoying.fields import JSONField
from django.contrib.auth.models import User
from django.conf import settings


class List(models.Model):
    title = models.CharField('название', max_length=255)
    key_name = models.CharField('ключевое имя', max_length=255)

    class Meta:
        verbose_name = 'список'
        verbose_name_plural = 'списки'

    def __unicode__(self):
        return self.title


class Movie(models.Model):
    title = models.CharField('название', max_length=255)
    plot = models.TextField('описание', null=True)
    director = models.CharField('режиссёр', max_length=255, null=True)
    writer = models.CharField('сценарист', max_length=255, null=True)
    genre = models.CharField('жанр', max_length=255, null=True)
    actors = models.CharField('актёры', max_length=255, null=True)
    imdb_id = models.CharField('IMDB id', max_length=15, unique=True)
    tmdb_id = models.IntegerField('TMDB id', unique=True)
    imdb_rating = models.DecimalField('IMDB рейтинг', max_digits=2, decimal_places=1, null=True)
    poster = models.URLField('постер', max_length=255, null=True)
    release_date = models.DateField('дата выпуска', null=True)
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

    def poster_big_url(self):
        if self.poster:
            url = self.poster_url(settings.POSTER_SIZE_BIG)
        else:
            url = settings.NO_POSTER_BIG_IMAGE_URL
        return url

    def poster_small_url(self):
        if self.poster:
            url = self.poster_url(settings.POSTER_SIZE_SMALL)
        else:
            url = settings.NO_POSTER_IMAGE_URL
        return url


class Record(models.Model):
    user = models.ForeignKey(User, verbose_name='пользователь')
    movie = models.ForeignKey(Movie, verbose_name='фильм')
    list = models.ForeignKey(List, verbose_name='список')
    rating = models.IntegerField('рейтинг', default=0)
    comment = models.CharField('комментарий', max_length=255, default='')

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'

    def __unicode__(self):
        return self.movie.title


def number_of_movies(user, list_id):
    return Record.objects.filter(list_id=list_id, user=user).count()


def number_of_watched(self):
    return number_of_movies(self, 1)


def number_of_to_watch(self):
    return number_of_movies(self, 2)


def get_movie_count(self):
    return '%d / %d' % (self.number_of_watched(), self.number_of_to_watch())


def is_vk_user(self):
    if self.username.isdigit():
        return True

User.add_to_class('number_of_watched', number_of_watched)
User.add_to_class('number_of_to_watch', number_of_to_watch)
User.add_to_class('get_movie_count', get_movie_count)
User.add_to_class('is_vk_user', is_vk_user)
