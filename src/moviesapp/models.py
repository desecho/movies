import json
from datetime import date
from typing import Any, Dict, List as ListType, Optional
from urllib.parse import urljoin

import vk_api
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    JSONField,
    Model,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    QuerySet,
    TextField,
    TimeField,
    URLField,
)
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from social_django.models import AbstractUserSocialAuth
from vk_api.exceptions import ApiError

from .exceptions import VKError
from .fb import Fb
from .http import HttpRequest
from .vk import Vk


# Cannot be moved to utils because it would cause circular imports
def get_tmdb_url(tmdb_id: int) -> str:
    return f"{settings.TMDB_MOVIE_BASE_URL}{tmdb_id}/"


# Cannot be moved to utils because it would cause circular imports
def get_poster_url(size: str, poster: Optional[str]) -> Optional[str]:
    if size == "small":
        poster_size = settings.POSTER_SIZE_SMALL
        no_image_url = settings.NO_POSTER_SMALL_IMAGE_URL
    elif size == "normal":
        poster_size = settings.POSTER_SIZE_NORMAL
        no_image_url = settings.NO_POSTER_NORMAL_IMAGE_URL
    elif size == "big":
        poster_size = settings.POSTER_SIZE_BIG
        no_image_url = settings.NO_POSTER_BIG_IMAGE_URL
    if poster is not None:
        return settings.POSTER_BASE_URL + poster_size + "/" + poster
    return no_image_url


class UserBase:
    def get_movie_ids(self) -> ListType[int]:
        return list(self.get_records().values_list("movie__pk", flat=True))

    def get_records(self) -> QuerySet["Record"]:
        if self.is_authenticated:  # type: ignore
            records: QuerySet[Record] = self.records.all()  # type: ignore
            return records
        return Record.objects.none()

    def get_record(self, id_: int) -> "Record":
        return self.get_records().get(pk=id_)

    def _get_fb_accounts(self) -> QuerySet[AbstractUserSocialAuth]:
        return self.social_auth.filter(provider="facebook")  # type: ignore

    def is_fb_user(self) -> bool:
        if self.is_authenticated:  # type: ignore
            return self._get_fb_accounts().exists()
        return False

    # It is requried that `is_fb_user` is run before running this.
    def get_fb_account(self) -> AbstractUserSocialAuth:  # 2DO possibly remove it from this class.
        return self._get_fb_accounts()[0]

    def _get_vk_accounts(self) -> QuerySet[AbstractUserSocialAuth]:
        return self.social_auth.filter(provider__in=settings.VK_BACKENDS)  # type: ignore

    # It is requried that `is_vk_user` is run before running this.
    def get_vk_account(self) -> Optional[AbstractUserSocialAuth]:  # 2DO possibly remove it from this class.
        vk_accounts = self._get_vk_accounts()
        if len(vk_accounts) == 1:
            return vk_accounts[0]
        for vk_account in vk_accounts:
            vk_session = vk_api.VkApi(token=vk_account.access_token)
            if vk_session.token["access_token"] is None:
                extra_data = vk_account.extra_data
                extra_data["access_token"] = None
                vk_account.extra_data = extra_data
                vk_account.save()
            vk = vk_session.get_api()
            try:
                vk.users.get(fields=["screen_name"])
            except ApiError:
                continue
            return vk_account

        if vk_session.token["access_token"] is None:
            return None
        raise VKError

    @property
    def is_vk_user(self) -> bool:
        """
        Show if a user has a vk account.

        It doesn't necessarily mean that he is currently using the app.
        Note: currently it does because it is not possible to link a vk-app account and a website account.
        But it is likely to change in the future.
        """
        if self.is_authenticated:  # type: ignore
            return self._get_vk_accounts().exists()
        return False

    @property
    def is_linked(self) -> bool:
        if self.is_authenticated:  # type: ignore
            return self.social_auth.exists()  # type: ignore
        return False

    def get_users(self, friends: bool = False, sort: bool = False) -> ListType["User"]:
        if friends:
            return list(self.get_friends(sort=sort))
        return self._get_available_users_and_friends(sort=sort)

    def _get_available_users_and_friends(self, sort: bool = False) -> ListType["User"]:
        available_users = User.objects.exclude(only_for_friends=True).exclude(pk=self.pk)  # type: ignore
        # We need distinct here because we can't concatenate distinct and non-distinct querysets.
        users = available_users.distinct() | self.get_friends()
        if sort:
            users = users.order_by("first_name")
        return list(set(users))

    def get_vk(self) -> Optional[Vk]:
        if self.is_vk_user:
            return Vk(self)  # type: ignore
        return None

    def get_friends(self, sort: bool = False) -> QuerySet["User"]:
        friends = User.objects.none()
        if self.is_linked:
            if self.is_vk_user:  # 2DO possibly refactor this (this check is run twice)
                vk = self.get_vk()
                if vk is not None:
                    friends |= vk.get_friends()
            if self.is_fb_user():
                friends |= Fb(self).get_friends()  # type: ignore
            if sort:
                friends = friends.order_by("first_name")
        return friends

    def has_friends(self) -> bool:
        return self.get_friends().exists()


class User(AbstractUser, UserBase):
    only_for_friends = BooleanField(
        verbose_name=_("Privacy"), default=False, help_text=_("Show my lists only to friends")
    )
    language = CharField(
        max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("Language")
    )
    avatar_small = URLField(null=True, blank=True)
    avatar_big = URLField(null=True, blank=True)
    loaded_initial_data = BooleanField(default=False)
    country = CountryField(verbose_name=_("Country"), null=True, blank=True)

    def __str__(self) -> str:
        name = self.get_full_name()
        if name:
            return name
        return self.username

    def _get_movies_number(self, list_id: int) -> int:
        return self.get_records().filter(list_id=list_id).count()

    @property
    def movies_watched_number(self) -> int:
        return self._get_movies_number(List.WATCHED)

    @property
    def movies_to_watch_number(self) -> int:
        return self._get_movies_number(List.TO_WATCH)

    @property
    def country_supported(self) -> bool:
        return self.country in settings.PROVIDERS_SUPPORTED_COUNTRIES


class UserAnonymous(AnonymousUser, UserBase):
    def __init__(self, request: HttpRequest):  # pylint: disable=unused-argument
        super().__init__()


class List(Model):
    WATCHED = 1
    TO_WATCH = 2
    name = CharField(max_length=255)
    key_name = CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return str(self.name)

    @classmethod
    def is_valid_id(cls, list_id: int) -> bool:
        return list_id in [cls.WATCHED, cls.TO_WATCH]


class Movie(Model):
    title = CharField(max_length=255)
    title_original = CharField(max_length=255)
    country = CharField(max_length=255, null=True, blank=True)
    description = TextField(null=True, blank=True)
    director = CharField(max_length=255, null=True, blank=True)
    writer = CharField(max_length=255, null=True, blank=True)
    genre = CharField(max_length=255, null=True, blank=True)
    actors = CharField(max_length=255, null=True, blank=True)
    imdb_id = CharField(max_length=15, unique=True, db_index=True)
    tmdb_id = PositiveIntegerField(unique=True)
    imdb_rating = DecimalField(max_digits=2, decimal_places=1, null=True)
    poster = CharField(max_length=255, null=True)
    release_date = DateField(null=True)
    runtime = TimeField(null=True, blank=True)
    homepage = URLField(null=True, blank=True)
    trailers = JSONField(null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self) -> str:
        return str(self.title)

    @property
    def imdb_url(self) -> str:
        return urljoin(settings.IMDB_BASE_URL, self.imdb_id)

    @property
    def tmdb_url(self) -> str:
        return get_tmdb_url(self.tmdb_id)

    @property
    def is_released(self) -> bool:
        return self.release_date is not None and self.release_date <= date.today()

    # Hack to make tests work
    @staticmethod
    def _get_real_trailers(trailers: Any) -> ListType[Dict[str, str]]:
        trailers_real: ListType[Dict[str, str]] = trailers
        if settings.IS_TEST:
            trailers_real = json.loads(trailers)
        return trailers_real

    def _pre_get_trailers(self) -> ListType[Dict[str, str]]:
        if self.trailers:
            trailers = self._get_real_trailers(self.trailers)
            return trailers
        # Fallback to English trailers when localized trailers are not available.
        trailers = self._get_real_trailers(self.trailers_en)  # type: ignore
        return trailers

    @staticmethod
    def _get_trailer_url(site: str, key: str) -> str:
        TRAILER_SITES: Dict[str, str] = settings.TRAILER_SITES
        base_url = TRAILER_SITES[site]
        return f"{base_url}{key}"

    def get_trailers(self) -> ListType[Dict[str, str]]:
        trailers = []
        for t in self._pre_get_trailers():
            trailer = {
                "url": self._get_trailer_url(t["site"], t["key"]),
                "name": t["name"],
            }
            trailers.append(trailer)
        return trailers

    @property
    def has_trailers(self) -> bool:
        return bool(self.get_trailers())

    def _get_poster(self, size: str) -> Optional[str]:
        return get_poster_url(size, self.poster)

    @property
    def poster_normal(self) -> Optional[str]:
        return self._get_poster("normal")

    @property
    def poster_small(self) -> Optional[str]:
        return self._get_poster("small")

    @property
    def poster_big(self) -> Optional[str]:
        return self._get_poster("big")

    @property
    def id_title(self) -> str:
        return f"{self.pk} - {self}"

    def cli_string(self, last_movie_id: int) -> str:
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


class Record(Model):
    user = ForeignKey(User, CASCADE, related_name="records")
    movie = ForeignKey(Movie, CASCADE, related_name="records")
    list = ForeignKey(List, CASCADE)
    rating = PositiveSmallIntegerField(default=0)
    comment = CharField(max_length=255, default="")
    date = DateTimeField(auto_now_add=True)
    watched_original = BooleanField(default=False)
    watched_extended = BooleanField(default=False)
    watched_in_theatre = BooleanField(default=False)
    watched_in_hd = BooleanField(default=False)
    watched_in_full_hd = BooleanField(default=False)
    watched_in_4k = BooleanField(default=False)

    def __str__(self) -> str:
        return self.movie.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.watched_in_4k:
            self.watched_in_full_hd = True
        if self.watched_in_full_hd:
            self.watched_in_hd = True
        super().save(*args, **kwargs)

    @property
    def provider_records(self) -> QuerySet["ProviderRecord"]:
        if not self.user.country_supported:
            return ProviderRecord.objects.none()
        return self.movie.provider_records.filter(country=self.user.country)


class Action(Model):
    ADDED_MOVIE = 1
    CHANGED_LIST = 2
    ADDED_RATING = 3
    ADDED_COMMENT = 4
    name = CharField(max_length=255)

    def __str__(self) -> str:
        return str(self.name)


class ActionRecord(Model):
    user = ForeignKey(User, CASCADE, related_name="actions")
    action = ForeignKey(Action, CASCADE)
    movie = ForeignKey(Movie, CASCADE)
    list = ForeignKey(List, CASCADE, blank=True, null=True)
    comment = CharField(max_length=255, blank=True, null=True)
    rating = PositiveSmallIntegerField(blank=True, null=True)
    date = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.movie.title} {self.action.name}"


class Provider(Model):
    id = PositiveSmallIntegerField(primary_key=True)
    name = CharField(max_length=255)

    def __str__(self) -> str:
        return str(self.name)

    @property
    def logo(self) -> str:
        return f"{settings.STATIC_URL}/img/providers/{self.id}.jpg"


class ProviderRecord(Model):
    provider = ForeignKey(Provider, CASCADE)
    movie = ForeignKey(Movie, CASCADE, related_name="provider_records")
    country = CountryField(verbose_name=_("Country"))

    def __str__(self) -> str:
        return f"{self.provider} - {self.movie}"

    @property
    def tmdb_watch_url(self) -> str:
        return f"{self.movie.tmdb_url}/watch?locale={self.country}"
