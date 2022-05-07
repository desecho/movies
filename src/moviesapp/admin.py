from django.contrib import admin

from .models import Action, ActionRecord, List, Movie, Record, User


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin[Record]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "list", "date")


@admin.register(ActionRecord)
class ActionRecordAdmin(admin.ModelAdmin[ActionRecord]):  # pylint:disable=unsubscriptable-object
    list_display = ("user", "movie", "action", "list", "date")


admin.site.register(User)
admin.site.register(Movie)
admin.site.register(List)
admin.site.register(Action)
