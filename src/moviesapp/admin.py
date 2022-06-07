from typing import Optional

from django.contrib.admin import ModelAdmin, register, site
from django.http import HttpRequest

from .models import Action, ActionRecord, List, Movie, Provider, ProviderRecord, Record, User


@register(Record)
class RecordAdmin(ModelAdmin[Record]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "list", "date")


@register(ActionRecord)
class ActionRecordAdmin(ModelAdmin[ActionRecord]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "action", "list", "date")


@register(Movie)
class MovieAdmin(ModelAdmin[Movie]):  # pylint:disable=unsubscriptable-object
    list_display = ("title",)
    search_fields = ["title"]


@register(ProviderRecord)
class ProviderRecordAdmin(ModelAdmin[ProviderRecord]):  # pylint:disable=unsubscriptable-object
    list_display = ("provider", "movie", "country")
    search_fields = ["movie__title"]


@register(List)
class ListAdmin(ModelAdmin[List]):  # pylint:disable=unsubscriptable-object
    def has_delete_permission(  # pylint:disable=no-self-use,unused-argument
        self, request: HttpRequest, obj: Optional[List] = None
    ) -> bool:
        return False


@register(Action)
class ActionAdmin(ModelAdmin[Action]):  # pylint:disable=unsubscriptable-object
    def has_delete_permission(  # pylint:disable=no-self-use,unused-argument
        self, request: HttpRequest, obj: Optional[Action] = None
    ) -> bool:
        return False


site.register(User)
site.register(Provider)
