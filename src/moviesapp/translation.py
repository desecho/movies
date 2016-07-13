from __future__ import unicode_literals

from modeltranslation.translator import register, TranslationOptions

from .models import Movie


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    fields = ('title', 'poster', 'description')
