import vk_api
from annoying.fields import JSONField  # Not using django-mysql instead because it's not supported by modeltranslation.
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from vk_api.exceptions import ApiError

from moviesapp.exceptions import VKError
from moviesapp.fb import Fb
from moviesapp.vk import Vk


# Cannot be moved to utils because it would cause circular imports
def get_poster_url(size, poster):
    if size == "small":
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == "normal":
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == "big":
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = None  # is not used anywhere
    if poster is not None:
        return settings.POSTER_BASE_URL + poster_size + "/" + poster
    return no_image_url


class UserBase:
    def get_movie_ids(self):
        return self.get_records().values_list("movie__pk")

    def get_records(self):
        if self.is_authenticated:
            return self.records.all()
        return Record.objects.none()

    def get_record(self, id_):
        return self.get_records().get(pk=id_)

    def _get_fb_accounts(self):
        return self.social_auth.filter(provider="facebook")

    def is_fb_user(self):
        if self.is_authenticated:
            return self._get_fb_accounts().exists()
        return False

    # It is requried that `is_fb_user` is run before running this.
    def get_fb_account(self):  # 2DO possibly remove it from this class.
        return self._get_fb_accounts()[0]

    def _get_vk_accounts(self):
        return self.social_auth.filter(provider__in=settings.VK_BACKENDS)

    # It is requried that `is_vk_user` is run before running this.
    def get_vk_account(self):  # 2DO possibly remove it from this class.
        vk_accounts = self._get_vk_accounts()
        if len(vk_accounts) == 1:
            return vk_accounts[0]
        for vk_account in vk_accounts:
            vk_session = vk_api.VkApi(token=vk_account.access_token)
            vk = vk_session.get_api()
            try:
                vk.users.get(fields=["screen_name"])
            except ApiError:
                continue
            return vk_account
        raise VKError

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

    @property
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
        # We need distinct here because we can't concatenate distinct and non-distinct querysets.
        users = available_users.distinct() | self.get_friends()
        if sort:
            users = users.order_by("first_name")
        return list(set(users))

    def get_vk(self):
        if self.is_vk_user():
            return Vk(self)
        return None

    def get_friends(self, sort=False):
        friends = User.objects.none()
        if self.is_linked:
            if self.is_vk_user():  # 2DO possibly refactor this (this check is run twice)
                friends |= self.get_vk().get_friends()
            if self.is_fb_user():
                friends |= Fb(self).get_friends()
            if sort:
                friends = friends.order_by("first_name")
        return friends

    def has_friends(self):
        return self.get_friends().exists()


class User(AbstractUser, UserBase):
    only_for_friends = models.BooleanField(
        verbose_name=_("Privacy"), default=False, help_text=_("Show my lists only to friends")
    )
    language = models.CharField(
        max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("Language")
    )
    avatar_small = models.URLField(null=True, blank=True)
    avatar_big = models.URLField(null=True, blank=True)
    loaded_initial_data = models.BooleanField(default=False)

    def __str__(self):
        name = self.get_full_name()
        if name:
            return name
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
        return str(self.name)

    @classmethod
    def is_valid_id(self, list_id):
        return list_id in [self.WATCHED, self.TO_WATCH]


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
        ordering = ["pk"]

    def __str__(self):
        return str(self.title)

    def imdb_url(self):
        return settings.IMDB_BASE_URL + self.imdb_id + "/"

    def get_trailers(self):
        if self.trailers:
            return self.trailers
        return self.trailers_en

    def has_trailers(self):
        return bool(self.get_trailers())

    def _get_poster(self, size):
        return get_poster_url(size, self.poster)

    @property
    def poster_normal(self):
        return self._get_poster("normal")

    @property
    def poster_small(self):
        return self._get_poster("small")

    @property
    def poster_big(self):
        return self._get_poster("big")

    @property
    def id_title(self):
        return f"{self.pk} - {self}"

    def cli_string(self, last_movie_id):
        """
        Return string version for CLI.

        We need last_movie_id because we want to know how big is the number (in characters) to be able to make
        perfect formatting.
        We need to keep last_movie_id as a parameter because otherwise we hit the database every time we run the
        function.
        """
        MAX_CHARS = 40
        ENDING = ".."
        n = len(str(last_movie_id)) + 1
        id_format = f"{{0: < {n}}}"
        title = str(self)
        title = (title[:MAX_CHARS] + ENDING) if len(title) > MAX_CHARS else title
        id_ = id_format.format(self.pk)
        title_max_length = MAX_CHARS + len(ENDING)
        title_format = f"{{:{title_max_length}s}}"
        title = title_format.format(title)  # pylint: disable=consider-using-f-string
        return f"{id_} - {title}"[1:]


class Record(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="records")
    movie = models.ForeignKey(Movie, models.CASCADE, related_name="records")
    list = models.ForeignKey(List, models.CASCADE)
    rating = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, default="")
    date = models.DateTimeField(auto_now_add=True)
    watched_original = models.BooleanField(default=False)
    watched_extended = models.BooleanField(default=False)
    watched_in_theatre = models.BooleanField(default=False)
    watched_in_hd = models.BooleanField(default=False)
    watched_in_full_hd = models.BooleanField(default=False)
    watched_in_4k = models.BooleanField(default=False)

    def __str__(self):
        return self.movie.title

    def save(self, *args, **kwargs):
        if self.watched_in_4k:
            self.watched_in_full_hd = True
        if self.watched_in_full_hd:
            self.watched_in_hd = True
        super().save(*args, **kwargs)


class Action(models.Model):
    ADDED_MOVIE = 1
    CHANGED_LIST = 2
    ADDED_RATING = 3
    ADDED_COMMENT = 4
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class ActionRecord(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name="actions")
    action = models.ForeignKey(Action, models.CASCADE)
    movie = models.ForeignKey(Movie, models.CASCADE)
    list = models.ForeignKey(List, models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} {self.action.name}"
