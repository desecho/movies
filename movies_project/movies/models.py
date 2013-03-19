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
