# -*- coding: utf-8 -*-
import facebook
import vkontakte
# Not using django-mysql instead because it's not supported by modeltranslation.
from annoying.fields import JSONField
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.auth.signals import user_logged_in
from django.core.cache import cache
from django.db import models
from django.dispatch import receiver
from django.utils.translation import LANGUAGE_SESSION_KEY, ugettext_lazy as _


class Vk:
    def __init__(self, user):
        vk_account = user.get_vk_account()
        self.vk = vkontakte.API(*settings.VK_BACKENDS_CREDENTIALS[vk_account.provider])
        self.vk_id = vk_account.uid
        self.user = user

    def get_friends(self):
        friends = cache.get('vk_friends')
        if friends is None:
            friends = self.vk.friends.get(uid=self.vk_id)
            cache.set('vk_friends', friends)
        friends_ids = map(str, friends)
        friends = User.objects.filter(social_auth__provider__in=settings.VK_BACKENDS, social_auth__uid__in=friends_ids)
        return friends

    def get_data(self, fields):
        return self.vk.getProfiles(uids=self.vk_id, fields=','.join(fields))[0]


class Fb:
    def __init__(self, user):
        access_token = user.get_fb_account().extra_data['access_token']
        self.fb = facebook.GraphAPI(access_token=access_token, version='2.7')

    def get_friends(self):
        friends = cache.get('fb_friends')
        if friends is None:
            friends = self.fb.get_connections(id='me', connection_name='friends')['data']
            cache.set('fb_friends', friends)
        friends_ids = [f['id'] for f in friends]
        friends = User.objects.filter(social_auth__provider='facebook', social_auth__uid__in=friends_ids)
        return friends


def activate_user_language_preference(request, lang):
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
    return no_image_url


class UserBase:
    def get_movie_ids(self):
        return self.get_records().values_list('movie__pk')

    def get_records(self):
        if self.is_authenticated:
            return self.records.all()
        else:
            return Record.objects.none()

    def get_record(self, id_):
        return self.get_records().get(pk=id_)

    def _get_fb_accounts(self):
        return self.social_auth.filter(provider='facebook')

    def is_fb_user(self):
        if self.is_authenticated:
            return self._get_fb_accounts().exists()
        return False

    def get_fb_account(self):
        if self.is_fb_user():
            return self._get_fb_accounts()[0]

    def _get_vk_accounts(self):
        return self.social_auth.filter(provider__in=settings.VK_BACKENDS)

    def get_vk_account(self):
        if self.is_vk_user():
            return self._get_vk_accounts()[0]

    def is_vk_user(self):
        """
        Show if a user has a vk account.

        It doesn't necessarily mean that he is currently using the app.
        Note: currently it does because it is not possible to link a vk-app account and a website account.
        But it is likely to change in the future.
        """
        if self.is_authenticated:
            return self._get_vk_accounts().exists()
        return False

    def is_linked(self):
        if self.is_authenticated:
            return self.social_auth.exists()
        return False

    def get_users(self, friends=False, sort=False):
        if friends:
            return self.get_friends(sort=sort)
        return self._get_available_users_and_friends(sort=sort)

    def _get_available_users_and_friends(self, sort=False):
        available_users = User.objects.exclude(only_for_friends=True).exclude(pk=self.pk)
        users = available_users | self.get_friends()
        if sort:
            users = users.order_by('first_name')
        return list(set(users))

    def get_friends(self, sort=False):
        friends = User.objects.none()
        if self.is_linked:
            if self.is_vk_user():
                friends |= Vk(self).get_friends()
            if self.is_fb_user():
                friends |= Fb(self).get_friends()
            if sort:
                friends = friends.order_by('first_name')
        return friends

    def has_friends(self):
        return self.get_friends().exists()


class User(AbstractUser, UserBase):
    only_for_friends = models.BooleanField(
        default=False,
        help_text=_('Privacy setting. It indicates whether only your friends have access to your movie lists.'))
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    location = models.CharField(max_length=100, null=True, blank=True)
    avatar_small = models.URLField(null=True, blank=True)
    avatar_big = models.URLField(null=True, blank=True)
    loaded_initial_data = models.BooleanField(default=False)

    def __str__(self):
        name = self.get_full_name()
        if name:
            return name
        else:
            return self.username

    def _get_movies_number(self, list_id):
        return self.get_records().filter(list_id=list_id).count()

    @property
    def movies_watched_number(self):
        return self._get_movies_number(List.WATCHED)

    @property
    def movies_to_watch_number(self):
        return self._get_movies_number(List.TO_WATCH)


class UserAnonymous(AnonymousUser, UserBase):
    def __init__(self, request):  # pylint: disable=unused-argument
        super().__init__()


class List(models.Model):
    WATCHED = 1
    TO_WATCH = 2
    name = models.CharField(max_length=255)
    key_name = models.CharField(max_length=255)

    def __str__(self):
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
    imdb_id = models.CharField(max_length=15, unique=True, db_index=True)
    tmdb_id = models.IntegerField(unique=True)
    imdb_rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    poster = models.CharField(max_length=255, null=True)
    release_date = models.DateField(null=True)
    runtime = models.TimeField(null=True, blank=True)
    homepage = models.URLField(null=True, blank=True)
    trailers = JSONField(null=True, blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.title

    def imdb_url(self):
        return settings.IMDB_BASE_URL + self.imdb_id + '/'

    def get_trailers(self):
        if self.trailers:
            return self.trailers
        else:
            return self.trailers_en

    def has_trailers(self):
        return bool(self.get_trailers())

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

    @property
    def id_title(self):
        return f'{self.pk} - {self}'

    def cli_string(self, last_movie_id):
        """
        Return string version for CLI.

        We need last_movie_id because we want to know how big is the number (in characters) to be able to make
        perfect formatting.
        We need to keep last_movie_id as a parameter because otherwise we hit the database every time we run the
        function.
        """
        MAX_CHARS = 40
        ENDING = '..'
        id_format = '{0: < %d}' % (len(str(last_movie_id)) + 1)
        title = str(self)
        title = (title[:MAX_CHARS] + ENDING) if len(title) > MAX_CHARS else title
        id_ = id_format.format(self.pk)
        title_max_length = MAX_CHARS + len(ENDING)
        title_format = '{:%ds}' % title_max_length
        title = title_format.format(title)
        return f'{id_} - {title}' [1:].decode('utf8')


class Record(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='records')
    movie = models.ForeignKey(Movie, models.CASCADE, related_name='records')
    list = models.ForeignKey(List, models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, default='')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.movie.title


class Action(models.Model):
    ADDED_MOVIE = 1
    CHANGED_LIST = 2
    ADDED_RATING = 3
    ADDED_COMMENT = 4
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ActionRecord(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='actions')
    action = models.ForeignKey(Action, models.CASCADE)
    movie = models.ForeignKey(Movie, models.CASCADE)
    list = models.ForeignKey(List, models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.movie.title} {self.action.name}'


@receiver(user_logged_in)
def lang(**kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
