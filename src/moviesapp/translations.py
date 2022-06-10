"""
Hardcoded translations.

We need this because we programatically use these translations in JavaScript and it does not get detected.
"""

from django.utils.translation import gettext_lazy as _

_("Actor")
_("Director")
