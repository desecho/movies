"""Model translation."""

from modeltranslation.translator import TranslationOptions, register

from .models import Action, List, Movie


@register(Movie)
class MovieTranslationOptions(TranslationOptions):
    """Movie translation options."""

    fields = ("title", "poster", "overview", "trailers")


@register(Action)
class ActionTranslationOptions(TranslationOptions):
    """Action translation options."""

    fields = ("name",)


@register(List)
class ListTranslationOptions(TranslationOptions):
    """List translation options."""

    fields = ("name",)
