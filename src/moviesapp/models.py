"""Models."""

import json
from datetime import datetime, time, timedelta
from typing import Any, Optional
from urllib.parse import urljoin

from dateutil.relativedelta import relativedelta
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
    Manager,
    Model,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    QuerySet,
    TextField,
    TimeField,
    UniqueConstraint,
    URLField,
)
from django.http import HttpRequest
from django.utils import formats
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from timezone_field import TimeZoneField

from .exceptions import ProviderNotFoundError
from .tmdb import get_poster_url, get_tmdb_url
from .types import TmdbTrailer, Trailer, TrailerSite, WatchDataRecord
from .utils import is_movie_released


class UserBase:
    """User base class."""

    def get_movie_ids(self) -> list[int]:
        """Get movie IDs."""
        return list(self.get_records().values_list("movie__pk", flat=True))

    def get_records(self) -> QuerySet["Record"]:
        """Get records."""
        if self.is_authenticated:  # type: ignore
            records: QuerySet[Record] = self.records.all()  # type: ignore
            return records
        return Record.objects.none()

    def get_record(self, id_: int) -> "Record":
        """Get record."""
        return self.get_records().get(pk=id_)

    # def _get_fb_accounts(self) -> QuerySet[AbstractUserSocialAuth]:
    #     """Get FB accounts."""
    #     return self.social_auth.filter(provider="facebook")  # type: ignore

    # def is_fb_user(self) -> bool:
    #     """Return True if user has FB account."""
    #     if self.is_authenticated:  # type: ignore
    #         return self._get_fb_accounts().exists()
    #     return False

    # # It is requried that `is_fb_user` is run before running this.
    # def get_fb_account(self) -> AbstractUserSocialAuth:  # 2DO possibly remove it from this class.
    #     """Get FB account."""
    #     return self._get_fb_accounts()[0]

    # def _get_vk_accounts(self) -> QuerySet[AbstractUserSocialAuth]:
    #     """Get VK accounts."""
    #     return self.social_auth.filter(provider=settings.VK_BACKEND)  # type: ignore

    # # It is requried that `is_vk_user` is run before running this.
    # def get_vk_account(self) -> Optional[AbstractUserSocialAuth]:  # 2DO possibly remove it from this class.
    #     """Get VK account."""
    #     vk_accounts = self._get_vk_accounts()
    #     if len(vk_accounts) == 1:
    #         return vk_accounts[0]

    #     raise VkError

    # @property
    # def is_vk_user(self) -> bool:
    #     """Return True if a user has a VK account."""
    #     if self.is_authenticated:  # type: ignore
    #         return self._get_vk_accounts().exists()
    #     return False

    # @property
    # def is_linked(self) -> bool:
    #     """Return True if user is linked."""
    #     if self.is_authenticated:  # type: ignore
    #         return self.social_auth.exists()  # type: ignore
    #     return False

    # def get_vk(self) -> Optional[Vk]:
    #     """Get VK."""
    #     if self.is_vk_user:
    #         return Vk(self)  # type: ignore
    #     return None

    # def get_friends(self, sort: bool = False) -> QuerySet["User"]:
    #     """Get friends."""
    #     friends = User.objects.none()
    #     if self.is_linked:
    #         if self.is_vk_user:  # 2DO possibly refactor this (this check is run twice)
    #             vk = self.get_vk()
    #             if vk is not None:
    #                 friends |= vk.get_friends()
    #         if self.is_fb_user():
    #             friends |= Fb(self).get_friends()  # type: ignore
    #         if sort:
    #             friends = friends.order_by("first_name")
    #     return friends

    # def has_friends(self) -> bool:
    #     """Return True if user has friends."""
    #     if self.is_authenticated:  # type: ignore
    #         user: User = self  # type: ignore
    #         cache_id = f"has_friends_{user.pk}"
    #         has_friends: Optional[bool] = cache.get(cache_id)
    #         if has_friends is None:
    #             has_friends = user.get_friends().exists()
    #             cache.set(cache_id, has_friends)
    #         return has_friends
    #     return False


class User(AbstractUser, UserBase):
    """User class."""

    only_for_friends = BooleanField(
        verbose_name=_("Only for friends"), default=False, help_text=_("Show my lists only to friends")
    )
    hidden = BooleanField(verbose_name=_("Hide account"), default=False, help_text=_("Don't show my lists to anybody"))
    language = CharField(
        max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name=_("Language")
    )
    avatar_small = URLField(null=True, blank=True)
    avatar_big = URLField(null=True, blank=True)
    loaded_initial_data = BooleanField(default=False)
    country = CountryField(verbose_name=_("Country"), null=True, blank=True)
    timezone = TimeZoneField(default=settings.TIME_ZONE)

    def __str__(self) -> str:
        """Return string representation."""
        if self.username and not self.username.isnumeric():
            return self.username
        return self.get_full_name()

    def _get_movies_number(self, list_id: int) -> int:
        """Get movies number."""
        return self.get_records().filter(list_id=list_id).count()

    @property
    def movies_watched_number(self) -> int:
        """Get movies watched number."""
        return self._get_movies_number(List.WATCHED)

    @property
    def movies_to_watch_number(self) -> int:
        """Get movies to watch number."""
        return self._get_movies_number(List.TO_WATCH)

    @property
    def is_country_supported(self) -> bool:
        """Return True if country is supported."""
        return self.country in settings.PROVIDERS_SUPPORTED_COUNTRIES


class UserAnonymous(AnonymousUser, UserBase):
    """Anonymous user class."""

    # Not sure if it is needed.
    def __init__(self, request: HttpRequest):  # pylint: disable=unused-argument
        """Init."""
        super().__init__()


class List(Model):
    """List."""

    WATCHED = 1
    TO_WATCH = 2
    name = CharField(max_length=255, unique=True)
    key_name = CharField(max_length=255, db_index=True, unique=True)

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.name)

    @classmethod
    def is_valid_id(cls, list_id: int) -> bool:
        """Return True if list ID is valid."""
        return list_id in [cls.WATCHED, cls.TO_WATCH]


class Movie(Model):
    """Movie."""

    title = CharField(max_length=255)
    title_original = CharField(max_length=255)
    country = CharField(max_length=255, null=True, blank=True)
    overview = TextField(null=True, blank=True)
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
    watch_data_update_date = DateTimeField(null=True, blank=True)

    class Meta:
        """Meta."""

        ordering = ["pk"]

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.title)

    @property
    def release_date_formatted(self) -> Optional[str]:
        """Return release date formatted."""
        if self.release_date:
            return formats.date_format(self.release_date, "DATE_FORMAT")
        return None

    @property
    def release_date_timestamp(self) -> float:
        """Return release date timestamp."""
        if self.release_date:
            dt = datetime.combine(self.release_date, time())
            return dt.timestamp()
        next_year = now() + relativedelta(years=1)
        return next_year.timestamp()

    @property
    def imdb_rating_float(self) -> Optional[float]:
        """Get IMDb rating float."""
        if self.imdb_rating:
            return float(self.imdb_rating)
        return None

    @property
    def runtime_formatted(self) -> Optional[str]:
        """Return runtime formatted."""
        if self.runtime:
            return self.runtime.strftime("%H:%M")
        return None

    @property
    def imdb_url(self) -> str:
        """Return IMDb URL."""
        return urljoin(settings.IMDB_BASE_URL, self.imdb_id)

    @property
    def tmdb_url(self) -> str:
        """Return TMDB URL."""
        return get_tmdb_url(self.tmdb_id)

    @property
    def is_released(self) -> bool:
        """Return True if movie is released."""
        return is_movie_released(self.release_date)

    @property
    def is_watch_data_updated_recently(self) -> bool:
        """Return True if watch data was updated recently."""
        return self.watch_data_update_date is not None and self.watch_data_update_date >= now() - timedelta(
            days=settings.WATCH_DATA_UPDATE_MIN_DAYS
        )

    # Hack to make tests work
    @staticmethod
    def _get_real_trailers(trailers: list[TmdbTrailer]) -> list[TmdbTrailer]:
        """
        Get "real" trailers.

        This is a hack to make the tests work.
        """
        trailers_real = trailers
        if settings.IS_TEST:
            trailers_str: str = trailers  # type: ignore
            trailers_real = json.loads(trailers_str)
        return trailers_real

    def _pre_get_trailers(self) -> list[TmdbTrailer]:
        """Pre-get trailers."""
        if self.trailers:
            trailers = self._get_real_trailers(self.trailers)
            return trailers
        # Fallback to English trailers when localized trailers are not available.
        trailers = self._get_real_trailers(self.trailers)  # type: ignore
        return trailers

    @staticmethod
    def _get_trailer_url(site: TrailerSite, key: str) -> str:
        """Get trailer URL."""
        TRAILER_SITES = settings.TRAILER_SITES
        base_url = TRAILER_SITES[site]
        return f"{base_url}{key}"

    def get_trailers(self) -> list[Trailer]:
        """Get trailers."""
        trailers: list[Trailer] = []
        for t in self._pre_get_trailers():
            trailer: Trailer = {
                "url": self._get_trailer_url(t["site"], t["key"]),
                "name": t["name"],
            }
            trailers.append(trailer)
        return trailers

    def save_watch_data(self, watch_data: list[WatchDataRecord]) -> None:
        """Save watch data for a movie."""
        for provider_record in watch_data:
            provider_id = provider_record["provider_id"]
            try:
                provider = Provider.objects.get(pk=provider_id)
            except Provider.DoesNotExist as e:
                raise ProviderNotFoundError(f"Provider ID - {provider_id}") from e
            ProviderRecord.objects.create(provider=provider, movie=self, country=provider_record["country"])
        self.watch_data_update_date = now()
        self.save()

    @classmethod
    def filter(cls, movie_id: Optional[int], start_from_id: bool = False, **kwargs: Any) -> QuerySet["Movie"]:
        """Filter movies."""
        movies = cls.objects.filter(**kwargs)
        if movie_id is not None:
            if start_from_id:
                return movies.filter(pk__gte=movie_id)
            return movies.filter(pk=movie_id)
        return movies

    def _get_poster(self, size: str) -> Optional[str]:
        """Get poster."""
        return get_poster_url(size, self.poster)

    @property
    def poster_normal(self) -> Optional[str]:
        """Get normal poster."""
        return self._get_poster("normal")

    @property
    def poster_small(self) -> Optional[str]:
        """Get small poster."""
        return self._get_poster("small")

    @property
    def poster_big(self) -> Optional[str]:
        """Get big poster."""
        return self._get_poster("big")

    @property
    def has_poster(self) -> bool:
        """Return True if movie has poster."""
        return self.poster is not None

    @property
    def title_with_id(self) -> str:
        """Get title with ID."""
        return f"{self.pk} - {self}"

    @classmethod
    def last(cls) -> Optional["Movie"]:
        """Get last movie."""
        return cls.objects.last()

    def cli_string(self, last_movie_id: int) -> str:
        """
        Return string representation for CLI.

        We need last movie id because we want to know how big is the number (in characters) to be able to make
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


class RecordQuerySet(QuerySet["Record"]):
    """Record query set."""

    def update(self, **kwargs: Any) -> int:
        """Update records."""
        ids = self.values_list("pk", flat=True)
        rows = super().update(**kwargs)
        # This is not optimized - we are saving the object twice.
        # This is needed because we need to use the custom save method of the model.
        for id_ in ids:
            Record.objects.get(pk=id_).save()
        return rows


class Record(Model):
    """Record."""

    user = ForeignKey(User, CASCADE, related_name="records")
    movie = ForeignKey(Movie, CASCADE, related_name="records")
    list = ForeignKey(List, CASCADE)
    rating = PositiveSmallIntegerField(default=0)
    order = PositiveSmallIntegerField(default=0)
    comment = CharField(max_length=255, default="")
    date = DateTimeField(auto_now_add=True)
    watched_original = BooleanField(default=False)
    watched_extended = BooleanField(default=False)
    watched_in_theatre = BooleanField(default=False)
    watched_in_hd = BooleanField(default=False)
    watched_in_full_hd = BooleanField(default=False)
    watched_in_4k = BooleanField(default=False)
    objects: Manager["Record"] = RecordQuerySet.as_manager()

    class Meta:
        """Meta."""

        constraints = [
            # A user should only have one record per movie.
            UniqueConstraint(fields=("user", "movie"), name="unique_user_movie_record"),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.user} - {self.movie.title} - {self.list}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Save."""
        if self.watched_in_4k:
            self.watched_in_full_hd = True
        if self.watched_in_full_hd:
            self.watched_in_hd = True
        super().save(*args, **kwargs)


class Action(Model):
    """Action."""

    ADDED_MOVIE = 1
    CHANGED_LIST = 2
    ADDED_RATING = 3
    ADDED_COMMENT = 4
    name = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.name)


class ActionRecord(Model):
    """Action record."""

    user = ForeignKey(User, CASCADE, related_name="actions")
    action = ForeignKey(Action, CASCADE)
    movie = ForeignKey(Movie, CASCADE)
    list = ForeignKey(List, CASCADE, blank=True, null=True)
    comment = CharField(max_length=255, blank=True, null=True)
    rating = PositiveSmallIntegerField(blank=True, null=True)
    date = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.user} - {self.movie.title} - {self.action.name}"


class Provider(Model):
    """Provider."""

    id = PositiveSmallIntegerField(primary_key=True)
    name = CharField(max_length=255)

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.name)

    @property
    def logo(self) -> str:
        """Return logo."""
        return f"/img/providers/{self.id}.jpg"


class ProviderRecord(Model):
    """Provider record."""

    provider = ForeignKey(Provider, CASCADE)
    movie = ForeignKey(Movie, CASCADE, related_name="provider_records")
    country = CountryField(verbose_name=_("Country"))

    class Meta:
        """Meta."""

        constraints = [
            # We should not have duplicated records
            UniqueConstraint(fields=("provider", "movie", "country"), name="unique_provider_movie_country_record"),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.provider} - {self.movie}"

    @property
    def tmdb_watch_url(self) -> str:
        """Return TMDb watch URL."""
        return f"{self.movie.tmdb_url}watch?locale={self.country}"


class VkCountry(Model):
    """VK country."""

    id = PositiveSmallIntegerField(primary_key=True)
    country = CountryField(verbose_name=_("Country"), unique=True)

    def __str__(self) -> str:
        """Return string representation."""
        return str(self.country)

    class Meta:
        """Meta."""

        verbose_name = "VK country"
        verbose_name_plural = "VK countries"
