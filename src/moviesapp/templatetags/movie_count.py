"""Template tag for movie count."""

from django import template
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _

from ..models import User

register = template.Library()


def _get_icon(name: str) -> str:
    return f'<span><font-awesome-icon icon="fa-solid {name}" /></span>'


@register.simple_tag
def movie_count(user: User) -> SafeString:
    """Get movie count HTML snippet."""
    watched = _("Watched")
    to_watch = _("To Watch")
    watched_number = user.movies_watched_number
    to_watch_number = user.movies_to_watch_number
    icon_eye = _get_icon("fa-eye")
    icon_eye_slash = _get_icon("fa-eye-slash")
    return mark_safe(  # nosec
        f'<div class="movie-count"><span title="{watched}" class="mr-2">{icon_eye} {watched_number}</span> '
        f'<span title="{to_watch}">{icon_eye_slash} {to_watch_number}</span></div>'
    )
