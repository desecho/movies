from __future__ import unicode_literals

from modeltranslation.translator import TranslationOptions, register

from .models import Movie


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ('title', 'poster', 'description')
