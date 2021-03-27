from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def movie_count(user):
    watched = _("Watched")
    to_watch = _("To Watch")
    watched_number = user.movies_watched_number
    to_watch_number = user.movies_to_watch_number
    return mark_safe(  # nosec
        f'<span title="{watched}" class="mr-2"><i class="fa fa-eye"></i> {watched_number}</span> '
        f'<span title="{to_watch}"><i class="fa fa-eye-slash"></i> {to_watch_number}</span>'
    )
