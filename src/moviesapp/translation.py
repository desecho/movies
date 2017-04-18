from __future__ import unicode_literals

from modeltranslation.translator import TranslationOptions, register

from .models import Movie, Action, List


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ('title', 'poster', 'description')


@register(Action)
class ActionTranslationOptions(TranslationOptions):
    fields = ('name', )

@register(List)
class ListTranslationOptions(TranslationOptions):
    fields = ('name', )
