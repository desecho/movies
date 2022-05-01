from typing import Any

from django import template
from django.template.context import RequestContext
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def abs_url(context: RequestContext, view_name: str, *args: Any, **kwargs: Any) -> str:
    url: str = context["request"].build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))
    return url
