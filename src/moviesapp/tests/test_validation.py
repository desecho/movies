import pytest

from moviesapp.exceptions import UnsupportedLanguageError
from moviesapp.validation import validate_language


def test_validate_language():
    validate_language("en")


def test_validate_language_fails():
    with pytest.raises(UnsupportedLanguageError) as excinfo:
        validate_language("ro")

    assert excinfo.match("ro")
