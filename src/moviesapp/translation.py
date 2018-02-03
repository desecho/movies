# -*- coding: utf-8 -*-

from modeltranslation.translator import TranslationOptions, register

from .models import Action, List, Movie


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ('title', 'poster', 'description', 'trailers')


@register(Action)
class ActionTranslationOptions(TranslationOptions):
    fields = ('name', )


@register(List)
class ListTranslationOptions(TranslationOptions):
    fields = ('name', )
