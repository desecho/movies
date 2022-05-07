from django.contrib.admin import ModelAdmin, register, site

from .models import Action, ActionRecord, List, Movie, Record, User


@register(Record)
class RecordAdmin(ModelAdmin[Record]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "list", "date")


@register(ActionRecord)
class ActionRecordAdmin(ModelAdmin[ActionRecord]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "action", "list", "date")


site.register(User)
site.register(Movie)
site.register(List)
site.register(Action)
