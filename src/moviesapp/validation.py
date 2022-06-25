"""Validation."""
from django.conf import settings

from .exceptions import UnsupportedLanguageError


def validate_language(language: str) -> None:
    """Validate language."""
    for lang in settings.LANGUAGES:
        if lang[0] == language:
            return None
    raise UnsupportedLanguageError(language)
