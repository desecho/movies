from typing import Any, Dict

from django import template

register = template.Library()


@register.filter
def get(dictionary: Dict[str, Any], key: str) -> Any:
    return dictionary.get(key, "")
