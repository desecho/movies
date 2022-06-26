"""Admin."""
from typing import Optional

from django.conf import settings
from django.contrib.admin import ModelAdmin, register, site
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django_celery_results.models import GroupResult

from .models import Action, ActionRecord, List, Movie, Provider, ProviderRecord, Record, User, VkCountry


@register(Record)
class RecordAdmin(ModelAdmin[Record]):  # pylint:disable=unsubscriptable-object
    """Record admin."""

    list_display = ("user", "movie", "list", "date")
    search_fields = ("movie__title", "user__username", "user__first_name", "user__last_name")


@register(ActionRecord)
class ActionRecordAdmin(ModelAdmin[ActionRecord]):  # pylint:disable=unsubscriptable-object
    """Action record admin."""

    list_display = ("user", "movie", "action", "date")
    search_fields = ("movie__title", "user__username", "user__first_name", "user__last_name")


@register(Movie)
class MovieAdmin(ModelAdmin[Movie]):  # pylint:disable=unsubscriptable-object
    """Movie admin."""

    list_display = ("title",)
    search_fields = ("title",)


@register(ProviderRecord)
class ProviderRecordAdmin(ModelAdmin[ProviderRecord]):  # pylint:disable=unsubscriptable-object
    """Provider record admin."""

    list_display = ("provider", "movie", "country")
    search_fields = ("movie__title",)


@register(List)
class ListAdmin(ModelAdmin[List]):  # pylint:disable=unsubscriptable-object
    """List admin."""

    def has_delete_permission(  # pylint:disable=no-self-use,unused-argument
        self, request: HttpRequest, obj: Optional[List] = None
    ) -> bool:
        """Return True if the user has delete permission."""
        return False


@register(Action)
class ActionAdmin(ModelAdmin[Action]):  # pylint:disable=unsubscriptable-object
    """Action admin."""

    def has_delete_permission(  # pylint:disable=no-self-use,unused-argument
        self, request: HttpRequest, obj: Optional[Action] = None
    ) -> bool:
        """Return True if the user has delete permission."""
        return False


@register(Provider)
class ProviderAdmin(ModelAdmin[Provider]):  # pylint:disable=unsubscriptable-object
    """Provider admin."""

    list_display = ("name",)
    search_fields = ("name",)

    def has_delete_permission(  # pylint:disable=no-self-use,unused-argument
        self, request: HttpRequest, obj: Optional[Provider] = None
    ) -> bool:
        """Return True if the user has delete permission."""
        return False


@register(User)
class UserAdmin(ModelAdmin[User]):  # pylint:disable=unsubscriptable-object
    """User admin."""

    list_display = ("username", "first_name", "last_name", "country")
    search_fields = ("username", "first_name", "last_name", "country")


site.register(VkCountry)

site.unregister(Group)
if settings.IS_CELERY_DEBUG:  # pragma: no cover
    site.unregister(GroupResult)
