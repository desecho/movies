from movies.models import Movie, Record, List, Action, ActionRecord
from django.contrib import admin


class RecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'date']


class ActionRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'action', 'date']


admin.site.register(Movie)
admin.site.register(Record, RecordAdmin)
admin.site.register(List)
admin.site.register(Action)
admin.site.register(ActionRecord, ActionRecordAdmin)
