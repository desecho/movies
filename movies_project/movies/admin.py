from movies.models import Movie, Record, List
from django.contrib import admin


class RecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'date']

admin.site.register(Movie)
admin.site.register(Record, RecordAdmin)
admin.site.register(List)
