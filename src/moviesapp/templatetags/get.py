"""Template tag "get"."""

from typing import Any

from django import template

from ..types import UntypedObject

register = template.Library()


@register.filter
def get(dictionary: UntypedObject, key: str) -> Any:
    """Get value from dictionary."""
    return dictionary.get(key, "")
