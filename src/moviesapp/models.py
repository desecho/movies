# -*- coding: utf8 -*-
from annoying.fields import JSONField
from south.modelsinspector import add_introspection_rules
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

add_introspection_rules([], ["^annoying.fields.JSONField"])


def get_poster_url(size, poster, filename=None):
    if size == 'small':
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == 'normal':
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == 'big':
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = None

    if poster:
        if filename is None:
            filename = poster.filename
        return settings.POSTER_BASE_URL + poster_size + '/' + filename
    else:
        return no_image_url


class User(AbstractUser):
    # preferences = JSONField('настройки', default='{"lang": "ru"}') REMOVED

    @property
    def preferences(self):
        return {'lang': 'ru'}

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
    # country = models.CharField('страна', max_length=255, null=True, blank=True) REMOVED
    overview = models.TextField('описание (рус)', null=True, blank=True)
    plot = models.TextField('описание (англ)', null=True, blank=True)
    director = models.CharField('режиссёр', max_length=255, null=True, blank=True)
    writer = models.CharField('сценарист', max_length=255, null=True, blank=True)
    genre = models.CharField('жанр', max_length=255, null=True, blank=True)
    actors = models.CharField('актёры', max_length=255, null=True, blank=True)
    imdb_id = models.CharField('IMDB id', max_length=15, unique=True)
    tmdb_id = models.IntegerField('TMDB id', unique=True)
    imdb_rating = models.DecimalField('IMDB рейтинг', max_digits=2, decimal_places=1, null=True)
    # poster_ru = models.CharField('постер (рус)', max_length=255, null=True) REMOVED
    poster = models.CharField('постер (англ)', max_length=255, null=True)  # RENAMED FROM poster_en
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

    def get_poster(self, size, lang):
        return 'http://media.creativebloq.futurecdn.net/sites/creativebloq.com/files/articles/article/2012/07/postersilence.jpg'
        #TODO
        # poster = self.poster_ru # TODO Fix this
        # filename = eval('self.poster_' + lang) # TODO Fix this
        filename = None  # TODO Fix this
        return get_poster_url(size, poster, filename)

    def poster_en_small_url(self):
        return self.get_poster('small', 'en')

    def poster_ru_small_url(self):
        return self.get_poster('small', 'ru')

    def poster_en_normal_url(self):
        return self.get_poster('normal', 'en')

    def poster_ru_normal_url(self):
        return self.get_poster('normal', 'ru')

    def poster_en_big_url(self):
        return self.get_poster('big', 'en')

    def poster_ru_big_url(self):
        return self.get_poster('big', 'ru')

    # def torrent_search_title(self):
    #     title = self.title.replace("'", r"\'") + ' '
    #     if self.release_date:
    #         title += str(self.release_date.year) + ' '
    #     return title + '720p'


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
