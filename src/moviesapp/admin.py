# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Action, ActionRecord, List, Movie, Record, User


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
