from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.simple_tag
def movie_count(user):
    LIST_IDS = {'watched': 1, 'to_watch': 2}

    def create_span_tag(title, list_id):
        number_of_movies = user.get_records().filter(list_id=list_id).count()
        return f'<span title="{title}">{number_of_movies}</span>'

    watched = create_span_tag(_('Watched'), LIST_IDS['watched'])
    to_watch = create_span_tag(_('To Watch'), LIST_IDS['to_watch'])
    return mark_safe(f'<i class="fa fa-eye"></i> {watched} &nbsp;<i class="fa fa-eye-slash"></i> {to_watch}')  # nosec
