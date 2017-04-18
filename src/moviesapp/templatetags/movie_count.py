from django import template
from django.utils.translation import ugettext_lazy as _

from ..models import Record

register = template.Library()


@register.simple_tag
def movie_count(user):
    LIST_IDS = {'watched': 1, 'to_watch': 2}

    def create_span_tag(title, list_id):
        number_of_movies = Record.objects.filter(list_id=list_id, user=user).count()
        return '<span title="{}">{}</span>'.format(title, number_of_movies)

    watched = create_span_tag(_('Watched'), LIST_IDS['watched'])
    to_watch = create_span_tag(_('To Watch'), LIST_IDS['to_watch'])
    return '%s / %s' % (watched, to_watch)
