from django.contrib import admin

from .models import Movie, Record, List, Action, ActionRecord, User


class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'list', 'date')


class ActionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'action', 'list', 'date')


admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Record, RecordAdmin)
admin.site.register(List)
admin.site.register(Action)
admin.site.register(ActionRecord, ActionRecordAdmin)
