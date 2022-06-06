from django.contrib.admin import ModelAdmin, register, site

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
    list_display = ("provider", "movie")
    search_fields = ["movie__title"]


site.register(User)
site.register(List)
site.register(Action)
site.register(Provider)
